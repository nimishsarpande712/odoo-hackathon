from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    _tablename_ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    offered_skills = db.relationship('UserSkillOffered', backref='user', cascade='all, delete-orphan')
    wanted_skills = db.relationship('UserSkillWanted', backref='user', cascade='all, delete-orphan')
    availability = db.relationship('Availability', backref='user', cascade='all, delete-orphan')


class Skill(db.Model):
    _tablename_ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    offered_by = db.relationship('UserSkillOffered', backref='skill', cascade='all, delete-orphan')
    wanted_by = db.relationship('UserSkillWanted', backref='skill', cascade='all, delete-orphan')


class UserSkillOffered(db.Model):
    _tablename_ = 'user_skills_offered'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete="CASCADE"), nullable=False)
    proficiency_level = db.Column(
        db.Enum('beginner', 'intermediate', 'advanced', 'expert', name='proficiency_level_enum'),
        default='beginner'
    )

    _table_args_ = (db.UniqueConstraint('user_id', 'skill_id', name='unique_user_skill_offered'),)


class UserSkillWanted(db.Model):
    _tablename_ = 'user_skills_wanted'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete="CASCADE"), nullable=False)
    desired_level = db.Column(
        db.Enum('beginner', 'intermediate', 'advanced', 'expert', name='desired_level_enum'),
        default='intermediate'
    )

    _table_args_ = (db.UniqueConstraint('user_id', 'skill_id', name='unique_user_skill_wanted'),)


class Availability(db.Model):
    _tablename_ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    day = db.Column(db.String(20))  # e.g., "Saturday"
    time_slot = db.Column(db.String(50))  # e.g., "Evening"