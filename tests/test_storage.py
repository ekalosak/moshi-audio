import os
from pathlib import Path

from google.cloud.storage import Client

from moshiaud import storage

TEST_FN = "dummy.txt"

def test_upload_doesnt_barf(store: Client, dummy_file: Path):
    print(f"AUDIO_BUCKET={storage.AUDIO_BUCKET}")
    storage.upload(dummy_file, TEST_FN, store)
    bucket = store.bucket(storage.AUDIO_BUCKET)
    bucket.delete_blob(TEST_FN, store)

def test_upload_download_both_work(store: Client, dummy_file: Path):
    with open(dummy_file, 'r') as f:
        expected_contents = f.read()
    storage.upload(dummy_file, TEST_FN, store)
    tmp = storage.download(TEST_FN, store)
    with open(tmp, 'r') as f:
        assert f.read() == expected_contents
    store.bucket(storage.AUDIO_BUCKET).delete_blob(TEST_FN)
    os.remove(tmp)