from utils.logger import get_logger
from openai import OpenAI
import os

logger = get_logger(__name__)

class STTService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def transcribe(self, audio_data: bytes, filename: str = 'recording.webm', mimetype: str = 'audio/webm') -> str:
        """
        Transcribe audio using OpenAI Whisper API.
        
        Args:
            audio_data: raw audio bytes
            filename: filename (used for extension detection)
            mimetype: MIME type of audio
        
        Returns:
            transcript string, or empty string on failure
        """
        try:
            logger.info(f"STT: Transcribing audio ({len(audio_data)} bytes, {filename})")
            
            # Send to OpenAI Whisper
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, audio_data, mimetype),
                language="en"
            )
            
            text = transcript.text.strip()
            logger.info(f"STT: Transcript: '{text}'")
            return text
        except Exception as e:
            logger.error(f"STT: Transcription failed: {e}")
            return ""