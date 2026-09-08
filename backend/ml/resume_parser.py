"""
Resume parser - extracts structured information from PDF and DOCX resumes.
"""
import os
import re

from ml.preprocessor import (
    extract_emails, extract_phones, extract_names, extract_experience_years,
    extract_gender, extract_location,
)


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        import pdfplumber
        text = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ''


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ''


def extract_text(file_path):
    """Extract text from PDF or DOCX based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def extract_skills(text):
    """Extract skills from resume text using keyword matching."""
    skills_keywords = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'kotlin', 'swift', 'scala', 'r', 'php', 'html', 'css', 'sql', 'nosql',
        'react', 'angular', 'vue', 'next.js', 'node.js', 'express', 'django', 'flask',
        'fastapi', 'spring', 'spring boot', 'laravel', 'rails',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'matplotlib', 'seaborn', 'tableau', 'power bi',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'ci/cd',
        'terraform', 'ansible', 'nginx', 'apache',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle',
        'git', 'github', 'gitlab',
        'rest api', 'graphql', 'grpc', 'microservices',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'data science', 'data analysis', 'data engineering', 'etl',
        'agile', 'scrum', 'kanban', 'jira',
        'linux', 'bash', 'shell',
        'android', 'ios', 'react native', 'flutter',
        'figma', 'adobe', 'ui/ux',
        'hadoop', 'spark', 'kafka', 'airflow',
        'cybersecurity', 'penetration testing', 'network security',
        'devops', 'monitoring', 'grafana', 'prometheus',
        'firebase', 'tailwind', 'bootstrap', 'webpack', 'vite',
        'unit testing', 'jest', 'pytest', 'selenium',
        'recruitment', 'hr', 'payroll', 'accounting', 'finance', 'excel', 'sap',
    ]

    text_lower = text.lower()
    found = []
    for skill in skills_keywords:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)

    return ', '.join(found)


def extract_education(text):
    """Extract degree/education info from resume text."""
    patterns = [
        r'(?:bachelor|master|phd|b\.sc|m\.sc|b\.tech|m\.tech|b\.e|m\.e|mba|bca|mca)[^\n]*',
        r'(?:degree|diploma|certification)[^\n]*in[^\n]*',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0).strip()[:200]
    return ''


def extract_institute(text):
    """Extract university/institute name from resume text."""
    patterns = [
        r'(?:university|college|institute|school)\s+of\s+[A-Za-z\s]+',
        r'[A-Za-z\s]+(?:university|college|institute)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()[:200]
    return ''


def extract_projects(text):
    """Extract project descriptions from resume text."""
    projects = []
    in_projects = False
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'project', line_stripped, re.IGNORECASE):
            in_projects = True
            continue
        if in_projects:
            if line_stripped and len(line_stripped) > 10:
                projects.append(line_stripped)
            elif not line_stripped and len(projects) > 0:
                break
    return '\n'.join(projects[:5]) if projects else ''


def extract_certifications(text):
    """Extract certifications from resume text."""
    certs = []
    in_certs = False
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'certification|certificate|license', line_stripped, re.IGNORECASE):
            in_certs = True
            continue
        if in_certs:
            if line_stripped and len(line_stripped) > 5:
                certs.append(line_stripped)
            elif not line_stripped and len(certs) > 0:
                break
    return '\n'.join(certs[:5]) if certs else ''


def parse_resume(file_path):
    """
    Parse a resume file and extract structured information.

    Returns dict with:
        name, email, phone, skills, education, institute,
        experience_years, projects, certifications, resume_text
    """
    resume_text = extract_text(file_path)

    if not resume_text:
        return {
            'name': '', 'email': '', 'phone': '', 'skills': '',
            'education': '', 'institute': '', 'experience_years': 0,
            'projects': '', 'certifications': '', 'resume_text': '',
            'gender': '', 'location': '', 'degree': ''
        }

    emails = extract_emails(resume_text)
    phones = extract_phones(resume_text)
    name = extract_names(resume_text, file_path)

    return {
        'name': name,
        'email': emails[0] if emails else '',
        'phone': phones[0] if phones else '',
        'skills': extract_skills(resume_text),
        'education': extract_education(resume_text),
        'institute': extract_institute(resume_text),
        'experience_years': extract_experience_years(resume_text),
        'projects': extract_projects(resume_text),
        'certifications': extract_certifications(resume_text),
        'resume_text': resume_text,
        'gender': extract_gender(resume_text),
        'location': extract_location(resume_text),
        'degree': extract_education(resume_text)
    }
