from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/tgstore.sdb'
db = SQLAlchemy(app)

class host_binary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_guid = db.Column(db.Integer)
    md5hash = db.Column(db.Text)
    execution_time = db.Column(db.DateTime)

    def __repr__(self):
        return "host_binary: <%d>" % self.id

class tg_ioc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_ioc_string = db.Column(db.Text, unique=True)
    categories = db.Column(db.Text)
    title = db.Column(db.Text)
    long_description = db.Column(db.Text)
    severity = db.Column(db.Integer)
    confidence = db.Column(db.Integer)

    def __repr__(self):
        return "tg_ioc: <%d>" % self.id

