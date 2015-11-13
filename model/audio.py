# from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
# from database import Base, db_session

from model.database import db
import datetime,time
class Audio(db.Model):
    __tablename__ = 'audio'

    audio_id = db.Column(db.Integer, primary_key=True)
    audio_url = db.Column(db.String())
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    refetch = db.Column(db.Integer)
    replay = db.Column(db.Integer)
    # created_on= db.Column(db.TIMESTAMP,default=db.func.current_timestamp())
    # updated_on = db.Column(db.TIMESTAMP,default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    # created_on= db.Column(db.DateTime,default=datetime.datetime.utcnow)
    # updated_on = db.Column(db.DateTime,default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_on= db.Column(db.BIGINT,default=time.time())
    updated_on = db.Column(db.BIGINT,default=time.time(), onupdate=time.time())

    def __init__(self, audio_url, image_id, refetch, replay):
        self.audio_url = audio_url
        self.image_id = image_id
        self.refetch = refetch
        self.replay = replay

    def __repr__(self):
        return '<Audio {}>'.format(self.audio_id)

    def add(self,audio):
        db.session.add(audio)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self,audio):
        db.session.delete(audio)
        return db.session.commit()