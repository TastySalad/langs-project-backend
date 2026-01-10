from utils.logger import get_logger

logger = get_logger(__name__)

class STTService:
    def transcribe(self, audio_data: bytes) -> str:
        # Stub: return dummy transcript
        logger.info("STT: Transcribing audio (stub)")
        return "Hello, NPC!"