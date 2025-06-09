from flask_login import UserMixin
from datetime import datetime
from extensions import db

SCHEMA = 'yourschema'

class User(UserMixin, db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # Increased length
    email = db.Column(db.String(128), unique=True, nullable=False)  # Increased length
    password = db.Column(db.String(512), nullable=False)  # Increased from 128 to 512
    pets = db.relationship('Pet', backref='owner', lazy=True,
                         primaryjoin='User.id == foreign(Pet.user_id)')
    
    def __init__(self, **kwargs):
        super(User, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

class Pet(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(f'{SCHEMA}.user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50))
    breed = db.Column(db.String(50))
    age = db.Column(db.Integer)
    photo = db.Column(db.String(200))
    health_records = db.relationship('HealthRecord', backref='pet', lazy=True,
                                   primaryjoin='Pet.id == foreign(HealthRecord.pet_id)')
    reminders = db.relationship('Reminder', backref='pet', lazy=True,
                              primaryjoin='Pet.id == foreign(Reminder.pet_id)')
    tasks = db.relationship('Task', backref='pet', lazy=True,
                          primaryjoin='Pet.id == foreign(Task.pet_id)')
    
    def __init__(self, **kwargs):
        super(Pet, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

class HealthRecord(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey(f'{SCHEMA}.pet.id'), nullable=False)
    type = db.Column(db.String(50))  # e.g., vaccination, vet visit, medication
    date = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    weight = db.Column(db.Float)

    def __init__(self, **kwargs):
        super(HealthRecord, self).__init__(**kwargs)

class Reminder(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey(f'{SCHEMA}.pet.id'), nullable=False)
    task = db.Column(db.String(100))
    due_date = db.Column(db.DateTime)
    recurring = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(Reminder, self).__init__(**kwargs)

class Task(db.Model):
    __table_args__ = {'schema': SCHEMA}
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey(f'{SCHEMA}.pet.id'), nullable=False)
    description = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)