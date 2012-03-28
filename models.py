from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/tgstore.sdb'
db = SQLAlchemy(app)

host_ioc = db.Table('tg_binary_ioc',
        db.Column('ioc_id', db.Integer, db.ForeignKey('tg_ioc.id')),
        db.Column('md5hash', db.Integer, db.ForeignKey('host_binary.md5hash'))
        )

class host_binary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_guid = db.Column(db.BigInteger, db.ForeignKey('host_guid.host_guid'))
    md5hash = db.Column(db.Text, db.ForeignKey('tg_binary.md5hash'))
    execution_time = db.Column(db.DateTime)

    counts = db.relationship('tg_ioc', secondary= host_ioc,
            backref=db.backref('counts', lazy='dynamic'),
            lazy='dynamic')

    def __repr__(self):
        return "host_binary: <%d>" % self.id

class host_guid(db.Model):
    host_guid = db.Column(db.BigInteger, primary_key=True)
    host_name = db.Column(db.Text)

    host = db.relationship('host_binary', uselist=False, backref='guid', lazy='dynamic')

    def __repr__(self):
        return "host_guid: <%d>" % self.host_guid

class tg_binary(db.Model):
    md5hash = db.Column(db.Text, primary_key=True)
    tg_id = db.Column(db.Integer)

    host = db.relationship('host_binary', uselist=False, backref='binary', lazy='dynamic')

    def __repr__(self):
        return "tg_binary: <%d>" % self.md5hash

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

