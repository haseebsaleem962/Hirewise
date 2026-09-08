"""
Dataset downloader and synthetic dataset generator for resume classification.
Downloads from public sources or generates a high-quality synthetic dataset.
"""
import os
import csv
import random
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

CATEGORIES = [
    'Data Science', 'Machine Learning', 'Web Development', 'Software Engineering',
    'HR', 'Finance', 'DevOps', 'Cybersecurity', 'Android Development',
    'Java Development', 'Python Development', 'Database Administration'
]

# Skill sets per category for synthetic data generation
CATEGORY_SKILLS = {
    'Data Science': ['python', 'r', 'sql', 'pandas', 'numpy', 'matplotlib', 'tableau',
                     'statistics', 'data visualization', 'regression', 'classification',
                     'clustering', 'deep learning', 'tensorflow', 'power bi', 'etl'],
    'Machine Learning': ['python', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                         'neural networks', 'nlp', 'computer vision', 'reinforcement learning',
                         'feature engineering', 'model deployment', 'mlops', 'xgboost'],
    'Web Development': ['html', 'css', 'javascript', 'react', 'node.js', 'express',
                        'mongodb', 'rest api', 'typescript', 'next.js', 'vue.js',
                        'angular', 'tailwind', 'bootstrap', 'sass', 'webpack'],
    'Software Engineering': ['java', 'c++', 'python', 'design patterns', 'oop',
                             'agile', 'git', 'unit testing', 'system design',
                             'microservices', 'docker', 'algorithms', 'data structures'],
    'HR': ['recruitment', 'talent acquisition', 'employee relations', 'hr policies',
           'performance management', 'payroll', 'onboarding', 'training',
           'compensation', 'benefits', 'labor laws', 'hris', 'workday'],
    'Finance': ['financial analysis', 'accounting', 'excel', 'budgeting', 'forecasting',
                'financial modeling', 'auditing', 'tax', 'gaap', 'sap',
                'investment', 'risk management', 'portfolio management', 'quickbooks'],
    'DevOps': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'ci/cd', 'terraform',
               'ansible', 'linux', 'bash', 'monitoring', 'grafana', 'prometheus',
               'git', 'nginx', 'cloud formation'],
    'Cybersecurity': ['penetration testing', 'network security', 'firewall', 'siem',
                      'vulnerability assessment', 'incident response', 'forensics',
                      'encryption', 'risk assessment', 'compliance', 'iso 27001',
                      'ethical hacking', 'malware analysis'],
    'Android Development': ['java', 'kotlin', 'android sdk', 'jetpack compose', 'firebase',
                            'room database', 'retrofit', 'mvvm', 'gradle',
                            'material design', 'coroutines', 'rxjava'],
    'Java Development': ['java', 'spring boot', 'hibernate', 'maven', 'gradle',
                         'microservices', 'rest api', 'jpa', 'spring security',
                         'junit', 'kafka', 'redis', 'postgresql'],
    'Python Development': ['python', 'django', 'flask', 'fastapi', 'celery',
                           'sqlalchemy', 'pytest', 'docker', 'redis', 'postgresql',
                           'rest api', 'asyncio', 'pandas', 'numpy'],
    'Database Administration': ['sql', 'mysql', 'postgresql', 'oracle', 'mongodb',
                                'database design', 'indexing', 'replication',
                                'backup', 'performance tuning', 'etl', 'ssis',
                                'stored procedures', 'data modeling']
}

EDUCATION_KEYWORDS = [
    'bachelor', 'master', 'phd', 'b.sc', 'm.sc', 'b.tech', 'm.tech',
    'b.e', 'm.e', 'mba', 'bca', 'mca', 'diploma', 'certification'
]

EXPERIENCE_LEVELS = ['entry level', 'junior', 'mid-level', 'senior', 'lead', 'manager']


