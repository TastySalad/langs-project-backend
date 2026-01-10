import json
from utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    def interpret_command(self, transcript: str, npc: dict, context: dict) -> dict:
        # Stub: return dummy response
        logger.info("LLM: Interpreting command (stub)")
        return {
            "npcReplyText": "Understood.",
            "actions": [{"type": "SAY", "text": "Hello back!"}]
        }