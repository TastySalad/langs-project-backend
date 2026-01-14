import json
import re
from utils.logger import get_logger
from openai import OpenAI
import os

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_npc_reply(self, transcript: str, npc_data: dict = None, context: dict = None, conversation_history: list = None) -> dict:
        """
        Generate a short NPC reply using OpenAI GPT, with action parsing.
        
        Args:
            transcript: transcribed user speech
            npc_data: NPC personality info (name, personality, mood, etc.)
            context: game context (positions, etc.)
            conversation_history: list of {role: 'user'|'npc', content: '...'}
        
        Returns:
            dict with 'say' (text response) and 'actions' (list of action dicts)
        """
        if not transcript or transcript.strip() == "":
            return {"say": "I didn't catch that. Can you try again?", "actions": []}
        
        try:
            npc_name = npc_data.get('name', 'NPC') if npc_data else 'NPC'
            personality = npc_data.get('personality', '') if npc_data else ''
            mood = npc_data.get('mood', 'neutral') if npc_data else 'neutral'
            
            system_prompt = f"""You are a game NPC named {npc_name}. 
Personality: {personality}
Current mood: {mood}

You can perform actions in the game world. When the player asks you to move, respond naturally and include movement instructions.

Format your response as:
[SAY] <what you say to the player>
[ACTIONS] <action commands, one per line>

Supported actions:
- MOVE <direction> <steps>  (direction: UP/DOWN/LEFT/RIGHT, steps: 1-10)

Example:
[SAY] Sure, I'll move over there.
[ACTIONS]
MOVE RIGHT 4

If no action is needed, only include [SAY]. Keep responses SHORT (max 15 words in SAY)."""
            
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
                max_tokens=100,
                temperature=0.7
            )
            
            raw_reply = response.choices[0].message.content.strip()
            logger.info(f"LLM: Raw reply: '{raw_reply}'")
            
            # Parse the response
            parsed = self._parse_npc_response(raw_reply)
            logger.info(f"LLM: Parsed - say: '{parsed['say']}', actions: {len(parsed['actions'])}")
            
            return parsed
        except Exception as e:
            logger.error(f"LLM: Generation failed: {e}")
            return {"say": "I'm not sure what you mean.", "actions": []}
    
    def _parse_npc_response(self, raw_reply: str) -> dict:
        """Parse [SAY] and [ACTIONS] sections from LLM response."""
        say = ""
        actions = []
        
        # Extract [SAY] section
        say_match = re.search(r'\[SAY\]\s*(.+?)(?=\[ACTIONS\]|$)', raw_reply, re.DOTALL | re.IGNORECASE)
        if say_match:
            say = say_match.group(1).strip()
        else:
            # Fallback: use entire response if no [SAY] tag
            say = raw_reply.strip()
        
        # Extract [ACTIONS] section
        actions_match = re.search(r'\[ACTIONS\]\s*(.+)', raw_reply, re.DOTALL | re.IGNORECASE)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            actions = self._parse_actions(actions_text)
        
        return {"say": say, "actions": actions}
    
    def _parse_actions(self, actions_text: str) -> list:
        """Parse action commands and validate/normalize them."""
        actions = []
        
        for line in actions_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Parse MOVE command: MOVE <direction> <steps>
            move_match = re.match(r'MOVE\s+(UP|DOWN|LEFT|RIGHT)\s+(\d+)', line, re.IGNORECASE)
            if move_match:
                direction = move_match.group(1).upper()
                steps = int(move_match.group(2))
                
                # Validate and clamp
                action = self._validate_move_action(direction, steps)
                if action:
                    actions.append(action)
        
        return actions
    
    def _validate_move_action(self, direction: str, steps: int) -> dict:
        """Validate and normalize MOVE action with clamping."""
        # Validate direction
        valid_directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        if direction not in valid_directions:
            logger.warning(f"Invalid direction: {direction}")
            return None
        
        # Clamp steps (1-10)
        steps = max(1, min(steps, 10))
        
        # Provide defaults and clamp numeric values
        step_size = 16  # Fixed step size
        speed = 80      # Fixed speed (pixels/sec)
        
        return {
            "type": "MOVE",
            "direction": direction,
            "steps": steps,
            "stepSize": step_size,
            "speed": speed
        }