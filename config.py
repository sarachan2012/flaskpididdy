import os

HOST = 'localhost'
PORT = 5000
DEBUG = True

# AWS_S3_BUCKET = 'media.pi-diddy.herokuapp.com'
AWS_S3_BUCKET = 'media2.pi-diddy.herokuapp.com'
AWS_ACCESS_KEY_ID = 'AKIAJEY5PHY35DCUPXGA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-southeast-1'

SQLALCHEMY_DATABASE_URI = "postgresql://admin-pididdy:pididdy@localhost:5432/pididdy"
# SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = True

MS_TRANSLATOR_CLIENT_ID = 'ms_translator_school'
MS_TRANSLATOR_CLIENT_SECRET = '73lkrZ1Pw8ELdduFBX0KDQp/Ncw/hoP107Ob03nLHnk='