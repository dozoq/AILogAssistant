from fastapi import UploadFile

from logassistant.core import Logger
from logassistant.domain.policy_engine import PolicyEngine
from logassistant.domain.security_agent import SecurityAgentService
from logassistant.schemas import NetworkLogEntry
from logassistant.services import EventDispatcher, FileHandler


class LogService:
    def __init__(self, policy_engine: PolicyEngine):
        self.agent = SecurityAgentService()
        self.policy_engine = policy_engine

    async def run_analysis(self, file: UploadFile) -> None:
        buffer = ""
        line_number = 0

        async for chunk_bytes in FileHandler.read_file_in_chunks(file):
            buffer += chunk_bytes.decode("utf-8", errors="ignore")
            lines = buffer.splitlines()
            if not chunk_bytes.endswith(b"\n") and lines:
                buffer = lines.pop()
            else:
                buffer = ""

            for line in lines:
                line_number += 1
                try:
                    log_entry = NetworkLogEntry.from_raw_line(line)
                except ValueError:
                    Logger.warn("Skipping malformed log line", line_no=line_number)
                    continue

                hit = self.policy_engine.evaluate_line(log_entry)

                if hit:
                    rule_name, reason, score = hit
                    Logger.warn(
                        "AI analysis triggered",
                        ip=log_entry.source_ip,
                        reason=reason,
                        score=score,
                    )
                    parts = line.strip().split(" ")
                    attacker_ip = parts[0] if len(parts) > 0 else "unknown"
                    await self.run_ai_analysis(
                        rule_name,
                        attacker_ip,
                        details=f"Score:{score}, Reason: {reason}, Log:{line}",
                    )
            if buffer:
                pass
        Logger.info("Batch log file analysis finished", total_lines=line_number)

    async def run_ai_analysis(
        self, attack_type: str, attacker_ip: str, details: str
    ) -> None:
        ai_analysis = await self.agent.analyze_log_entry(
            attack_type, attacker_ip, details
        )
        await EventDispatcher.dispatch(attack_type, attacker_ip, details, ai_analysis)
