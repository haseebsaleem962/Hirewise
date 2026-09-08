"""
Authentication routes - simplified: no login required, auto-create default user.
"""
from flask import Blueprint, jsonify
from models import db, bcrypt, User

auth_bp = Blueprint('auth', __name__)


def get_default_user():
    """Get or create the default recruiter user (no auth needed)."""
    user = User.query.first()
    if not user:
        try:
            user = User(
                name='Recruiter',
                email='recruiter@company.com',
                password_hash=bcrypt.generate_password_hash('default').decode('utf-8'),
                role='recruiter'
            )
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            user = User.query.first()
    return user


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user = get_default_user()
    return jsonify({'user': user.to_dict()}), 200
