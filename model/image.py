# from sqlalchemy import Column, Integer, String, TIMESTAMP, func
# from database import Base, db_session

from model.database import db
import time

class Image(db.Model):
    __tablename__ = 'images'

    image_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String())
    # created_on= db.Column(db.TIMESTAMP,default=db.func.current_timestamp())
    # updated_on = db.Column(db.TIMESTAMP,default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_on= db.Column(db.BIGINT,default=time.time())
    updated_on = db.Column(db.BIGINT,default=time.time(), onupdate=time.time())

    def __init__(self, image_url):
        self.image_url = image_url

    def __repr__(self):
        return '<Image {}>'.format(self.image_id)

    def add(self,image):
        db.session.add(image)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self,image):
        db.session.delete(image)
        return db.session.commit()

