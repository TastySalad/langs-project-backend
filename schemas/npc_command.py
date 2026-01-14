from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class NPC(BaseModel):
    name: str
    personality: str
    mood: str
    obedience: float

class Context(BaseModel):
    playerPosition: Dict[str, float]
    npcPosition: Dict[str, float]
    hearingRange: float

class NPCCommandRequest(BaseModel):
    npc: NPC
    context: Optional[Context] = None
    transcript: Optional[str] = None
    # audio will be handled separately in multipart

class Action(BaseModel):
    type: str
    # MOVE action fields
    direction: Optional[str] = None
    steps: Optional[int] = None
    stepSize: Optional[int] = 16  # Default step size
    speed: Optional[int] = 80      # Default speed (pixels/sec)
    confidence: Optional[float] = None
    text: Optional[str] = None

class TTS(BaseModel):
    format: str
    audioBase64: str

class NPCCommandResponse(BaseModel):
    say: str                    # What the NPC says
    actions: List[Action] = []  # Actions to execute
    npcReplyText: str           # Deprecated, kept for compatibility
    tts: Optional[TTS] = None
    traceId: str
    # debug fields
    transcript_used: Optional[str] = None
    raw_llm_output: Optional[str] = None