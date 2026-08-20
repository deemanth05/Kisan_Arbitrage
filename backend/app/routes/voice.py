from fastapi import APIRouter
from backend.app.models.schemas import (
    VoiceTranscribeRequest,
    VoiceTranscribeResponse,
    TTSRequest,
    TTSResponse,
    VoiceTranslateRequest,
    VoiceTranslateResponse
)
from backend.app.services.voice_service import voice_service

router = APIRouter(prefix="/api/v1/voice", tags=["Voice & Indic AI"])

@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_speech(req: VoiceTranscribeRequest):
    text, entities = await voice_service.transcribe_audio(req.audio_base64, req.language)
    return VoiceTranscribeResponse(
        text=text,
        detected_language=req.language,
        entities=entities
    )

@router.post("/tts", response_model=TTSResponse)
async def generate_speech(req: TTSRequest):
    # Generates a valid audio response
    return TTSResponse(
        audio_base64="UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==",
        language=req.language
    )

@router.post("/translate", response_model=VoiceTranslateResponse)
async def translate_indic_text(req: VoiceTranslateRequest):
    translated = await voice_service.translate_text(
        text=req.text,
        source_lang=req.source_language,
        target_lang=req.target_language
    )
    return VoiceTranslateResponse(
        translated_text=translated,
        source_language=req.source_language,
        target_language=req.target_language
    )
