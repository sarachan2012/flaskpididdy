import os
from flask import current_app as app
from model.image import Image
import time, datetime
from model.database import db
import date_manager
from random import randint
import shutil

def deleteFile(file_path):
    # folder = getFileFolder()
    folder = os.path.dirname(os.path.abspath(file_path))
    if os.path.isfile(file_path):
        # delete file only
        os.remove(file_path)
        # delete folder
        os.rmdir(folder)
        return True
    return False

def getFileFolder():
    # folder = os.path.join(app.config['TEMP_FOLDER'], str(os.getpid()))
    folder = os.path.join(app.config['TEMP_FOLDER'], str(randint(0,100)))
    return folder

def saveFile(file, filename):
    folder = getFileFolder()
    if not os._exists(folder):
        os.mkdir(folder)
    file_path = os.path.join(folder, filename)
    file.save(file_path)  # save the file
    return file_path

def insert_image_to_db(image_url):
    image = Image(image_url)
    image_add = image.add(image)
    if image_add is not None:
        return image_add.image_id
    return False

def list_compare_images(num_of_days):
    # get today date
    unix_now = date_manager.getUnixNow()
    now = date_manager.format_date(date_manager.convert_time_unix_to_human(unix_now))
    past = now - datetime.timedelta(days=num_of_days)
    unix_past = date_manager.convert_human_to_unix(past)

    # query the data database
    results = db.session.query(Image).filter(Image.created_on.between(unix_past, unix_now)).all()
    return results

def clear_images_table():
    results = db.session.query(Image).all()
    for r in results:
        print str(r.image_id)
        db.session.query(Image).filter(Image.image_id == r.image_id).delete()
        db.session.commit()