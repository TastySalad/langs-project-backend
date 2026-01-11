from utils.logger import get_logger
from openai import OpenAI
import os
import base64

logger = get_logger(__name__)

class TTSService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def synthesize(self, text: str) -> bytes:
        """
        Generate speech audio using OpenAI TTS.
        
        Args:
            text: text to synthesize
        
        Returns:
            mp3 bytes, or empty bytes on failure
        """
        if not text or text.strip() == "":
            logger.warning("TTS: Empty text, returning empty bytes")
            return b""
        
        try:
            logger.info(f"TTS: Synthesizing '{text[:50]}...'")
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            audio_bytes = response.content
            logger.info(f"TTS: Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
        except Exception as e:
            logger.error(f"TTS: Synthesis failed: {e}")
            return b""