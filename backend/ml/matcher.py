"""
Resume-to-hiring-criteria matcher.
Calculates match score between a candidate resume and hiring criteria.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Comprehensive skills dictionary for matching
SKILLS_DICTIONARY = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'kotlin', 'swift', 'scala', 'r', 'php', 'perl', 'dart', 'html', 'css', 'sql',
    'react', 'angular', 'vue.js', 'vue', 'next.js', 'nextjs', 'svelte', 'node.js', 'nodejs',
    'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'laravel',
    'rails', 'asp.net', '.net',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'xgboost',
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'power bi', 'tableau',
    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'google cloud',
    'jenkins', 'ci/cd', 'terraform', 'ansible', 'nginx', 'apache',
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'oracle',
    'git', 'github', 'gitlab', 'bitbucket',
    'rest api', 'graphql', 'grpc', 'websocket', 'microservices',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    'data science', 'data analysis', 'data engineering', 'etl',
    'agile', 'scrum', 'kanban', 'jira',
    'linux', 'bash', 'shell', 'powershell',
    'android', 'ios', 'react native', 'flutter',
    'figma', 'adobe', 'sketch', 'ui/ux', 'ux design',
    'hadoop', 'spark', 'kafka', 'airflow',
    'blockchain', 'ethereum', 'solidity',
    'cybersecurity', 'penetration testing', 'network security',
    'devops', 'sre', 'monitoring', 'grafana', 'prometheus',
    'oop', 'design patterns', 'system design', 'algorithms', 'data structures',
    'firebase', 'supabase', 'heroku', 'vercel', 'netlify',
    'tailwind', 'bootstrap', 'sass', 'webpack', 'vite',
    'unit testing', 'jest', 'pytest', 'selenium', 'cypress',
    'recruitment', 'hr', 'talent acquisition', 'payroll', 'workday',
    'financial analysis', 'accounting', 'auditing', 'tax', 'gaap', 'sap', 'quickbooks',
    'excel', 'word', 'powerpoint',
}


def extract_skills_from_text(text):
    """Extract skills mentioned in text by matching against skills dictionary."""
    if not text:
        return set()

    text_lower = text.lower()
    found_skills = set()

    for skill in SKILLS_DICTIONARY:
        # Match whole word or phrase
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    return found_skills


def skill_match_score(candidate_skills, required_skills):
    """
    Calculate skill match using Jaccard-like similarity.
    Returns: (score 0-100, matched_skills, missing_skills)
    """
    if not required_skills:
        return 100.0, list(candidate_skills), []

    candidate_set = {s.lower().strip() for s in candidate_skills if s}
    required_set = {s.lower().strip() for s in required_skills if s}

    if not required_set:
        return 100.0, list(candidate_set), []

    matched = candidate_set & required_set
    missing = required_set - candidate_set

    # Weighted: coverage of required skills is more important
    coverage = len(matched) / len(required_set) if required_set else 1.0
    score = coverage * 100

    return round(score, 2), sorted(matched), sorted(missing)


def text_similarity_score(resume_text, criteria_text):
    """Calculate TF-IDF cosine similarity between resume and criteria text."""
    if not resume_text or not criteria_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    try:
        vectors = vectorizer.fit_transform([resume_text, criteria_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return round(float(similarity) * 100, 2)
    except ValueError:
        return 0.0


def category_match_score(predicted_category, role_title):
    """Score based on how well predicted category matches the role."""
    if not predicted_category or not role_title:
        return 50.0

    pred_lower = predicted_category.lower()
    role_lower = role_title.lower()

    # Direct match
    if pred_lower == role_lower:
        return 100.0

    # Partial keyword overlap
    pred_words = set(pred_lower.split())
    role_words = set(role_lower.split())
    overlap = pred_words & role_words

    if overlap:
        return round(len(overlap) / max(len(role_words), 1) * 100, 2)

    # Related categories mapping
    related = {
        'data science': ['machine learning', 'python development'],
        'machine learning': ['data science', 'python development', 'software engineering'],
        'web development': ['software engineering', 'python development', 'java development'],
        'software engineering': ['web development', 'java development', 'python development'],
        'python development': ['data science', 'machine learning', 'web development'],
        'java development': ['software engineering', 'web development'],
        'android development': ['java development', 'software engineering'],
        'devops': ['software engineering', 'cybersecurity'],
        'cybersecurity': ['devops', 'database administration'],
        'database administration': ['data science', 'devops'],
        'hr': ['finance'],
        'finance': ['hr'],
    }

    for key, related_cats in related.items():
        if key in role_lower and pred_lower in related_cats:
            return 60.0

    return 20.0


def experience_score(candidate_exp_years, required_exp):
    """Score experience match."""
    if not required_exp:
        return 80.0

    try:
        req_years = int(re.search(r'\d+', required_exp).group())
    except (AttributeError, ValueError):
        return 70.0

    if candidate_exp_years >= req_years:
        return 100.0
    elif candidate_exp_years >= req_years - 1:
        return 80.0
    elif candidate_exp_years >= req_years - 2:
        return 60.0
    else:
        return max(0, 40 - (req_years - candidate_exp_years) * 10)


def calculate_match(resume_text, candidate_skills_str, predicted_category,
                    experience_years, criteria):
    """
    Calculate overall match score between resume and hiring criteria.

    Args:
        resume_text: Full resume text
        candidate_skills_str: Comma-separated skills string
        predicted_category: ML-predicted resume category
        experience_years: Years of experience (int)
        criteria: dict with role_title, required_skills, required_experience

    Returns:
        dict with match_score, matched_skills, missing_skills, breakdown
    """
    # Extract candidate skills
    candidate_skills = set()
    if candidate_skills_str:
        candidate_skills.update(s.strip().lower() for s in candidate_skills_str.split(','))
    candidate_skills.update(extract_skills_from_text(resume_text))

    # Parse required skills
    required_skills = []
    if criteria.get('required_skills'):
        required_skills = [s.strip().lower() for s in criteria['required_skills'].split(',') if s.strip()]

    # Calculate component scores
    skill_score, matched, missing = skill_match_score(candidate_skills, required_skills)
    criteria_text = criteria.get('role_title', '') + ' ' + criteria.get('required_skills', '') + ' ' + criteria.get('job_description', '')
    text_sim = text_similarity_score(resume_text, criteria_text)
    cat_score = category_match_score(predicted_category, criteria.get('role_title', ''))
    exp_score = experience_score(experience_years, criteria.get('required_experience', ''))

    # Weighted combination
    overall = (
        skill_score * 0.35 +
        text_sim * 0.25 +
        cat_score * 0.20 +
        exp_score * 0.20
    )

    return {
        'match_score': round(overall, 2),
        'matched_skills': ', '.join(matched),
        'missing_skills': ', '.join(missing),
        'breakdown': {
            'skill_match': skill_score,
            'text_similarity': text_sim,
            'category_match': cat_score,
            'experience_match': exp_score
        }
    }
