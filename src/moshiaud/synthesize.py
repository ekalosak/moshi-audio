import os

import av
from google.cloud import texttospeech as tts
from loguru import logger

from moshi import traced
from . import audio

GOOGLE_SPEECH_SYNTHESIS_TIMEOUT = int(os.getenv("GOOGLE_SPEECH_SYNTHESIS_TIMEOUT", 5))

client = tts.TextToSpeechClient()

def _synthesize_bytes(text: str, voice: tts.Voice, rate: int = 24000) -> bytes:
    """Synthesize speech to a bytestring in WAV (PCM_16) format.
    Implemented with tts.googleapis.com;
    """
    logger.debug(f"text={text} voice={voice} rate={rate}")
    synthesis_input = tts.SynthesisInput(text=text)
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16,  # NOTE fixed s16 format
        sample_rate_hertz=rate,
    )
    langcode = voice.language_codes[0]
    logger.trace(f"Extracted language code from voice: {langcode}")
    voice_selector = tts.VoiceSelectionParams(
        name=voice.name,
        language_code=langcode,
        ssml_gender=voice.ssml_gender,
    )
    with logger.contextualize(voice_selector=voice_selector, audio_config=audio_config):
        logger.trace(f"Synthesizing speech for: {synthesis_input}")
        request = dict(
            input=synthesis_input,
            voice=voice_selector,
            audio_config=audio_config,
        )
        response = client.synthesize_speech(request=request, timeout=GOOGLE_SPEECH_SYNTHESIS_TIMEOUT)
        logger.trace(f"Synthesized speech: {len(response.audio_content)} bytes")
    return response.audio_content

def _synthesize_af(text: str, voice: tts.Voice, rate: int = 24000) -> av.AudioFrame:
    audio_bytes = _synthesize_bytes(text, voice, rate)
    audio_frame = audio.wav2af(audio_bytes)
    return audio_frame

@traced
def synthesize(text: str, voice: tts.Voice, rate: int = 24000, to="audio_frame") -> av.AudioFrame | bytes:
    """Synthesize speech to an AudioFrame or Storage.
    Returns:
        - AudioFrame: if to == "audio_frame"
        - bytes: raw WAV format audio if to == "bytes"
    Raises:
        - ValueError if to is invalid.
    """
    with logger.contextualize(text=text, voice=voice, rate=rate, to=to):
        if to == "audio_frame":
            result = _synthesize_af(text, voice, rate)
        elif to == "bytes":
            result = _synthesize_bytes(text, voice, rate)
        else:
            raise ValueError(f"Invalid value for 'to': {to}")
        logger.trace(f"synthesized speech: {type(result)}")
        assert isinstance(result, (av.AudioFrame, bytes, str))
    return result
