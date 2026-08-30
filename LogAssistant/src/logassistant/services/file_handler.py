import json
import re

import aiofiles
from fastapi import UploadFile

from logassistant.core import BASE_DIR
from logassistant.schemas.global_security_policy import GlobalSecurityPolicy


class FileHandler:
    def __init__(self, chunk_size: int = 64 * 1024):
        self.chunk_size = chunk_size
        self.policies_path = BASE_DIR / "data" / "recognition" / "policies.json"
        self.knowledge_base_path = (
            BASE_DIR / "data" / "mitre_attack" / "mitre_sample.txt"
        )

    async def read_file_in_chunks(self, file: UploadFile):
        try:
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            print(f"Error reading file {file.filename}: {e}")
            raise

    async def load_policies(self) -> dict:
        if not self.policies_path.exists():
            raise FileNotFoundError(
                f"policy file does not exist at {self.policies_path}"
            )
        async with aiofiles.open(self.policies_path, "r", encoding="utf-8") as f:
            content = await f.read()
            dump = json.loads(content)
            policy_object = GlobalSecurityPolicy.model_validate_json(content)
            for rule in policy_object.rules:
                rule.compiled_regex = re.compile(rule.pattern, re.IGNORECASE)
            return policy_object

    async def load_knowledge_base_blocks(self, separator: str = "---") -> list[str]:
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                f"knowledge file not found at {self.knowledge_base_path}"
            )
        async with aiofiles.open(self.knowledge_base_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return [
                block.strip() for block in content.split(separator) if block.strip()
            ]


file_handler = FileHandler()
