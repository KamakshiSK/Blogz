from datetime import datetime
from app import db
from hashutils import make_pw_hash

class Blog(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
    def __init__(self, title, content, owner, timestamp=None):
        self.title = title
        self.content =  content
        if timestamp == None:
            self.timestamp = datetime.utcnow()
        self.owner = owner

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable= False)
    password = db.Column(db.String(120), nullable = False)

    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = make_pw_hash(password)