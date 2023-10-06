import os

from google.cloud import speech as stt

from loguru import logger
from moshi import traced

from .exceptions import TranscriptionError

GCLOUD_PROJECT = os.getenv("GCP_PROJECT", None)
client = stt.SpeechClient(project=GCLOUD_PROJECT)
logger.info(f"Speech client initialized, using project: {client.project}")

@traced
def transcribe(aud: str | bytes, bcp47: str) -> str:
    """Transcribe audio to text using Google Cloud Speech-to-Text.
    Args:
        - aud: audio GCP Storage path  e.g. "gs://moshi-audio/activities/1/1/1.wav"
        - bcp47: BCP 47 language code e.g. "en-US" https://www.rfc-editor.org/rfc/bcp/bcp47.txt
    Notes:
        - https://cloud.google.com/speech-to-text/docs/error-messages
            - "Invalid recognition 'config': bad encoding"
        - https://cloud.google.com/speech-to-text/docs/troubleshooting#returns_an_empty_response
            - Usually it's the emulator's mic being disabled...
    """
    with logger.contextualize(aud=aud if isinstance(aud, str) else 'bytes ommitted', bcp47=bcp47):
        if isinstance(aud, str):
            config = stt.RecognitionConfig(language_code=bcp47)
            audio = stt.RecognitionAudio(uri=aud)
        elif isinstance(aud, bytes):
            config = stt.RecognitionConfig(
                # NOTE wav and flac get encoding and sample rate from the file headers.
                # encoding=stt.RecognitionConfig.AudioEncoding.LINEAR16,
                # sample_rate_hertz=16000,
                language_code=bcp47,
            )
            audio = stt.RecognitionAudio(content=aud)
        else:
            raise TypeError(f"Invalid type for 'aud': {type(aud)}")
        logger.debug(f"RecognitionConfig: type(aud)={type(aud)} config={config}")
        logger.debug(f"RecognitionAudio: {audio if isinstance(aud, str) else 'bytes: ommitted'}")
        response = client.recognize(config=config, audio=audio)
        logger.debug(f"response={response}")
        try:
            text = response.results[0].alternatives[0].transcript
            conf = response.results[0].alternatives[0].confidence
        except IndexError as exc:
            raise TranscriptionError("No transcription found. Usually this means silent audio, but it could be corrupted audio.") from exc
        with logger.contextualize(confidence=conf):
            logger.log("TRANSCRIPT", text)
        return text