import json
from utils.logger import get_logger
from openai import OpenAI
import os

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_npc_reply(self, transcript: str, npc_data: dict = None, context: dict = None) -> str:
        """
        Generate a short NPC reply using OpenAI GPT.
        
        Args:
            transcript: transcribed user speech
            npc_data: NPC personality info (name, personality, mood, etc.)
            context: game context (positions, etc.)
        
        Returns:
            one-sentence NPC reply or fallback on error
        """
        if not transcript or transcript.strip() == "":
            return "I didn't catch that. Can you try again?"
        
        try:
            npc_name = npc_data.get('name', 'NPC') if npc_data else 'NPC'
            personality = npc_data.get('personality', '') if npc_data else ''
            mood = npc_data.get('mood', 'neutral') if npc_data else 'neutral'
            
            system_prompt = f"""You are a game NPC named {npc_name}. 
Personality: {personality}
Current mood: {mood}

Respond to the player's speech with ONE SHORT sentence (max 15 words). Stay in character. Be natural and conversational."""
            
            user_msg = f"Player says: {transcript}"
            
            logger.info(f"LLM: Generating reply for '{transcript}'")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=30,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content.strip()
            logger.info(f"LLM: Reply generated: '{reply}'")
            return reply
        except Exception as e:
            logger.error(f"LLM: Generation failed: {e}")
            return "I'm not sure what you mean."