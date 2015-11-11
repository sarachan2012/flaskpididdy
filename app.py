import os,subprocess,sys,logging
import shutil, time, datetime
import pytesseract,requests,boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
from flask import Flask, jsonify, render_template, request
from werkzeug import secure_filename


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config.from_pyfile('config.py')
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMP_FOLDER'] = '/tmp'
app.config['OCR_OUTPUT_FILE'] = 'ocr'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'])

def process_image(url):
    image = _get_image(url)
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image)

def _get_image(url):
    return Image.open(StringIO(requests.get(url).content))

def upload_image_to_s3(file, file_path):
    filename = getCurrentTimestamp() + secure_filename(file.filename)
    conn = boto.s3.connect_to_region(
       region_name = app.config.get('AWS_REGION'),
       aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID'),
       aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY'),
       calling_format = boto.s3.connection.OrdinaryCallingFormat()
    )
    bucket = conn.get_bucket(app.config.get('AWS_S3_BUCKET'))
    k = bucket.new_key(filename)
    k.set_contents_from_filename(file_path)
    bucket.set_acl('public-read')
    return k.generate_url(expires_in=0, query_auth=False)

def deleteFile(folder, file_path):
    if os.path.isfile(file_path):
        # delete file only
        os.remove(file_path)
        # delete folder
        os.rmdir(folder)
        return True
    return False

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

@app.route('/alls3files', methods = ['GET'])
def getAllfiles():
    conn = boto.s3.connect_to_region(
       region_name = app.config.get('AWS_REGION'),
       aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID'),
       aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY'),
       calling_format = boto.s3.connection.OrdinaryCallingFormat()
    )
    bucket = conn.get_bucket(app.config.get('AWS_S3_BUCKET'))
    arr = []
    for key in bucket.list():
        arr.append(key.name.decode('utf-8', 'ignore'))
    return str(arr)

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
            filename = getCurrentTimestamp() + secure_filename(file.filename) #filename and extension
            folder = os.path.join(app.config['TEMP_FOLDER'], str(os.getpid()))
            os.mkdir(folder)
            file_path = os.path.join(folder, filename)
            file.save(file_path) # save the file
            # upload to amazon s3
            s3_url = upload_image_to_s3(file, file_path)
            print s3_url
            # process the image via ocr
            output = process_image(s3_url)
            resp = jsonify( {
                u'status': 200,
                u'message': str(output)
            } )
            resp.status_code = 200
            # delete file
            deleteFile(folder, file_path)
            return resp
    elif request.method == 'GET':
        resp = jsonify( {
                u'status': 200,
                u'message': str('I\'m working.')
            } )
        resp.status_code = 200
        return resp
    return None

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
