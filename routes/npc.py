from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from services.stt import STTService
from services.llm import LLMService
from services.tts import TTSService
from utils.tracing import generate_trace_id
from utils.logger import get_logger
import os
import json
import base64

logger = get_logger(__name__)

npc_bp = Blueprint('npc', __name__)

stt_service = STTService()
llm_service = LLMService()
tts_service = TTSService()

MAX_AUDIO_SIZE = 5 * 1024 * 1024  # 5MB

@npc_bp.route('/command', methods=['POST'])
def npc_command():
    trace_id = generate_trace_id()
    logger.info(f"[{trace_id}] NPC command received")

    # Check payload size
    if request.content_length and request.content_length > MAX_AUDIO_SIZE:
        logger.warning(f"[{trace_id}] Payload too large: {request.content_length} bytes")
        raise RequestEntityTooLarge(f"Audio file exceeds {MAX_AUDIO_SIZE} bytes")

    # Parse multipart/form-data
    npc_data = request.form.get('npc')
    context_data = request.form.get('context')
    conversation_history_data = request.form.get('conversationHistory')
    audio_file = request.files.get('audio')

    # Parse NPC and context JSON
    try:
        npc = json.loads(npc_data) if npc_data and isinstance(npc_data, str) else (npc_data or {})
        context = json.loads(context_data) if context_data and isinstance(context_data, str) else (context_data or {})
        conversation_history = json.loads(conversation_history_data) if conversation_history_data and isinstance(conversation_history_data, str) else []
    except json.JSONDecodeError:
        logger.error(f"[{trace_id}] Invalid JSON in npc or context")
        raise BadRequest("Invalid JSON in npc or context")

    # Get transcript from audio
    transcript = ""
    if audio_file:
        audio_data = audio_file.read()
        if len(audio_data) > MAX_AUDIO_SIZE:
            logger.warning(f"[{trace_id}] Audio data too large: {len(audio_data)} bytes")
            raise RequestEntityTooLarge(f"Audio file exceeds {MAX_AUDIO_SIZE} bytes")
        
        # Transcribe
        filename = audio_file.filename or 'recording.webm'
        mimetype = audio_file.content_type or 'audio/webm'
        transcript = stt_service.transcribe(audio_data, filename, mimetype)
        logger.info(f"[{trace_id}] Transcript: '{transcript}'")
    else:
        logger.warning(f"[{trace_id}] No audio file provided")

    # Generate NPC reply
    npc_reply_text = llm_service.generate_npc_reply(transcript, npc, context, conversation_history)
    logger.info(f"[{trace_id}] NPC reply: '{npc_reply_text}'")

    # Generate TTS if reply exists
    tts_data = None
    if npc_reply_text and npc_reply_text.strip():
        audio_bytes = tts_service.synthesize(npc_reply_text)
        if audio_bytes:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            tts_data = {
                "format": "mp3",
                "audioBase64": audio_base64
            }
            logger.info(f"[{trace_id}] TTS generated: {len(audio_bytes)} bytes")
        else:
            logger.warning(f"[{trace_id}] TTS synthesis failed, returning text only")

    # Build response
    response = {
        "traceId": trace_id,
        "transcript": transcript,
        "npcReplyText": npc_reply_text,
        "tts": tts_data
    }

    logger.info(f"[{trace_id}] Response sent")
    return jsonify(response)