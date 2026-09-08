"""
Email routes - send emails to candidates and view email logs.
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, Candidate, HiringCriteria, EmailLog
from routes.auth import get_default_user
from services.email_service import send_candidate_email, send_custom_email

email_bp = Blueprint('email', __name__)


@email_bp.route('/send/<int:candidate_id>', methods=['POST'])
def send_email(candidate_id):
    current_user = get_default_user()
    """Send status email to a single candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json() or {}

    email_type = data.get('email_type', '')
    if not email_type:
        # Auto-detect from candidate status
        if candidate.final_status in ['AI Shortlisted', 'Manually Shortlisted', 'Selected']:
            email_type = 'shortlisted'
        elif candidate.final_status == 'Rejected':
            email_type = 'rejected'
        else:
            return jsonify({'error': 'Please specify email_type (shortlisted/rejected)'}), 400

    # Get role title for personalized email
    criteria = HiringCriteria.query.get(candidate.criteria_id)
    role_title = criteria.role_title if criteria else ''

    # Send email
    success, message = send_candidate_email(candidate, email_type, role_title)

    # Log the email
    email_log = EmailLog(
        candidate_id=candidate.id,
        email_type=email_type,
        email_status='sent' if success else 'failed'
    )
    db.session.add(email_log)
    db.session.commit()

    return jsonify({
        'message': message,
        'email_log': email_log.to_dict()
    }), 200 if success else 500


@email_bp.route('/bulk/<int:criteria_id>', methods=['POST'])
def send_bulk_emails(criteria_id):
    current_user = get_default_user()
    """Send emails to candidates for a hiring criteria.

    Pass email_type ('shortlisted' or 'rejected') to target only that group;
    when omitted, the type is auto-detected from each candidate's status.
    """
    criteria = HiringCriteria.query.get_or_404(criteria_id)
    data = request.get_json() or {}
    email_type = (data.get('email_type') or '').strip().lower()

    role_title = criteria.role_title

    query = Candidate.query.filter_by(criteria_id=criteria_id)

    if email_type == 'shortlisted':
        candidates = query.filter(Candidate.final_status.in_(
            ['AI Shortlisted', 'Manually Shortlisted', 'Selected'])).all()
    elif email_type == 'rejected':
        candidates = query.filter(Candidate.final_status == 'Rejected').all()
    else:
        candidates = query.filter(Candidate.final_status.in_(
            ['AI Shortlisted', 'Manually Shortlisted', 'Selected', 'Rejected'])).all()

    results = []
    for candidate in candidates:
        if not candidate.email:
            results.append({
                'candidate_id': candidate.id,
                'candidate_name': candidate.name,
                'email_type': 'skipped',
                'status': 'skipped (no email address)'
            })
            continue

        if email_type in ('shortlisted', 'rejected'):
            mail_type = email_type
        elif candidate.final_status in ['AI Shortlisted', 'Manually Shortlisted', 'Selected']:
            mail_type = 'shortlisted'
        else:
            mail_type = 'rejected'

        success, message = send_candidate_email(candidate, mail_type, role_title)

        email_log = EmailLog(
            candidate_id=candidate.id,
            email_type=mail_type,
            email_status='sent' if success else 'failed'
        )
        db.session.add(email_log)

        results.append({
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'email_type': mail_type,
            'status': 'sent' if success else 'failed'
        })

    db.session.commit()

    sent = sum(1 for r in results if r['status'] == 'sent')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = len(results) - sent - failed

    return jsonify({
        'message': f'Sent {sent} emails, {failed} failed, {skipped} skipped',
        'results': results
    }), 200


