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
    direction: Optional[str] = None
    steps: Optional[int] = None
    confidence: Optional[float] = None
    text: Optional[str] = None

class TTS(BaseModel):
    format: str
    audioBase64: str

class NPCCommandResponse(BaseModel):
    npcReplyText: str
    actions: List[Action]
    tts: Optional[TTS] = None
    traceId: str
    # debug fields
    transcript_used: Optional[str] = None
    raw_llm_output: Optional[str] = None