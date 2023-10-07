import os
from pathlib import Path
import tempfile

from google.cloud.storage import Client
from loguru import logger

from moshi import traced


AUDIO_BUCKET = os.getenv("AUDIO_BUCKET")
logger.info(f"AUDIO_BUCKET={AUDIO_BUCKET}")


@traced
def download(audio_path: str, store: Client) -> str:
    """Download an audio file from storage to a local temporary file.
    Caller is responsible for deleting the temporary file.
    Optional tmp path.
    Returns:
        tfn: the path to the temporary file.
    """
    logger.debug(f"audio_path={audio_path}")
    with logger.contextualize(audio_bucket=AUDIO_BUCKET, audio_path=audio_path):
        logger.trace("Creating objects...")
        afl = Path(audio_path)
        if tmp is None:
            _, tmp = tempfile.mkstemp(suffix=afl.suffix, prefix=afl.stem, dir='/tmp')
        try:
            bucket = store.bucket(AUDIO_BUCKET)
        except ValueError as e:
            raise ValueError(f"Could not find bucket {AUDIO_BUCKET}; set AUDIO_BUCKET env var to existing bucket") from e
        blob = bucket.blob(audio_path)
        logger.trace("Downloading bytes...")
        blob.download_to_filename(tmp)
    return tmp

@traced
def upload(file_path: Path, storage_path: Path, store: Client, bucket_name: str=AUDIO_BUCKET):
    """Upload a file to storage.
    Args:
        file_path: the path to the file to upload.
        storage_path: the path to the file in storage.
        bucket: the storage bucket to upload to.
    """
    with logger.contextualize(file_path=file_path, storage_path=storage_path, bucket=bucket_name):
        logger.debug("Creating objects...")
        bucket = store.bucket(bucket_name)
        _upload_here = str(storage_path)
        blob = bucket.blob(_upload_here)
        _upload_me = str(file_path)
        logger.debug(f"Uploading bytes: from {_upload_me} to {_upload_here}")
        blob.upload_from_filename(_upload_me)