"""
Candidate routes - upload resumes, list, view, blind view, update status.
"""
import os
import re
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, Candidate, HiringCriteria
from routes.auth import get_default_user
from ml.resume_parser import parse_resume
from ml.matcher import calculate_match
from ml.preprocessor import extract_experience_years

candidates_bp = Blueprint('candidates', __name__)


_YEAR_RANGE = re.compile(r'^\d{4}\s*[-\u2013]\s*\d{4}$')


def _reparse_candidate(candidate):
    """Re-parse the stored resume file and refresh extracted fields.

    Only overwrites fields that are empty or clearly invalid (e.g. a name
    fragment like 'H' or a phone that is really a year range), so manual
    edits made from the UI are preserved.

    Returns (ok, updated_fields).
    """
    if not candidate.resume_file_path or not os.path.exists(candidate.resume_file_path):
        return False, 'Resume file not found on server'

    try:
        parsed = parse_resume(candidate.resume_file_path)
    except Exception as e:
        return False, f'Error parsing resume: {str(e)}'

    if not parsed.get('resume_text'):
        return False, 'Could not extract text from resume'

    updated = []

    # A name like 'H' is a parsing fragment; 'Haseeb (bscs)' carries a
    # parenthesized degree suffix that belongs in the degree field, not the name
    bad_name = (
        not candidate.name
        or len(candidate.name.strip()) <= 2
        or bool(re.search(r'\([^)]*\)', candidate.name))
    )
    if parsed.get('name') and bad_name:
        candidate.name = parsed['name']
        updated.append('name')

    if parsed.get('email') and not candidate.email:
        candidate.email = parsed['email']
        updated.append('email')

    bad_phone = not candidate.phone or bool(_YEAR_RANGE.match(candidate.phone.strip()))
    if parsed.get('phone') and bad_phone:
        candidate.phone = parsed['phone']
        updated.append('phone')
    elif candidate.phone and _YEAR_RANGE.match(candidate.phone.strip()) and not parsed.get('phone'):
        # No real phone found — clear the year range so it stops posing as one
        candidate.phone = ''
        updated.append('phone')

    if parsed.get('gender') and not candidate.gender:
        candidate.gender = parsed['gender']
        updated.append('gender')

    if parsed.get('location') and not candidate.location:
        candidate.location = parsed['location']
        updated.append('location')

    for field in ('skills', 'institute', 'degree', 'projects', 'certifications'):
        if parsed.get(field) and not getattr(candidate, field):
            setattr(candidate, field, parsed[field])
            updated.append(field)

    # Keep the stored category in sync with the position the resume was
    # uploaded for (older records hold ML-predicted categories instead)
    if candidate.criteria and candidate.resume_category != candidate.criteria.role_title:
        candidate.resume_category = candidate.criteria.role_title
        updated.append('resume_category')

    return True, updated


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@candidates_bp.route('/upload', methods=['POST'])
def upload_resumes():
    current_user = get_default_user()
    """Upload one or more resume files with a hiring criteria ID."""
    criteria_id = request.form.get('criteria_id')
    if not criteria_id:
        return jsonify({'error': 'criteria_id is required'}), 400

    criteria = HiringCriteria.query.get_or_404(int(criteria_id))

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    results = []
    errors = []

    for file in files:
        if file.filename == '':
            continue

        if not allowed_file(file.filename):
            errors.append(f"Unsupported format: {file.filename}")
            continue

        try:
            # Save file
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Parse resume
            parsed = parse_resume(file_path)
            resume_text = parsed.get('resume_text', '')

            if not resume_text:
                errors.append(f"Could not extract text from: {file.filename}")
                continue

            # Store criteria role title as category (more meaningful than ML prediction)
            category = criteria.role_title

            # Extract experience years
            exp_years = parsed.get('experience_years', 0)
            if not exp_years:
                exp_years = extract_experience_years(resume_text)

            # Calculate match score
            criteria_dict = {
                'role_title': criteria.role_title,
                'required_skills': criteria.required_skills,
                'required_experience': criteria.required_experience,
                'job_description': criteria.job_description or ''
            }

            match_result = calculate_match(
                resume_text=resume_text,
                candidate_skills_str=parsed.get('skills', ''),
                predicted_category=category,
                experience_years=exp_years,
                criteria=criteria_dict
            )

            # Determine AI status
            ai_status = 'AI Shortlisted' if match_result['match_score'] >= criteria.minimum_score else 'Not Shortlisted'

            # Create candidate record
            candidate = Candidate(
                criteria_id=criteria.id,
                name=parsed.get('name', ''),
                email=parsed.get('email', ''),
                phone=parsed.get('phone', ''),
                gender=parsed.get('gender', ''),
                institute=parsed.get('institute', ''),
                degree=parsed.get('degree', ''),
                skills=parsed.get('skills', ''),
                experience=f"{exp_years} years" if exp_years else '',
                projects=parsed.get('projects', ''),
                certifications=parsed.get('certifications', ''),
                location=parsed.get('location', ''),
                resume_category=category,
                resume_text=resume_text,
                resume_file_path=file_path,
                match_score=match_result['match_score'],
                matched_skills=match_result['matched_skills'],
                missing_skills=match_result['missing_skills'],
                ai_status=ai_status,
                final_status=ai_status
            )
            db.session.add(candidate)
            db.session.commit()

            results.append(candidate.to_dict())

        except Exception as e:
            errors.append(f"Error processing {file.filename}: {str(e)}")

    shortlisted = sum(1 for c in results if c.get('ai_status') == 'AI Shortlisted')

    return jsonify({
        'message': f'Processed {len(results)} resumes',
        'total_files': len(files),
        'processed': len(results),
        'shortlisted': shortlisted,
        'failed': len(errors),
        'candidates': results,
        'errors': errors
    }), 201


