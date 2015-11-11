import os
import subprocess
import sys
import logging
import shutil
import datetime

from flask import Flask, jsonify, render_template, request
from werkzeug import secure_filename

from manager import ocr_manager, recognition_manager, s3_manager, image_manager

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config.from_pyfile('config.py')
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMP_FOLDER'] = '/tmp'
app.config['OCR_OUTPUT_FILE'] = 'ocr'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])

def getCurrentTimestamp():
    return str(datetime.datetime.now()).split('.')[0].translate(None, '-: ')

@app.errorhandler(404)
def not_found(error):
    resp = jsonify( {
        u'status': 404,
        u'message': u'Resource not found'
    } )
    resp.status_code = 404
    return resp

@app.route('/')
def api_root():
    resp = jsonify( {
        u'status': 200,
        u'message': u'Welcome to our secret APIs'
    } )
    resp.status_code = 200
    return resp

@app.route('/s3/all', methods = ['GET'])
def getAllfiles():
    return s3_manager.get_all_s3_files()

@app.route('/upload', methods = ['GET'])
def upload():
    # return render_template('upload_form.html', landing_page = 'process')
    return render_template('upload_form.html', landing_page = 'fileupload')

@app.route('/fileupload', methods = ['GET', 'POST'])
def fileUpload():
    if request.method == 'POST':
        file = request.files['file']
        # print file
        if file and allowed_file(file.filename):
            filename = getCurrentTimestamp() + '_' + secure_filename(file.filename) #filename and extension
            file_path = image_manager.saveFile(file, filename)
            # upload to amazon s3
            s3_url = s3_manager.upload_image_to_s3(filename, file_path)
            print s3_url
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
    elif request.method == 'GET':
        resp = jsonify( {
                u'status': 200,
                u'message': str('I\'m working.')
            } )
        resp.status_code = 200
        return resp
    return None

@app.route('/compareimg', methods = ['GET'])
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

@app.route('/process', methods = ['GET','POST'])
def process():
    if request.method == 'POST':
        file = request.files['file']
        hocr = request.form.get('hocr') or ''
        ext = '.hocr' if hocr else '.txt'
        if file and allowed_file(file.filename):
            folder = os.path.join(app.config['TEMP_FOLDER'], str(os.getpid()))
            os.mkdir(folder)
            input_file = os.path.join(folder, secure_filename(file.filename))
            output_file = os.path.join(folder, app.config['OCR_OUTPUT_FILE'])
            file.save(input_file)

            command = ['tesseract', input_file, output_file, '-l', request.form['lang'], hocr]
            proc = subprocess.Popen(command, stderr=subprocess.PIPE)
            proc.wait()

            output_file += ext

            if os.path.isfile(output_file):
                f = open(output_file)
                resp = jsonify( {
                    u'status': 200,
                    u'ocr':{k:v.decode('utf-8') for k,v in enumerate(f.read().splitlines())},
                    u'value': str('123')
                } )
            else:
                resp = jsonify( {
                    u'status': 422,
                    u'message': u'Unprocessable Entity'
                } )
                resp.status_code = 422

            shutil.rmtree(folder)
            return resp
        else:
            resp = jsonify( {
                u'status': 415,
                u'message': u'Unsupported Media Type'
            } )
            resp.status_code = 415
            return resp
    else:
        resp = jsonify( {
            u'status': 405,
            u'message': u'The method is not allowed for the requested URL'
        } )
        resp.status_code = 405
        return resp

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(app.config.get('HOST'), app.config.get('PORT'), app.debug)
