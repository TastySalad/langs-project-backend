from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from services.stt import STTService
from services.llm import LLMService
from services.tts import TTSService
from schemas.npc_command import NPCCommandRequest, NPCCommandResponse
from utils.tracing import generate_trace_id
from utils.logger import get_logger
import os
import json

logger = get_logger(__name__)

npc_bp = Blueprint('npc', __name__)

stt_service = STTService()
llm_service = LLMService()
tts_service = TTSService()

@npc_bp.route('/command', methods=['POST'])
def npc_command():
    trace_id = generate_trace_id()
    logger.info(f"Request {trace_id}: NPC command received")

    # Handle multipart/form-data or JSON
    if request.content_type.startswith('multipart/form-data'):
        npc_data = request.form.get('npc')
        context_data = request.form.get('context')
        transcript = request.form.get('transcript')
        audio_file = request.files.get('audio')
    else:
        data = request.get_json()
        npc_data = data.get('npc')
        context_data = data.get('context')
        transcript = data.get('transcript')
        audio_file = None

    # Validate required npc
    if not npc_data:
        raise BadRequest("Missing 'npc' field")

    try:
        npc = json.loads(npc_data) if isinstance(npc_data, str) else npc_data
        context = json.loads(context_data) if context_data and isinstance(context_data, str) else (context_data or {})
    except json.JSONDecodeError:
        raise BadRequest("Invalid JSON in npc or context")

    # Get transcript
    if transcript:
        pass  # use as is
    elif audio_file:
        audio_data = audio_file.read()
        transcript = stt_service.transcribe(audio_data)
    else:
        raise BadRequest("Missing 'transcript' or 'audio'")

    # LLM interpretation
    llm_result = llm_service.interpret_command(transcript, npc, context)

    # TTS
    tts_result = tts_service.generate_audio(llm_result['npcReplyText'])

    # Build response
    response = {
        "npcReplyText": llm_result['npcReplyText'],
        "actions": llm_result['actions'],
        "tts": tts_result,
        "traceId": trace_id
    }

    if os.getenv('DEBUG') == 'true':
        response['transcript_used'] = transcript
        response['raw_llm_output'] = json.dumps(llm_result)

    logger.info(f"Request {trace_id}: Response sent")
    return jsonify(response)