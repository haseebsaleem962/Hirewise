from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='recruiter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    hiring_criteria = db.relationship('HiringCriteria', backref='creator', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HiringCriteria(db.Model):
    __tablename__ = 'hiring_criteria'

    id = db.Column(db.Integer, primary_key=True)
    role_title = db.Column(db.String(200), nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, default='')
    required_experience = db.Column(db.String(100), default='')
    education_requirement = db.Column(db.String(200), default='')
    minimum_score = db.Column(db.Integer, default=70)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidates = db.relationship('Candidate', backref='criteria', lazy=True,
                                 cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'role_title': self.role_title,
            'required_skills': self.required_skills,
            'job_description': self.job_description or '',
            'required_experience': self.required_experience,
            'education_requirement': self.education_requirement,
            'minimum_score': self.minimum_score,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'candidate_count': len(self.candidates) if self.candidates else 0
        }


class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    criteria_id = db.Column(db.Integer, db.ForeignKey('hiring_criteria.id'), nullable=False)
    name = db.Column(db.String(200), default='')
    email = db.Column(db.String(200), default='')
    phone = db.Column(db.String(50), default='')
    gender = db.Column(db.String(50), default='')
    institute = db.Column(db.String(300), default='')
    degree = db.Column(db.String(300), default='')
    skills = db.Column(db.Text, default='')
    experience = db.Column(db.Text, default='')
    projects = db.Column(db.Text, default='')
    certifications = db.Column(db.Text, default='')
    location = db.Column(db.String(200), default='')
    resume_category = db.Column(db.String(100), default='')
    resume_text = db.Column(db.Text, default='')
    resume_file_path = db.Column(db.String(500), default='')
    match_score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(db.Text, default='')
    missing_skills = db.Column(db.Text, default='')
    ai_status = db.Column(db.String(50), default='Pending')
    manual_status = db.Column(db.String(50), default='')
    final_status = db.Column(db.String(50), default='Pending')
    blind_reviewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    email_logs = db.relationship('EmailLog', backref='candidate', lazy=True)

    def to_dict(self, blind=False):
        data = {
            'id': self.id,
            'criteria_id': self.criteria_id,
            'email': self.email,
            'phone': self.phone,
            'degree': self.degree,
            'skills': self.skills,
            'experience': self.experience,
            'projects': self.projects,
            'certifications': self.certifications,
            'resume_category': self.criteria.role_title if self.criteria else self.resume_category,
            'match_score': self.match_score,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'ai_status': self.ai_status,
            'manual_status': self.manual_status,
            'final_status': self.final_status,
            'blind_reviewed': self.blind_reviewed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if blind:
            data['name'] = 'Hidden'
            data['gender'] = 'Hidden'
            data['institute'] = 'Hidden'
            data['location'] = 'Hidden'
            data['email'] = 'Hidden'
            data['phone'] = 'Hidden'
        else:
            data['name'] = self.name
            data['gender'] = self.gender
            data['institute'] = self.institute
            data['location'] = self.location
        return data


class EmailLog(db.Model):
    __tablename__ = 'email_logs'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    email_type = db.Column(db.String(50), nullable=False)  # 'shortlisted' or 'rejected'
    email_status = db.Column(db.String(50), default='sent')
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'email_type': self.email_type,
            'email_status': self.email_status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'candidate_name': self.candidate.name if self.candidate else 'Unknown'
        }
