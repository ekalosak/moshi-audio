"""This module provides speech synthesis and transcription utilities.
"""
import os
import random
from textwrap import shorten

import av
from google.cloud import speech as stt
from google.cloud import texttospeech as tts
from firebase_admin.firestore import firestore
from loguru import logger

from moshi import traced


logger.trace('[START] Loading clients...')
sclient = stt.SpeechClient()
db = firestore.Client(project=GCLOUD_PROJECT)
logger.trace('[END] Loading clients...')