from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    time = db.Column(db.String(5), nullable=False)

    def __init__(self, title, time):
        self.title = title
        self.time = time

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time
        }

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, filename):
        self.filename = filename

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }