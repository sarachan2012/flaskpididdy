import os
import subprocess
import sys
import logging
import shutil
from flask import Flask, jsonify, render_template, request

from model.database import db
from controller import main_controller

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMP_FOLDER'] = '/tmp'
app.config['OCR_OUTPUT_FILE'] = 'ocr'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
# add configuration values
app.config.from_pyfile('config.py')
# set up database
db.init_app(app)
with app.test_request_context():
    # drop all tables
    # db.drop_all()
    # create all table on load
    db.create_all()


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
def getAllS3Files():
    return main_controller.get_all_s3_files()

@app.route('/upload', methods = ['GET'])
def upload():
    # return render_template('upload_form.html', landing_page = 'process')
    return render_template('upload_form.html', landing_page = 'fileupload')

@app.route('/fileupload', methods = ['GET', 'POST'])
def fileUpload():
    if request.method == 'POST':
        file = request.files['file']
        # print file
        return main_controller.file_upload(file)
    elif request.method == 'GET':
        resp = jsonify( {
                u'status': 200,
                u'message': str('I\'m working.')
            } )
        resp.status_code = 200
        return resp
    return None

@app.route('/test/js', methods = ['GET', 'POST'])
def test_js():
    return main_controller.exec_webspeech('Hello')

@app.route('/test/fileupload', methods = ['GET', 'POST'])
def test_fileUpload():
    if request.method == 'POST':
        file = request.files['file']
        # print file
        return main_controller.test_file_upload(file)
    elif request.method == 'GET':
        resp = jsonify( {
                u'status': 200,
                u'message': str('I\'m working.')
            } )
        resp.status_code = 200
        return resp
    return None

@app.route('/compareimg', methods = ['GET', 'POST'])
def compareImage():
    if request.method == 'POST':
        # files = request.files.getlist("file")
        file = request.files['file']
        resp = jsonify( {
            u'status': 200,
            u'message': str(main_controller.compareImage(file))
        })
        resp.status_code = 200
        return resp
    elif request.method == 'GET':
        resp = jsonify( {
            u'status': 200,
            u'message': str('I\'m working.')
        })
        resp.status_code = 200
        return resp


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(app.config.get('HOST'), app.config.get('PORT'), app.debug)
