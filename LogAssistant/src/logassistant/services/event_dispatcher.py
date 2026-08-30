import json

from logassistant.services.connection_manager import connection_manager


class EventDispatcher:
    async def dispatch(
        self, attack_type: str, ip: str, details: str, ai_report: dict
    ) -> None:
        if attack_type == "":
            raise ValueError("attack_type cannot be empty")
        if ip == "":
            raise ValueError("ip cannot be empty")
        if details == "":
            raise ValueError("details cannot be empty")
        if not ai_report:
            raise ValueError("ai_report cannot be empty")
        event_data = {
            "attack_type": attack_type,
            "ip": ip,
            "details": details,
            "ai_report": ai_report,
        }
        await connection_manager.broadcast(json.dumps(event_data))


event_dispatcher = EventDispatcher()
