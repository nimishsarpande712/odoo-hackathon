from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=True)
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    email_verification_expires = db.Column(db.DateTime, nullable=True)
    
    # Password reset fields
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Security fields
    login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    offered_skills = db.relationship('UserSkillOffered', backref='user', cascade='all, delete-orphan')
    wanted_skills = db.relationship('UserSkillWanted', backref='user', cascade='all, delete-orphan')
    availability = db.relationship('Availability', backref='user', cascade='all, delete-orphan')
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='user', cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', cascade='all, delete-orphan')


class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    offered_by = db.relationship('UserSkillOffered', backref='skill', cascade='all, delete-orphan')
    wanted_by = db.relationship('UserSkillWanted', backref='skill', cascade='all, delete-orphan')


class UserSkillOffered(db.Model):
    __tablename__ = 'user_skills_offered'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete="CASCADE"), nullable=False)
    proficiency_level = db.Column(
        db.Enum('beginner', 'intermediate', 'advanced', 'expert', name='proficiency_level_enum'),
        default='beginner'
    )

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='unique_user_skill_offered'),)


class UserSkillWanted(db.Model):
    __tablename__ = 'user_skills_wanted'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete="CASCADE"), nullable=False)
    desired_level = db.Column(
        db.Enum('beginner', 'intermediate', 'advanced', 'expert', name='desired_level_enum'),
        default='intermediate'
    )

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='unique_user_skill_wanted'),)


class Availability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    day = db.Column(db.String(20))  # e.g., "Saturday"
    time_slot = db.Column(db.String(50))  # e.g., "Evening"


class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)


class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    email_address = db.Column(db.String(255), nullable=False)
    email_type = db.Column(
        db.Enum('verification', 'password_reset', 'welcome', 'notification', name='email_type_enum'),
        nullable=False
    )
    subject = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.Enum('sent', 'failed', 'bounced', name='email_status_enum'),
        default='sent'
    )
    error_message = db.Column(db.Text, nullable=True)
    template_used = db.Column(db.String(100), nullable=True)