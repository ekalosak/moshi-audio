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
    bcp47: str  # af-ZA  /config/voices doc -> af-ZA key -> af-ZA-Standard-A key -> data dict[str, str]
    model: str  # af-ZS-Standard-A  data['model']
    language_name: str  # Afrikaans (South Africa)  data['language_name']
    ssml_gender: int  # 1 male 2 female
    type: Literal['wavenet', 'standard']  # standard  data['type']

    def __init__(self, bcp47: str=None, tts_voice: tts.Voice=None, **kwargs):
        if not bcp47 and not tts_voice:
            raise ValueError("Must provide either bcp47 or tts_voice.")
        elif tts_voice and bcp47:
            raise ValueError("Must provide either bcp47 or tts_voice, not both.")
        elif bcp47:
            super().__init__(bcp47=bcp47, **kwargs)
        else:
            if len(tts_voice.language_codes) > 1:
                logger.warning(f"Voice ({tts_voice.name}) has multiple language codes, only using first: {tts_voice.language_codes}")
            super().__init__(bcp47=tts_voice.language_codes[0], **kwargs)

    def __eq__(self, other):
        if isinstance(other, Voice):
            return self.bcp47 == other.bcp47 and self.model == other.model
        return False

    @property
    def audio_version(self) -> str:
        return self._audio_version

    @classmethod
    def _kwargs_from_docpath(cls, docpath: DocPath) -> dict:
        return dict(bcp47=docpath.parts[2]) 

    def get_docpath(bcp47: str) -> DocPath:
        return DocPath(f"/config/voices/{bcp47}")

    def docpath(self):
        return self.get_docpath(self.bcp47)

    @traced
    @staticmethod
    def list_voices(bcp47: str, db: Client) -> list[tts.Voice]:
        """List all voices supported by ChatMoshi. Retrieve them from the Firebase document /config/voices.
        If that doc doesn't exist, then list all voices from Google Cloud Text-to-Speech.
        Args:
            - lan: if provided, filter by language code. It must be a BCP 47 language code e.g. "en-US" https://www.rfc-editor.org/rfc/bcp/bcp47.txt
        """
        logger.debug(f"Listing voices for language: {bcp47}")
        doc = db.collection("config").document("voices").get()
        assert doc.exists, "Voices document doesn't exist."
        _voices = doc.to_dict()[bcp47]
        voices = [tts.Voice(
            name=name,
            ssml_gender=model['ssml_gender'],
            natural_sample_rate_hertz=24000,
            language_codes=[bcp47],
        ) for name, model in _voices.items()]
        return voices

    @classmethod
    def get_voice(cls, bcp47: str, gender=2, model="Standard") -> 'Voice':
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
        logger.debug(f"Getting voice for: {bcp47}")
        voc: list[Voice] = Voice.list_voices(bcp47)
        logger.debug(f"Language {bcp47} has {len(voices)} supported voices.")
        model_matches = []
        ...
        # for voice in voices:
        #     if model.lower() == voice.model
        #         model_matches.append(voice)
        # if len(model_matches) == 0:
        #     logger.warning(f"No voice found for model={model}, using any model.")
        #     model_matches = voices
        # gender_matches = []
        # for voice in model_matches:
        #     if voice.
        # if len(gender_matches) == 0:
        #     logger.warning(f"No voice found for gender={gender}, using any model.")
        #     gender_matches = model_matches
        # voices = gender_matches
        # if len(voices) > 0:
        #     voice = random.choice(voices)
        #     logger.debug(f"Found voice: ({voice.name} {voice.ssml_gender})")
        #     return voice
        # raise ValueError(f"Voice not found for {bcp47}, gender={gender}, model={model}")