@email_bp.route('/logs', methods=['GET'])
def get_email_logs():
    current_user = get_default_user()
    """Get email sending history."""
    user_criteria_ids = [c.id for c in HiringCriteria.query.filter_by(
        created_by=current_user.id).all()]

    if not user_criteria_ids:
        return jsonify({'logs': []}), 200

    logs = EmailLog.query.join(Candidate).filter(
        Candidate.criteria_id.in_(user_criteria_ids)
    ).order_by(EmailLog.sent_at.desc()).all()

    return jsonify({
        'logs': [log.to_dict() for log in logs]
    }), 200


@email_bp.route('/test', methods=['POST'])
def test_email():
    """Test SMTP connection to verify email configuration."""
    import smtplib
    data = request.get_json() or {}
    test_email_addr = data.get('email', current_app.config.get('SMTP_USER', ''))

    if not test_email_addr:
        return jsonify({'error': 'No test email address provided'}), 400

    smtp_host = current_app.config.get('SMTP_HOST', '')
    smtp_port = current_app.config.get('SMTP_PORT', 587)
    smtp_user = current_app.config.get('SMTP_USER', '')
    smtp_pass = current_app.config.get('SMTP_PASS', '')

    if not smtp_user or not smtp_pass:
        return jsonify({'error': 'SMTP not configured. Add SMTP_USER and SMTP_PASS to your .env file'}), 400

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
        return jsonify({
            'success': True,
            'message': f'SMTP connection successful! Emails will send from {smtp_user}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'SMTP connection failed: {str(e)}'
        }), 400


@email_bp.route('/send-custom/<int:candidate_id>', methods=['POST'])
def send_custom(candidate_id):
    """Send a custom email to a single candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json() or {}

    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not subject or not body:
        return jsonify({'error': 'Both subject and body are required'}), 400

    criteria = HiringCriteria.query.get(candidate.criteria_id)
    role_title = criteria.role_title if criteria else ''

    success, message = send_custom_email(candidate, subject, body, role_title)

    email_log = EmailLog(
        candidate_id=candidate.id,
        email_type='custom',
        email_status='sent' if success else 'failed'
    )
    db.session.add(email_log)
    db.session.commit()

    return jsonify({
        'message': message,
        'email_log': email_log.to_dict()
    }), 200 if success else 500


@email_bp.route('/bulk-custom/<int:criteria_id>', methods=['POST'])
def send_bulk_custom(criteria_id):
    """Send custom email to all candidates for a criteria."""
    criteria = HiringCriteria.query.get_or_404(criteria_id)
    data = request.get_json() or {}

    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    candidate_ids = data.get('candidate_ids', [])

    if not subject or not body:
        return jsonify({'error': 'Both subject and body are required'}), 400

    if candidate_ids:
        candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    else:
        candidates = Candidate.query.filter_by(criteria_id=criteria_id).filter(
            Candidate.email != '', Candidate.email.isnot(None)
        ).all()

    role_title = criteria.role_title
    results = []
    for candidate in candidates:
        success, message = send_custom_email(candidate, subject, body, role_title)
        email_log = EmailLog(
            candidate_id=candidate.id,
            email_type='custom',
            email_status='sent' if success else 'failed'
        )
        db.session.add(email_log)
        results.append({
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'email': candidate.email,
            'status': 'sent' if success else 'failed'
        })

    db.session.commit()
    sent = sum(1 for r in results if r['status'] == 'sent')
    failed = sum(1 for r in results if r['status'] == 'failed')

    return jsonify({
        'message': f'Sent {sent} custom emails, {failed} failed',
        'results': results
    }), 200


@email_bp.route('/config-status', methods=['GET'])
def email_config_status():
    """Check if SMTP is configured."""
    smtp_user = current_app.config.get('SMTP_USER', '')
    smtp_sender = current_app.config.get('SMTP_SENDER', '')
    configured = bool(smtp_user and current_app.config.get('SMTP_PASS', ''))
    return jsonify({
        'configured': configured,
        'smtp_host': current_app.config.get('SMTP_HOST', ''),
        'smtp_user': smtp_user,
        'smtp_sender': smtp_sender or smtp_user,
    }), 200
