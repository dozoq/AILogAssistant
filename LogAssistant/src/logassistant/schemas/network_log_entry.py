import re

from pydantic import BaseModel, Field


class NetworkLogEntry(BaseModel):
    source_ip: str = Field(..., description="Source IP")
    timestamp: str = Field(..., description="Timestamp of network activity")
    method: str = Field(..., description="HTTP Method")
    url: str = Field(..., description="URL Path")
    status: int = Field(..., description="HTTP Status code")
    size: int = Field(..., description="Response size in bytes")
    user_agent: str = Field(..., description="browser agent used by actor")

    @classmethod
    def from_raw_line(cls, line: str) -> "NetworkLogEntry":
        clean_line = line.strip()

        if " " not in clean_line:
            raise ValueError("Malformed line: Missing spaces")
        source_ip, rest = clean_line.split(" ", 1)

        if "[" not in rest or "]" not in rest:
            raise ValueError("Malformed line: Missing timestamp brackets")
        _, rest = rest.split("[", 1)
        timestamp, rest = rest.split("]", 1)

        if '"' not in rest:
            raise ValueError("Malformed line: Missing request quotes")
        _, rest = rest.split('"', 1)
        request_str, rest = rest.split('"', 1)

        request_parts = [p for p in request_str.split(" ") if p]
        if len(request_parts) < 2:
            raise ValueError("Malformed line: Invalid HTTP request format")
        method = request_parts[0]
        url = request_parts[1]

        rest = rest.strip()
        status_size_parts = rest.split(" ", 2)
        if len(status_size_parts) < 2:
            raise ValueError("Malformed line: Missing status or size")

        status = (
            int(status_str) if (status_str := status_size_parts[0]).isdigit() else 200
        )
        size = int(size_str) if (size_str := status_size_parts[1]).isdigit() else 0

        user_agent = "Unknown"
        if '"' in rest:
            _, ua_part = rest.split('"', 1)
            if '"' in ua_part:
                user_agent, _ = ua_part.split('"', 1)

        return cls(
            source_ip=source_ip,
            timestamp=timestamp,
            method=method,
            url=url,
            status=status,
            size=size,
            user_agent=user_agent,
        )
