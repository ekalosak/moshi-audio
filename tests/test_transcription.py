from pathlib import Path

from google.cloud.storage import Client
import pytest

from moshi import setup_loguru
from moshiaud import storage, transcribe

# NOTE must setup logging for TRANSCRIPT to be logged and not error
setup_loguru()

# NOTE speech to text works for flac and wav only: https://cloud.google.com/speech-to-text/docs/encoding

@pytest.mark.skip("The store client points to demo-test, hardcoded, so this fails with a billing error.")
def test_transcribe_gs_path(usr_audio: Path, store: Client):
    """Test transcription of a local audio file."""
    # NOTE: This test is not run in CI because it requires a GCP project with
    #       a valid service account key. It is run locally by developers.
    if usr_audio.suffix not in ('.wav', '.flac'):
        pytest.skip(f"Skipping test for audio with suffix: {usr_audio.suffix}")
    if 'mono' not in usr_audio.stem:
        pytest.skip(f"Google Speech-to-Text only supports mono audio, not stereo. Skipping test for audio with stem: {usr_audio.stem}")
    print(f"usr_audio={usr_audio}")
    gs_path = Path("tests/data") / usr_audio.name
    storage.upload(usr_audio, gs_path, store)
    transcription = transcribe.transcribe(gs_path, "en-US")
    print(f"transcription={transcription}")
    assert transcription == "hello"

def test_transcribe_gs_bytes(usr_audio: Path, store: Client):
    """Test transcription of a local audio file using the transcription's direct bytes functionality."""
    if usr_audio.suffix not in ('.wav', '.flac'):
        pytest.skip(f"Skipping test for audio with suffix: {usr_audio.suffix}")
    if 'mono' not in usr_audio.stem:
        pytest.skip(f"Google Speech-to-Text only supports mono audio, not stereo. Skipping test for audio with stem: {usr_audio.stem}")
    print(f"usr_audio={usr_audio}")
    with open(usr_audio, 'rb') as f:
        audio_bytes = f.read()
    transcription = transcribe.transcribe(audio_bytes, "en-US")
    print(f"transcription={transcription}")
    assert transcription == "hello"