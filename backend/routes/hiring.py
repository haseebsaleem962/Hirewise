"""
Hiring criteria routes - manage screening criteria for candidate evaluation.
"""
from flask import Blueprint, request, jsonify
from models import db, HiringCriteria
from routes.auth import get_default_user

hiring_bp = Blueprint('hiring', __name__)


@hiring_bp.route('', methods=['POST'])
def create_criteria():
    current_user = get_default_user()
    data = request.get_json()

    if not data or not data.get('role_title') or not data.get('required_skills'):
        return jsonify({'error': 'role_title and required_skills are required'}), 400

    criteria = HiringCriteria(
        role_title=data['role_title'],
        required_skills=data['required_skills'],
        required_experience=data.get('required_experience', ''),
        education_requirement=data.get('education_requirement', ''),
        minimum_score=data.get('minimum_score', 70),
        job_description=data.get('job_description', ''),
        created_by=current_user.id
    )
    db.session.add(criteria)
    db.session.commit()

    return jsonify({
        'message': 'Hiring criteria created',
        'criteria': criteria.to_dict()
    }), 201


@hiring_bp.route('', methods=['GET'])
def list_criteria():
    current_user = get_default_user()
    all_criteria = HiringCriteria.query.filter_by(created_by=current_user.id)\
        .order_by(HiringCriteria.created_at.desc()).all()
    return jsonify({
        'criteria': [c.to_dict() for c in all_criteria]
    }), 200


@hiring_bp.route('/<int:criteria_id>', methods=['GET'])
def get_criteria(criteria_id):
    criteria = HiringCriteria.query.get_or_404(criteria_id)

    result = criteria.to_dict()
    result['candidates'] = [c.to_dict() for c in criteria.candidates]

    return jsonify({'criteria': result}), 200


@hiring_bp.route('/<int:criteria_id>', methods=['PUT'])
def update_criteria(criteria_id):
    criteria = HiringCriteria.query.get_or_404(criteria_id)
    data = request.get_json()

    if data.get('role_title'):
        criteria.role_title = data['role_title']
    if data.get('required_skills') is not None:
        criteria.required_skills = data['required_skills']
    if data.get('required_experience') is not None:
        criteria.required_experience = data['required_experience']
    if data.get('education_requirement') is not None:
        criteria.education_requirement = data['education_requirement']
    if data.get('minimum_score') is not None:
        criteria.minimum_score = data['minimum_score']
    if data.get('job_description') is not None:
        criteria.job_description = data['job_description']

    db.session.commit()

    return jsonify({
        'message': 'Hiring criteria updated',
        'criteria': criteria.to_dict()
    }), 200


@hiring_bp.route('/<int:criteria_id>', methods=['DELETE'])
def delete_criteria(criteria_id):
    criteria = HiringCriteria.query.get_or_404(criteria_id)
    db.session.delete(criteria)
    db.session.commit()

    return jsonify({'message': 'Hiring criteria deleted'}), 200
