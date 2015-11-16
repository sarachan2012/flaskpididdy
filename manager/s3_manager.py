import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import current_app as app

def setup_s3_connection():
    conn = boto.s3.connect_to_region(
       region_name = app.config.get('AWS_REGION'),
       aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID'),
       aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY'),
       calling_format = boto.s3.connection.OrdinaryCallingFormat()
    )
    bucket = conn.get_bucket(app.config.get('AWS_S3_BUCKET'))
    return bucket

def upload_image_audio_to_s3(filename, file_path):
    bucket = setup_s3_connection()
    k = bucket.new_key(filename)
    k.set_contents_from_filename(file_path)
    bucket.set_acl('public-read')
    return k.generate_url(expires_in=0, query_auth=False)

def get_all_s3_files():
    bucket = setup_s3_connection()
    arr = []
    for key in bucket.list():
        arr.append(key.name.decode('utf-8'))
    return str(arr)
