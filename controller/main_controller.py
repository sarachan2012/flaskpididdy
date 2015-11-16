__author__ = 'SARA'
import datetime
from flask import Flask, jsonify, current_app as app
from collections import OrderedDict
from werkzeug import secure_filename
from microsofttranslator import Translator
import urllib2, urllib

from manager import ocr_manager, recognition_manager, s3_manager, image_manager, audio_manager

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['PNG', 'png', 'JPG', 'jpg', 'JPEG', 'jpeg', 'GIF', 'gif'])

def getCurrentTimestamp():
    return str(datetime.datetime.now()).split('.')[0].translate(None, '-: ')

def get_all_s3_files():
    return s3_manager.get_all_s3_files()

def file_upload(file):
    if file and allowed_file(file.filename):
        image_file_name = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        image_file_path = image_manager.saveFile(file, image_file_name)
        # upload to amazon s3
        image_s3_url = s3_manager.upload_image_audio_to_s3(image_file_name, image_file_path)
        # print image_s3_url
        # image recognition
        has_existing_image = image_process(image_s3_url)
        # print has_existing_image
        if has_existing_image is not None:
            # get the audio
            audio_obj = audio_manager.get_audio_lowest_refetch_image_only(has_existing_image)
            resp = jsonify( {
                u'status': 200,
                u'image_id': str(has_existing_image),
                u'audio_id': str(audio_obj.audio_id),
                u'audio_url': str(audio_obj.audio_url),
                u'message': str('Successful file upload.')
            } )
            resp.status_code = 200
            return resp
        # insert to database
        image_id = image_manager.insert_image_to_db(image_s3_url)
        # process the image via ocr
        output = ocr_manager.process_image(image_s3_url)
        print type(output)
        print str(output)
        # translate ocr output to chinese
        chinese_output = translator(output)
        # call js
        audio_file_name = getCurrentTimestamp() + '_' + "output.mp3"
        audio_file_path = audio_manager.getAudioFilePath(audio_file_name)
        audio_dl_file = exec_webspeech(chinese_output, audio_file_path)
        audio_s3_url = s3_manager.upload_image_audio_to_s3(audio_file_name, audio_file_path)
        # insert audio to db
        audio_id = audio_manager.insert_audio_to_db(audio_s3_url, image_id)

        resp = jsonify( {
            u'status': 200,
            u'image_id': str(image_id),
            u'audio_id': str(audio_id),
            u'audio_url': str(audio_s3_url),
            u'message': str('Successful file upload.')
        } )
        resp.status_code = 200
        # delete file
        image_manager.deleteFile(image_file_path)
        audio_manager.deleteAudioFile(audio_file_path)
        return resp
    else:
        error_resp = jsonify({
            u'status': 201,
            u'message': str('Not process')
        } )
        error_resp.status_code = 201
        return error_resp

def image_process(new_uploaded_url):
    results = {}
    # retrieve 1 months worth of images from DB
    files_to_compare = image_manager.list_compare_images(30)
    print 'Retrieve data: ' + str(len(files_to_compare))
    if len(files_to_compare) == 0:
        return None
    else:
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
        if highest_similarity >= 90:
            return image_id
    return None

def compareImage(file):
    if file and allowed_file(file.filename):
        filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        file_path = image_manager.saveFile(file, filename)
        # upload to amazon s3
        s3_url = s3_manager.upload_image_audio_to_s3(filename, file_path)
        return image_process(s3_url)
    return None

def translator(text):
    translator = Translator(app.config['MS_TRANSLATOR_CLIENT_ID'], app.config['MS_TRANSLATOR_CLIENT_SECRET'])
    return translator.translate(text, "zh-CHT").encode('utf-8')

def exec_webspeech(text, file_path):
    url = 'http://120.24.87.124/cgi-bin/ekho2.pl?cmd=SAVEMP3&voice=EkhoCantonese&speedDelta=0&pitchDelta=0&volumeDelta=0&text=' + text
    f = urllib2.urlopen(url)
    with open(file_path, "wb") as code:
        code.write(f.read())
    return True
    # return urllib.urlretrieve (url, filepath)

def update_refetch(image_id, audio_id):
    # get audio object and  update audio object
    audio_manager.update_audio_refetch(audio_id)
    # get the next best audio
    new_audio_obj = audio_manager.get_audio_lowest_refetch(image_id, audio_id)
    new_audio_id = new_audio_obj.audio_id
    new_audio_url = new_audio_obj.audio.audio_url
    resp = jsonify( {
        u'status': 200,
        u'image_id': str(image_id),
        u'audio_id': str(new_audio_id),
        u'audio_url': str(new_audio_url),
        u'message': str('Successful refetch.')
    } )
    resp.status_code = 200
    return resp

def test_file_upload(file):
    if file and allowed_file(file.filename):
        filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
        file_path = image_manager.saveFile(file, filename)
        # upload to amazon s3
        s3_url = s3_manager.upload_image_audio_to_s3(filename, file_path)
        # print s3_url
        # insert to database
        image_id = image_manager.insert_image_to_db(s3_url)
        # print image_id
        # process the image via ocr
        output = ocr_manager.process_image(s3_url)
        # translate ocr output to chinese
        # chinese_output = translator(output)
        resp = jsonify( {
            u'status': 200,
            u'message': str(image_id)
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
