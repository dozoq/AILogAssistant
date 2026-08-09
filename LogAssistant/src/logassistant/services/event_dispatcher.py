import json

from logassistant.services.connection_manager import connection_manager

class EventDispatcher:
    async def dispatch(self, attack_type: str, ip: str, details: str, ai_report: dict) -> None:
        event_data = {
            "attack_type": attack_type,
            "ip": ip,
            "details": details,
            "ai_report": ai_report
        }
        await connection_manager.broadcast(json.dumps(event_data))

event_dispatcher = EventDispatcher()