@candidates_bp.route('', methods=['GET'])
def list_candidates():
    current_user = get_default_user()
    """List all candidates with optional filters."""
    criteria_id = request.args.get('criteria_id')
    status = request.args.get('status')
    category = request.args.get('category')
    blind = request.args.get('blind', 'false').lower() == 'true'

    query = Candidate.query.join(HiringCriteria).filter(
        HiringCriteria.created_by == current_user.id
    )

    if criteria_id:
        query = query.filter(Candidate.criteria_id == int(criteria_id))
    if status:
        query = query.filter(Candidate.final_status == status)
    if category:
        query = query.filter(Candidate.resume_category == category)

    candidates = query.order_by(Candidate.match_score.desc()).all()

    return jsonify({
        'candidates': [c.to_dict(blind=blind) for c in candidates],
        'total': len(candidates)
    }), 200


@candidates_bp.route('/<int:candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    current_user = get_default_user()
    """Get full candidate details."""
    candidate = Candidate.query.get_or_404(candidate_id)
    blind = request.args.get('blind', 'false').lower() == 'true'

    return jsonify({'candidate': candidate.to_dict(blind=blind)}), 200


@candidates_bp.route('/<int:candidate_id>/blind', methods=['GET'])
def get_candidate_blind(candidate_id):
    current_user = get_default_user()
    """Get candidate with PII hidden for blind review."""
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.blind_reviewed = True
    db.session.commit()

    return jsonify({'candidate': candidate.to_dict(blind=True)}), 200


@candidates_bp.route('/<int:candidate_id>/status', methods=['PUT'])
def update_candidate_status(candidate_id):
    current_user = get_default_user()
    """Update candidate status (manual shortlist, reject, select, on-hold)."""
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json()

    new_status = data.get('status', '')

    # Normalize status input - accept both lowercase and formatted versions
    status_map = {
        'shortlisted': 'Manually Shortlisted',
        'manually shortlisted': 'Manually Shortlisted',
        'ai shortlisted': 'AI Shortlisted',
        'rejected': 'Rejected',
        'selected': 'Selected',
        'on_hold': 'On Hold',
        'on hold': 'On Hold',
    }
    normalized = status_map.get(new_status.lower().strip(), new_status)

    valid_statuses = ['AI Shortlisted', 'Manually Shortlisted', 'Rejected', 'Selected', 'On Hold']

    if normalized not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    new_status = normalized

    if new_status in ['Manually Shortlisted', 'Rejected', 'Selected', 'On Hold']:
        candidate.manual_status = new_status
    candidate.final_status = new_status

    db.session.commit()

    return jsonify({
        'message': 'Candidate status updated',
        'candidate': candidate.to_dict()
    }), 200


@candidates_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_candidates():
    """Delete multiple candidates by their IDs."""
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No candidate IDs provided'}), 400

    deleted = Candidate.query.filter(Candidate.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({
        'message': f'{deleted} candidate(s) deleted',
        'deleted': deleted
    }), 200


@candidates_bp.route('/all', methods=['DELETE'])
@candidates_bp.route('/all/<int:criteria_id>', methods=['DELETE'])
def delete_all_candidates(criteria_id=None):
    """Delete all candidates, optionally filtered by criteria."""
    if criteria_id:
        deleted = Candidate.query.filter_by(criteria_id=criteria_id).delete(synchronize_session=False)
    else:
        deleted = Candidate.query.delete(synchronize_session=False)
    db.session.commit()

    return jsonify({
        'message': f'{deleted} candidate(s) deleted',
        'deleted': deleted
    }), 200


@candidates_bp.route('/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    """Delete a single candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)
    # Also delete the uploaded file if it exists
    if candidate.resume_file_path and os.path.exists(candidate.resume_file_path):
        try:
            os.remove(candidate.resume_file_path)
        except OSError:
            pass
    db.session.delete(candidate)
    db.session.commit()

    return jsonify({'message': 'Candidate deleted'}), 200


@candidates_bp.route('/<int:candidate_id>', methods=['PUT'])
def update_candidate(candidate_id):
    """Update candidate fields (email, name, etc.)."""
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json() or {}

    # Allow updating specific fields
    updatable = ['email', 'name', 'phone', 'location', 'experience', 'skills', 'degree', 'institute']
    updated = []
    for field in updatable:
        if field in data:
            setattr(candidate, field, data[field])
            updated.append(field)

    db.session.commit()

    return jsonify({
        'message': f'Updated: {", ".join(updated) if updated else "nothing"}',
        'candidate': candidate.to_dict()
    }), 200


@candidates_bp.route('/reparse-all', methods=['POST'])
def reparse_all_candidates():
    """Re-extract resume data for every candidate to fix earlier parsing issues."""
    criteria_id = request.args.get('criteria_id', type=int)

    query = Candidate.query
    if criteria_id:
        query = query.filter_by(criteria_id=criteria_id)

    candidates = query.all()
    results = []
    updated_count = 0

    for candidate in candidates:
        ok, info = _reparse_candidate(candidate)
        if ok and info:
            updated_count += 1
            results.append({'id': candidate.id, 'ok': True, 'updated_fields': info})
        elif not ok:
            results.append({'id': candidate.id, 'ok': False, 'error': info})

    db.session.commit()

    return jsonify({
        'message': f'Re-parsed {len(candidates)} candidate(s), {updated_count} updated',
        'total': len(candidates),
        'updated': updated_count,
        'results': results
    }), 200


@candidates_bp.route('/<int:candidate_id>/reparse', methods=['POST'])
def reparse_candidate(candidate_id):
    """Re-extract resume data for a single candidate."""
    candidate = Candidate.query.get_or_404(candidate_id)

    ok, info = _reparse_candidate(candidate)
    db.session.commit()

    if not ok:
        return jsonify({'error': info}), 400

    return jsonify({
        'message': 'Candidate re-parsed',
        'updated_fields': info,
        'candidate': candidate.to_dict()
    }), 200


@candidates_bp.route('/ranking/<int:criteria_id>', methods=['GET'])
def get_ranking(criteria_id):
    current_user = get_default_user()
    """Get ranked candidate list for a hiring criteria, sorted by match score."""
    blind = request.args.get('blind', 'false').lower() == 'true'

    candidates = Candidate.query.filter_by(criteria_id=criteria_id)\
        .order_by(Candidate.match_score.desc()).all()

    ranked = []
    for i, c in enumerate(candidates, 1):
        data = c.to_dict(blind=blind)
        data['rank'] = i
        ranked.append(data)

    return jsonify({
        'ranking': ranked,
        'total': len(ranked)
    }), 200
