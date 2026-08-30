from logassistant.core import Logger
from logassistant.schemas import GlobalSecurityPolicy, NetworkLogEntry


class PolicyEngine:
    def __init__(self, policy: GlobalSecurityPolicy):
        self.ip_risk_scores = {}
        self.volumetric_counters = {}
        self.policy = policy
        self.treshold = 100

    def evaluate_line(self, entry: NetworkLogEntry) -> tuple[str, str, int] | None:
        if entry.source_ip not in self.ip_risk_scores:
            self.ip_risk_scores[entry.source_ip] = 0
        if entry.source_ip not in self.volumetric_counters:
            self.volumetric_counters[entry.source_ip] = {}

        for rule in self.policy.rules:
            value_to_check = (
                entry.url if rule.target_field == "url" else entry.user_agent
            )
            # DO AI: "search" is not a known attribute of "None"PylancereportOptionalMemberAccess
            if rule.compiled_regex.search(value_to_check):
                if rule.type == "signature":
                    added_score = (
                        rule.on_success_score
                        if entry.status == 200
                        else rule.on_reject_score
                    )
                    self.ip_risk_scores[entry.source_ip] += added_score
                    reason = f"Signature match: '{rule.name}' (+{added_score} pts)"
                    Logger.info(
                        "Signature matched",
                        ip=entry.source_ip,
                        rule=rule.name,
                        score_added=added_score,
                        current_total=self.ip_risk_scores[entry.source_ip],
                    )

                elif rule.type == "volumetric":
                    self.volumetric_counters[entry.source_ip][rule.name] = (
                        self.volumetric_counters[entry.source_ip].get(rule.name, 0) + 1
                    )
                    if (
                        self.volumetric_counters[entry.source_ip][rule.name]
                        >= rule.volumetric_threshold
                    ):
                        added_score = (
                            rule.on_success_score
                            if entry.status == 200
                            else rule.on_reject_score
                        )
                        self.ip_risk_scores[entry.source_ip] += added_score
                        reason = f"Volumetric treshold passed: '{rule.name}' (+{added_score} pts)"
                        Logger.info(
                            "Volumetric threshold passed",
                            ip=entry.source_ip,
                            rule=rule.name,
                            count=self.volumetric_counters[entry.source_ip][rule.name],
                            current_total=self.ip_risk_scores[entry.source_ip],
                        )

                if self.ip_risk_scores[entry.source_ip] >= self.treshold:
                    final_reason = reason
                    final_score = self.ip_risk_scores[entry.source_ip]

                    self.ip_risk_scores[entry.source_ip] = 0
                    self.volumetric_counters[entry.source_ip] = {}
                    return rule.name, final_reason, final_score
        return None
