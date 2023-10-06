import os

from google.cloud.firestore import Client
from google.cloud import texttospeech as tts
import pytest

from moshiaud import audio, voice, synthesize

@pytest.mark.gcp
def test_synthesize(db: Client):
    msg = "Hello"
    voc = voice.Voice.read("en-US", db)
    af = synthesize.synthesize(msg, voice)
    assert af.rate == 24000
    print(f"Test wav length: {audio.seconds(af)}")