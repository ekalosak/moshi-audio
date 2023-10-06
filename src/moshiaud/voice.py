import os

from google.cloud.firestore import Client
from google.cloud import texttospeech as tts
from loguru import logger

from moshi import traced

# TODO move Voice to moshi-base..?

GOOGLE_VOICE_SELECTION_TIMEOUT = int(os.getenv("GOOGLE_VOICE_SELECTION_TIMEOUT", 5))
logger.info(f"GOOGLE_VOICE_SELECTION_TIMEOUT={GOOGLE_VOICE_SELECTION_TIMEOUT}")

def gender_match(g1: str, g2: tts.SsmlVoiceGender) -> bool:
    if g1.lower() not in ("male", "female"):
        raise ValueError(f"SSML Gender not yet supported: {g1}")
    if g1.lower() == "female" and g2 == 2:
        return True
    elif g1.lower() == "male" and g2 == 1:
        return True
    else:
        return False

@traced
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

# def get_voice(bcp47: str, gender="FEMALE", model="Standard", random_choice=False) -> str:
#     """Get a valid voice for the language. Just picks the first match.
#     Args:
#         - bcp47: Language code in BPC 47 format e.g. "en-US" https://www.rfc-editor.org/rfc/bcp/bcp47.txt
#         - gender: SSML Gender
#         - model: Voice model class (e.g. "Standard", "WaveNet")
#         - random_choice: if True, pick a random voice from the list of matches. If False, pick the first match.
#     Raises:
#         - ValueError if no voice found.
#     Source:
#         - https://cloud.google.com/text-to-speech/pricing for list of valid voice model classes
#     """
#     logger.debug(f"Getting voice for: {bcp47}")
#     voices = list_voices(bcp47)
#     logger.debug(f"Language {bcp47} has {len(voices)} supported voices.")
#     model_matches = []
#     for voice in voices:
#         if model.lower() in voice.name.lower():
#             model_matches.append(voice)
#     if len(model_matches) == 0:
#         logger.warning(f"No voice found for model={model}, using any model.")
#         model_matches = voices
#     gender_matches = []
#     for voice in model_matches:
#         if gender_match(gender, voice.ssml_gender):
#             gender_matches.append(voice)
#     if len(gender_matches) == 0:
#         logger.warning(f"No voice found for gender={gender}, using any model.")
#         gender_matches = model_matches
#     voices = gender_matches
#     if len(voices) > 0:
#         voice = random.choice(voices)
#         logger.debug(f"Found voice: ({voice.name} {voice.ssml_gender})")
#         return voice
#     raise ValueError(f"Voice not found for {bcp47}, gender={gender}, model={model}")
