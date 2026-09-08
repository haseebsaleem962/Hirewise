"""
Dashboard routes - aggregate stats and recent activity.
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from models import db, Candidate, HiringCriteria, EmailLog
from routes.auth import get_default_user

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    current_user = get_default_user()
    """Get dashboard statistics."""
    # Count criteria created by this user
    user_criteria_ids = [c.id for c in HiringCriteria.query.filter_by(
        created_by=current_user.id).all()]

    if not user_criteria_ids:
        return jsonify({
            'total_candidates': 0,
            'total_criteria': 0,
            'shortlisted': 0,
            'rejected': 0,
            'selected': 0,
            'on_hold': 0,
            'pending': 0,
            'avg_match_score': 0,
            'category_breakdown': {},
            'status_breakdown': {}
        }), 200

    # Total candidates
    total = Candidate.query.filter(
        Candidate.criteria_id.in_(user_criteria_ids)).count()

    # Status counts
    status_counts = db.session.query(
        Candidate.final_status, func.count(Candidate.id)
    ).filter(
        Candidate.criteria_id.in_(user_criteria_ids)
    ).group_by(Candidate.final_status).all()

    status_dict = {s: c for s, c in status_counts}

    # Average match score
    avg_score = db.session.query(
        func.avg(Candidate.match_score)
    ).filter(
        Candidate.criteria_id.in_(user_criteria_ids)
    ).scalar() or 0

    # Category breakdown — grouped by the position (criteria) the resume was
    # uploaded for, so old ML-predicted categories never leak into the stats
    category_counts = db.session.query(
        HiringCriteria.role_title, func.count(Candidate.id)
    ).select_from(Candidate).join(
        HiringCriteria, Candidate.criteria_id == HiringCriteria.id
    ).filter(
        Candidate.criteria_id.in_(user_criteria_ids)
    ).group_by(HiringCriteria.role_title).all()

    category_dict = {cat: count for cat, count in category_counts if cat}

    return jsonify({
        'total_candidates': total,
        'total_criteria': len(user_criteria_ids),
        'shortlisted': status_dict.get('AI Shortlisted', 0) + status_dict.get('Manually Shortlisted', 0),
        'rejected': status_dict.get('Rejected', 0),
        'selected': status_dict.get('Selected', 0),
        'on_hold': status_dict.get('On Hold', 0),
        'pending': status_dict.get('Pending', 0),
        'avg_match_score': round(float(avg_score), 1),
        'category_breakdown': category_dict,
        'status_breakdown': status_dict
    }), 200


@dashboard_bp.route('/recent', methods=['GET'])
def get_recent():
    current_user = get_default_user()
    """Get recent candidate uploads."""
    user_criteria_ids = [c.id for c in HiringCriteria.query.filter_by(
        created_by=current_user.id).all()]

    if not user_criteria_ids:
        return jsonify({'candidates': []}), 200

    recent = Candidate.query.filter(
        Candidate.criteria_id.in_(user_criteria_ids)
    ).order_by(Candidate.created_at.desc()).limit(10).all()

    return jsonify({
        'candidates': [c.to_dict() for c in recent]
    }), 200
