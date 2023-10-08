import os

from google.cloud.firestore import Client
from google.cloud import texttospeech as tts
from loguru import logger
from typing import Literal

from moshi import traced
from moshi.storage import DocPath
from moshi.voice import Voice as BaseVoice
from .__version__ import __version__

GOOGLE_VOICE_SELECTION_TIMEOUT = int(os.getenv("GOOGLE_VOICE_SELECTION_TIMEOUT", 5))
logger.info(f"GOOGLE_VOICE_SELECTION_TIMEOUT={GOOGLE_VOICE_SELECTION_TIMEOUT}")

class Voice(BaseVoice):
    _tts_voice: tts.Voice = None
    audio_version: str = __version__

    def __init__(self, bcp47: str=None, model: str=None, tts_voice: tts.Voice=None, **kwargs):
        if not bcp47 and not tts_voice:
            raise ValueError("Must provide either bcp47 or tts_voice.")
        elif tts_voice and bcp47:
            raise ValueError("Must provide either bcp47 or tts_voice, not both.")
        elif bcp47:
            super().__init__(bcp47=bcp47, model=model, **kwargs)
        else:
            if len(tts_voice.language_codes) > 1:
                logger.warning(f"Voice ({tts_voice.name}) has multiple language codes, only using first: {tts_voice.language_codes}")
            super().__init__(bcp47=tts_voice.language_codes[0], **kwargs)
        if not self._tts_voice:
            self._tts_voice = tts.Voice(
                name=self.model,
                ssml_gender=self.gender,
                natural_sample_rate_hertz=24000,
                language_codes=[self.bcp47],
            )

    def __eq__(self, other):
        if isinstance(other, Voice):
            return self.bcp47 == other.bcp47 and self.model == other.model
        return False

    @classmethod
    def _kwargs_from_docpath(cls, docpath: DocPath) -> dict:
        return dict(bcp47=docpath.parts[2]) 

    def get_docpath(bcp47: str) -> DocPath:
        return DocPath(f"/config/voices/{bcp47}")

    def docpath(self):
        return self.get_docpath(self.bcp47)

    @classmethod
    @traced
    def list_voices(cls, bcp47: str, db: Client) -> list['Voice']:
        """List all voices supported by ChatMoshi. Retrieve them from the Firebase document /config/voices.
        If that doc doesn't exist, then list all voices from Google Cloud Text-to-Speech.
        Args:
            - lan: if provided, filter by language code. It must be a BCP 47 language code e.g. "en-US" https://www.rfc-editor.org/rfc/bcp/bcp47.txt
        """
        logger.debug(f"Listing voices for language: {bcp47}")
        doc = db.collection("config").document("voices").get()
        assert doc.exists, "Voices document doesn't exist."
        _voices = doc.to_dict()[bcp47]
        voices = [cls(**v) for v in _voices.values()]
        return sorted(voices, key=lambda v: v.model)

    @classmethod
    def get_voice(cls, bcp47: str, db: Client, gender=2, model="Standard") -> 'Voice':
        """Get a valid voice for the language. Just picks the first match.
        Args:
            - bcp47: Language code in BPC 47 format e.g. "en-US" https://www.rfc-editor.org/rfc/bcp/bcp47.txt
            - gender: SSML Gender
            - model: Voice model class (e.g. "Standard", "WaveNet")
        Raises:
            - ValueError if no voice found.
        Source:
            - https://cloud.google.com/text-to-speech/pricing for list of valid voice model classes
        """
        with logger.contextualize(bcp47=bcp47, gender=gender, voice_model=model):
            voices = cls.list_voices(bcp47, db)
            logger.info(f"Found {len(voices)} voices for language: {bcp47}")
            for voc in voices:
                if voc.gender == gender and model in voc.model:
                    return voc
            logger.warning("No complete match found")
            for voc in voices:
                if model in voc.model:
                    return voc
            raise ValueError(f"No voice found for bcp47={bcp47} gender={gender} model={model}")