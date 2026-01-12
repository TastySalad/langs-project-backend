import json
from utils.logger import get_logger
from openai import OpenAI
import os

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_npc_reply(self, transcript: str, npc_data: dict = None, context: dict = None, conversation_history: list = None) -> str:
        """
        Generate a short NPC reply using OpenAI GPT.
        
        Args:
            transcript: transcribed user speech
            npc_data: NPC personality info (name, personality, mood, etc.)
            context: game context (positions, etc.)
            conversation_history: list of {role: 'user'|'npc', content: '...'}
        
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
            
            # Build messages with conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history and isinstance(conversation_history, list):
                for entry in conversation_history:
                    role = entry.get('role', '')
                    content = entry.get('content', '')
                    if role == 'user':
                        messages.append({"role": "user", "content": f"Player says: {content}"})
                    elif role == 'npc':
                        messages.append({"role": "assistant", "content": content})
            
            # Add current user message
            user_msg = f"Player says: {transcript}"
            messages.append({"role": "user", "content": user_msg})
            
            logger.info(f"LLM: Generating reply for '{transcript}' (history: {len(conversation_history or [])} messages)")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=30,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content.strip()
            logger.info(f"LLM: Reply generated: '{reply}'")
            return reply
        except Exception as e:
            logger.error(f"LLM: Generation failed: {e}")
            return "I'm not sure what you mean."