def generate_synthetic_resume(category, idx):
    """Generate a realistic synthetic resume text for a given category."""
    skills = CATEGORY_SKILLS.get(category, [])
    selected_skills = random.sample(skills, min(random.randint(5, 10), len(skills)))

    name = f"Candidate {idx}"
    email = f"candidate{idx}@example.com"

    edu = random.choice(EDUCATION_KEYWORDS)
    exp_years = random.randint(0, 15)
    exp_level = random.choice(EXPERIENCE_LEVELS)

    projects = [
        f"Built a {random.choice(['web application', 'data pipeline', 'mobile app', 'machine learning model', 'API service'])} using {', '.join(random.sample(selected_skills, min(3, len(selected_skills))))}",
        f"Developed {random.choice(['automation tools', 'analytics dashboard', 'e-commerce platform', 'chatbot', 'monitoring system'])} with {', '.join(random.sample(selected_skills, min(2, len(selected_skills))))}",
    ]

    certifications = random.sample([
        'AWS Certified', 'Google Cloud Certified', 'Microsoft Certified',
        'PMP', 'Scrum Master', 'Oracle Certified', 'Cisco Certified',
        'CompTIA Security+', 'TensorFlow Developer Certificate'
    ], random.randint(0, 3))

    resume_text = f"""
{name}
Email: {email}
Phone: +1-555-{random.randint(1000, 9999)}

OBJECTIVE
Seeking a {exp_level} position in {category} where I can apply my skills and contribute to impactful projects.

EDUCATION
{edu.title()} in Computer Science / Related Field
University of Technology, {random.randint(2010, 2024)}

EXPERIENCE
{exp_years} years of experience in {category.lower()}
{exp_level.title()} Professional with expertise in {', '.join(selected_skills[:4])}

SKILLS
{', '.join(selected_skills)}

PROJECTS
{chr(10).join(f'- {p}' for p in projects)}

CERTIFICATIONS
{chr(10).join(f'- {c}' for c in certifications) if certifications else 'None'}

ADDITIONAL INFORMATION
Strong problem-solving skills, team player, excellent communication abilities.
Passionate about {category.lower()} and continuous learning.
Available for immediate joining.
"""
    return resume_text.strip()


def generate_dataset(num_per_category=80, output_path=None):
    """Generate a synthetic resume dataset."""
    if output_path is None:
        output_path = os.path.join(DATA_DIR, 'resume_dataset.csv')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    rows = []
    idx = 1
    for category in CATEGORIES:
        for _ in range(num_per_category):
            resume_text = generate_synthetic_resume(category, idx)
            rows.append({'resume_text': resume_text, 'category': category})
            idx += 1

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic dataset: {len(df)} resumes across {len(CATEGORIES)} categories")
    print(f"Saved to: {output_path}")
    return df


def download_or_generate_dataset(output_path=None):
    """Try to download a real dataset, fall back to synthetic generation."""
    if output_path is None:
        output_path = os.path.join(DATA_DIR, 'resume_dataset.csv')

    if os.path.exists(output_path):
        print(f"Dataset already exists at: {output_path}")
        return pd.read_csv(output_path)

    # Try downloading from Hugging Face datasets (public resume datasets)
    try:
        print("Attempting to download dataset from Hugging Face...")
        from datasets import load_dataset
        ds = load_dataset("nickmachnik/resume-classification", split="train")
        df = pd.DataFrame(ds)
        if 'resume_text' not in df.columns and 'resume_str' in df.columns:
            df = df.rename(columns={'resume_str': 'resume_text'})
        if 'resume_text' not in df.columns and 'text' in df.columns:
            df = df.rename(columns={'text': 'resume_text'})
        df.to_csv(output_path, index=False)
        print(f"Downloaded dataset: {len(df)} resumes")
        return df
    except Exception as e:
        print(f"Hugging Face download failed: {e}")

    # Fallback to synthetic
    print("Falling back to synthetic dataset generation...")
    return generate_dataset(num_per_category=80, output_path=output_path)


if __name__ == '__main__':
    df = download_or_generate_dataset()
    print(f"\nDataset shape: {df.shape}")
    print(f"Categories: {df['category'].nunique()}")
    print(df['category'].value_counts())
