import os

from google.cloud.firestore import Client
from google.cloud import texttospeech as tts
import pytest

from moshiaud import audio, synthesize
from moshiaud.voice import Voice

@pytest.fixture(params=["en-US-Standard-A", "yue-HK-Standard-A"])
def voice(request) -> tts.Voice:
    voc = Voice(request.param)
    return voc.tts

@pytest.mark.gcp
def test_synthesize(db: Client):
    msg = "Hello"
    voc = voice.Voice.read("en-US", db)
    af = synthesize.synthesize(msg, voice)
    assert af.rate == 24000
    print(f"Test wav length: {audio.seconds(af)}")