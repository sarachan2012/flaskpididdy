__author__ = 'SARA'
from flask import current_app as app
from model.audio import Audio
from model.database import db
import os, shutil
from random import randint

def insert_audio_to_db(audio_url, image_id, refetch):
    audio = Audio(audio_url, image_id, refetch)
    audio_add = audio.add(audio)
    if audio_add is not None:
        return audio_add.audio_id
    return False

def getFileFolder():
    # folder = os.path.join(app.config['TEMP_FOLDER'], str(os.getpid()))
    folder = os.path.join(app.config['TEMP_FOLDER'], str(randint(0,100)))
    return folder

def getAudioFilePath(filename):
    folder = getFileFolder()
    if not os._exists(folder):
        os.mkdir(folder)
    file_path = os.path.join(folder, filename)
    return file_path

def saveAudioFile(file, filename):
    folder = getFileFolder()
    if not os._exists(folder):
        os.mkdir(folder)
    file_path = os.path.join(folder, filename)
    file.save(file_path)  # save the file
    return file_path

def deleteAudioFile(file_path):
    # folder = getFileFolder()
    folder = os.path.dirname(os.path.abspath(file_path))
    if os.path.isfile(file_path):
        # delete file only
        os.remove(file_path)
        # delete folder
        os.rmdir(folder)
        return True
    return False

def update_audio_refetch(audio_id):
    audio_obj = db.session.query(Audio).filter(Audio.audio_id==audio_id).first()
    # print "audio id:" + str(audio_id)
    old_refetch = audio_obj.refetch
    audio_obj.refetch = old_refetch + 1
    # print "old:" + str(old_refetch)
    # print "new:" + str(audio_obj.refetch)
    return db.session.commit()

def get_audio_lowest_refetch(image_id, audio_id):
    # order by asc and first
    # return (db.session.query(Audio).filter(Audio.image_id==image_id).filter(Audio.audio_id==audio_id).order_by(Audio.refetch)).first()
    obj = (db.session.query(Audio).filter(Audio.image_id==image_id).filter(Audio.audio_id==audio_id).order_by(Audio.refetch)).all()
    for o in obj:
        print str(o)
    # print str(obj.audio_url)
    return obj[0]

def get_audio_lowest_refetch_image_only(image_id):
    # order by asc and first
    return db.session.query(Audio).filter(Audio.image_id==image_id).order_by(Audio.refetch).first()

def clear_audios_table():
    num_rows_deleted = 0
    try:
        num_rows_deleted = db.session.query(Audio).delete()
        db.session.commit()
    except:
        db.session.rollback()
    return num_rows_deleted