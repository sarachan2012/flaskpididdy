__author__ = 'SARA'
import datetime
from flask import Flask, jsonify
from werkzeug import secure_filename

from manager import ocr_manager, recognition_manager, s3_manager, image_manager

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])

def getCurrentTimestamp():
    return str(datetime.datetime.now()).split('.')[0].translate(None, '-: ')

def get_all_s3_files():
    return s3_manager.get_all_s3_files()

def file_upload(file):
    if file and allowed_file(file.filename):
        filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        file_path = image_manager.saveFile(file, filename)
        # upload to amazon s3
        s3_url = s3_manager.upload_image_to_s3(filename, file_path)
        print s3_url
        # insert to database
        image_manager.insert_image_to_db(s3_url)
        # process the image via ocr
        output = ocr_manager.process_image(s3_url)
        resp = jsonify( {
            u'status': 200,
            u'message': str(output)
        } )
        resp.status_code = 200
        # delete file
        image_manager.deleteFile(file_path)
        return resp
    else:
        error_resp = jsonify( {
            u'status': 200,
            u'message': str('Not process')
        } )
        error_resp.status_code = 200
        return error_resp

def compareImage():
    diff = recognition_manager.compare_image_rms()
    similarity = recognition_manager.get_images_similarity(diff)
    resp = jsonify( {
            u'status': 200,
            u'difference': str(diff),
            u'similarity': str(similarity)
        } )
    resp.status_code = 200
    return resp