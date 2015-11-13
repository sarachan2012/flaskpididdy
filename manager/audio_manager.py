__author__ = 'SARA'
from flask import current_app as app
from model.audio import Audio
from model.database import db

def insert_audio_to_db(audio_url, image_id):
    audio = Audio(audio_url, image_id, 0, 0)
    audio_add = audio.add(audio)
    if not audio_add:
        return True
    return False

def get_audio_lowest_refetch(image_id):
    # order by asc and first
    return None