__author__ = 'SARA'
import datetime
from flask import Flask, jsonify, current_app as app
from collections import OrderedDict
from werkzeug import secure_filename
from microsofttranslator import Translator
import spidermonkey

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
        # print s3_url
        # image recognition
        has_existing_image = image_process(s3_url)
        if has_existing_image is not None:
            # get the audio
            return has_existing_image
        # insert to database
        image_manager.insert_image_to_db(s3_url)
        # process the image via ocr
        output = ocr_manager.process_image(s3_url)
        # translate ocr output to chinese
        chinese_output = translator(output)
        # call js

        resp = jsonify( {
            u'status': 200,
            u'message': str(chinese_output)
        } )
        resp.status_code = 200
        # delete file
        image_manager.deleteFile(file_path)
        return resp
    else:
        error_resp = jsonify({
            u'status': 200,
            u'message': str('Not process')
        } )
        error_resp.status_code = 200
        return error_resp

def test_file_upload(file):
    if file and allowed_file(file.filename):
        filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        file_path = image_manager.saveFile(file, filename)
        # upload to amazon s3
        s3_url = s3_manager.upload_image_to_s3(filename, file_path)
        # print s3_url
        # insert to database
        image_manager.insert_image_to_db(s3_url)
        # process the image via ocr
        output = ocr_manager.process_image(s3_url)
        # translate ocr output to chinese
        # chinese_output = translator(output)
        resp = jsonify( {
            u'status': 200,
            u'message': str(output)
        } )
        resp.status_code = 200
        # delete file
        image_manager.deleteFile(file_path)
        return resp
    else:
        error_resp = jsonify({
            u'status': 200,
            u'message': str('Not process')
        } )
        error_resp.status_code = 200
        return error_resp

def image_process(new_uploaded_url):
    results = {}
    # retrieve 1 months worth of images from DB
    files_to_compare = image_manager.list_compare_images(30)
    if files_to_compare is None:
        return None
    for img_obj in files_to_compare:
        img_obj_id = img_obj.image_id
        img_obj_url = img_obj.image_url
        similarity = recognition_manager.get_images_rms_similarity(new_uploaded_url, img_obj_url)
        results[img_obj_id] = similarity
    sort_results = OrderedDict(sorted(results.items(),key=lambda kv: kv[1], reverse=True))
    # get the first element
    image_id, highest_similarity = sort_results.items()[0]
    # print highest_similarity
    # threshold for similarity
    if highest_similarity >= 80:
        return image_id
    return None

def compareImage(file):
    if file and allowed_file(file.filename):
        filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        file_path = image_manager.saveFile(file, filename)
        # upload to amazon s3
        s3_url = s3_manager.upload_image_to_s3(filename, file_path)
        return image_process(s3_url)
    return None

def translator(text):
    translator = Translator(app.config['MS_TRANSLATOR_CLIENT_ID'], app.config['MS_TRANSLATOR_CLIENT_SECRET'])
    return translator.translate(text, "zh-CHT").encode('utf-8')

def loadJsFile(fname):
    return open(fname).read()

def exec_webspeech(text):
    chinese_output = translator(text)
    rt = spidermonkey.Runtime()
    cx = rt.new_context()
    cx.add_global("loadfile", loadJsFile)
    ret = cx.execute('var contents = loadfile("WebSpeech.js"); eval(contents);')
    return ret