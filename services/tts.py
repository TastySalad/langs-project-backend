from utils.logger import get_logger

logger = get_logger(__name__)

class TTSService:
    def generate_audio(self, text: str) -> dict:
        # Stub: return dummy TTS
        logger.info("TTS: Generating audio (stub)")
        return {
            "format": "mp3",
            "audioBase64": "dummy_base64_audio"
        }