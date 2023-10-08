import os

from google.cloud import texttospeech as tts
import pytest

from moshiaud import voice

@pytest.mark.parametrize("bcp47,model", [("zh-Hans-CN", "cmn-CN-Standard-A"), ("en-US", "en-US-Standard-A"), ("yue-Hant-HK", "yue-HK-Standard-A")])
def test_default_voice(bcp47: str, model: str):
    voc = voice.Voice(bcp47, model)
    assert voc.bcp47 == bcp47
    assert voc.type in ['Standard', 'WaveNet']

@pytest.mark.fs
@pytest.mark.parametrize("bcp47", ["es-MX", "zh-Hans-CN", "en-US", "yue-Hant-HK", "ar-AE"])
def test_list_voices(bcp47):
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        pytest.skip("Skipping test because emulator not running; set the FIRESTORE_EMULATOR_HOST environment variable to run this test.")
    voices = voice.Voice.read_all(bcp47)
    assert len(voices) > 0
    assert all(isinstance(v, voices.Voice) for v in voices)
    for v in voices:
        assert v.bcp47 == bcp47
        assert v.name
        assert v.model in ['Standard', 'WaveNet']

@pytest.mark.fs
@pytest.mark.parametrize("bcp47", ["es-MX", "zh-Hans-CN", "en-US", "yue-Hant-HK", "ar-AE"])
@pytest.mark.parametrize("ssml", ["MALE", "FEMALE"])
def test_get_voice(bcp47, ssml):
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        pytest.skip("Skipping test because emulator not running; set the FIRESTORE_EMULATOR_HOST environment variable to run this test.")
    voc = voice.Voice.read(bcp47)
    assert isinstance(voc, tts.Voice)
    if bcp47.startswith("zh"):
        assert voc.name.startswith('cmn-CN'), "Language mismatch"
    else:
        assert voc.name.startswith(bcp47.split('-')[0]), "Language mismatch"