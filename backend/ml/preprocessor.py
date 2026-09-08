"""
Text preprocessing module for resume text cleaning and normalization.
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data on import
_nltk_downloaded = False


def ensure_nltk_data():
    global _nltk_downloaded
    if _nltk_downloaded:
        return
    for resource in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if 'punkt' in resource else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
    _nltk_downloaded = True


ensure_nltk_data()

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Additional domain-specific stopwords to keep
DOMAIN_KEEP_WORDS = {
    'python', 'java', 'c', 'r', 'sql', 'aws', 'api', 'ui', 'ml', 'ai',
    'nlp', 'ci', 'cd', 'devops', 'linux', 'git', 'html', 'css', 'js'
}


def clean_text(text):
    """Clean and normalize resume text."""
    if not text or not isinstance(text, str):
        return ''

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove email addresses (keep for extraction, remove from classification text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # Remove phone numbers
    text = re.sub(r'\+?\d[\d\s\-()]{7,}\d', '', text)

    # Remove special characters but keep meaningful punctuation
    text = re.sub(r'[^a-z0-9\s.,;#/+\-]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def tokenize(text):
    """Tokenize text into words."""
    try:
        tokens = word_tokenize(text)
    except LookupError:
        tokens = text.split()
    return tokens


def remove_stopwords(tokens):
    """Remove stopwords but keep domain-specific terms."""
    return [t for t in tokens if t not in stop_words or t in DOMAIN_KEEP_WORDS]


def lemmatize(tokens):
    """Lemmatize tokens to their base form."""
    return [lemmatizer.lemmatize(t) for t in tokens]


def preprocess_text(text):
    """Full preprocessing pipeline: clean -> tokenize -> remove stopwords -> lemmatize."""
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    return ' '.join(tokens)


def extract_emails(text):
    """Extract email addresses from text.

    PDF extraction frequently breaks emails across lines, e.g.
    'user.name@gmail.c\nom' or 'Email: user.name\n@gmail.com', so we also
    search a copy of the text where those broken addresses are rejoined.
    """
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)

    joined = text
    # A: local part on one line, '@domain' starting the next line
    joined = re.sub(r'(?<=[a-zA-Z0-9._%+\-])[ \t]*\n[ \t]*(?=@)', '', joined)
    # B: domain with a dot but a very short TLD fragment before the line break
    #    (e.g. 'user@gmail.c' + 'om ...' — but NOT a complete 'user@gmail.com')
    joined = re.sub(r'([a-zA-Z0-9._%+\-]@[a-zA-Z0-9.\-]*\.[a-zA-Z]{0,2})[ \t]*\n[ \t]*([a-zA-Z])', r'\1\2', joined)
    # C: domain without any dot yet on the first line (e.g. 'user@gmail' + '.com')
    joined = re.sub(r'([a-zA-Z0-9._%+\-]@[a-zA-Z0-9\-]*)[ \t]*\n[ \t]*([a-zA-Z.])', r'\1\2', joined)

    if joined != text:
        for email in re.findall(pattern, joined):
            if email not in emails:
                emails.append(email)

    return emails


# Lines that talk about IDs/dates rather than contact phones
_PHONE_CONTEXT_SKIP = re.compile(
    r'\b(?:c\s*\.?\s*n\s*\.?\s*i\s*\.?\s*c|cnic|ssn|id\s*(?:no|number|card)?|'
    r'date\s*of\s*birth|dob|reg(?:istration)?\s*(?:no|number)?)\b',
    re.IGNORECASE
)


def _is_valid_phone(candidate):
    """Filter out dates, year ranges and IDs captured by the phone pattern."""
    digits = re.sub(r'\D', '', candidate)
    # Real phone numbers (with country code) have 9-13 digits;
    # dates like '15-01-2006' and year ranges like '2023 - 2027' have 8.
    if not (9 <= len(digits) <= 13):
        return False
    # Anything containing a 4-digit group that looks like a year is a date/range
    for group in re.findall(r'\d{4}', candidate):
        if 1900 <= int(group) <= 2035:
            return False
    return True


def extract_phones(text):
    """Extract phone numbers, skipping ID numbers, dates and year ranges."""
    pattern = r'[(]?\+?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'

    def scan(lines):
        found = []
        for line in lines:
            line = line.strip()
            if not line or _PHONE_CONTEXT_SKIP.search(line):
                continue
            for m in re.finditer(pattern, line):
                candidate = m.group().strip()
                if _is_valid_phone(candidate):
                    found.append(candidate)
        return found

    phones = scan(text.split('\n'))
    if phones:
        return phones

    # Phone may be wrapped across lines ('0318-\n4783092'); rejoin and retry
    joined = re.sub(r'(?<=[0-9+\-()])[ \t]*\n[ \t]*(?=[0-9+\-()])', '', text)
    return scan(joined.split('\n'))


# Headings that commonly sit at the very top of a resume instead of the name
_NON_NAME_HEADINGS = {
    'about me', 'about', 'curriculum vitae', 'cv', 'resume', 'profile',
    'objective', 'career objective', 'professional summary', 'summary',
    'contact', 'contact info', 'contact information', 'personal information',
    'personal details', 'personal profile', 'education', 'experience',
    'work experience', 'skills', 'key skills', 'technical skills', 'academics',
}

# Words that disqualify a line from being a person's name
_NON_NAME_WORDS = {
    'gmail', 'yahoo', 'hotmail', 'outlook', 'mail', 'com', 'www', 'http',
    'https', 'skill', 'skills', 'objective', 'profile', 'summary',
    'curriculum', 'vitae', 'resume', 'about', 'me',
}


def _clean_name_candidate(line):
    """Reduce a line to a plausible person name, or '' if it isn't one."""
    # Names don't contain digits — cut at the first digit
    candidate = re.split(r'\d', line)[0]
    # Drop parenthesized degrees/titles, emails, URLs and contact keywords
    candidate = re.sub(r'\([^)]*\)', ' ', candidate)
    candidate = re.sub(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', ' ', candidate)
    candidate = re.sub(r'(?:https?://|www\.)\S+', ' ', candidate)
    candidate = re.split(r'\b(?:e-?mail|mobile|phone|tel|contact|cell)\b',
                         candidate, flags=re.IGNORECASE)[0]
    candidate = re.sub(r"[^A-Za-z.'\- ]", ' ', candidate)
    candidate = re.sub(r'\s+', ' ', candidate).strip(" .-'")

    words = candidate.split()
    if not (1 <= len(words) <= 4):
        return ''
    for w in words:
        if len(w) > 25 or not re.fullmatch(r"[A-Za-z][A-Za-z'\-]*\.?", w):
            return ''
        if w.lower().strip(".'-") in _NON_NAME_WORDS:
            return ''
    # Reject lines made only of initials like 'M . Saleem' fragments
    if not any(len(w.strip(".'-")) > 2 for w in words):
        return ''
    # Normalize ALL-CAPS PDF rendering of names
    return ' '.join(w.capitalize() if w.isupper() else w for w in words)


def extract_names(text, file_path=None):
    """Extract the candidate name from resume text.

    Tries, in order: an explicit 'Name:' label, a small-caps PDF name split
    across two lines, the first name-like line near the top, and finally a
    name derived from the resume filename.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return ''

    # 1) Explicit label, e.g. 'Full Name : Haseeb ...'
    for line in lines[:40]:
        if re.search(r'father|mother|guardian|reference', line, re.IGNORECASE):
            continue
        m = re.search(r'\b(?:full\s+name|name)\b\s*[:\-]\s*([^\n]+)', line, re.IGNORECASE)
        if m:
            name = _clean_name_candidate(m.group(1))
            if name:
                return name

    # 2) Small-caps PDF rendering splits the name, e.g. 'H' / 'ASEEB (BSCS)'
    if len(lines) > 1 and re.fullmatch(r'[A-Za-z]', lines[0]) \
            and lines[1].isupper() and len(lines[1]) <= 40:
        name = _clean_name_candidate(lines[0] + lines[1])
        if name:
            return name

    # 3) First name-like line near the top of the resume
    for line in lines[:6]:
        if line.lower().strip(' :') in _NON_NAME_HEADINGS:
            continue
        name = _clean_name_candidate(line)
        if name:
            return name

    # 4) Fall back to the resume filename, e.g. 'Haseeb_resume_1.pdf'
    if file_path:
        import os
        base = os.path.basename(file_path)
        base = re.sub(r'^[0-9a-f]{32}_', '', base)  # strip upload uuid prefix
        base = os.path.splitext(base)[0]
        base = re.sub(r'[_\-]+', ' ', base)
        words = [w for w in base.split()
                 if w and not w.isdigit()
                 and w.lower() not in _NON_NAME_WORDS
                 and w.lower() not in {'new', 'final', 'updated', 'copy',
                                       'version', 'application', 'letter',
                                       'software', 'engineer', 'developer'}]
        if words:
            return ' '.join(w.capitalize() for w in words)[:60]

    return ''


def extract_gender(text):
    """Extract gender from labels like 'Gender : Male'."""
    m = re.search(r'\bgender\s*[:\-]?\s*(male|female|other)\b', text, re.IGNORECASE)
    return m.group(1).capitalize() if m else ''


def extract_location(text):
    """Extract a location from labels like 'Domicile :', 'City:', 'Address:'."""
    m = re.search(r'\b(?:domicile|location|city|address)\s*[:\-]\s*([A-Za-z ,.\-]{3,80})',
                  text, re.IGNORECASE)
    if m:
        location = m.group(1).strip(' .,-')
        return location[:100]
    return ''


def extract_education(text):
    """Extract education-related information."""
    text_lower = text.lower()
    edu_keywords = [
        'bachelor', 'master', 'phd', 'b.sc', 'm.sc', 'b.tech', 'm.tech',
        'b.e', 'm.e', 'mba', 'bca', 'mca', 'diploma', 'degree',
        'university', 'college', 'institute', 'school'
    ]
    found = []
    for line in text.split('\n'):
        if any(kw in line.lower() for kw in edu_keywords):
            found.append(line.strip())
    return '\n'.join(found[:5])


def extract_experience_years(text):
    """Extract years of experience from text."""
    patterns = [
        r'(\d+)\s*(?:\+\s*)?years?\s*(?:of\s*)?(?:experience|exp)',
        r'experience\s*:?\s*(\d+)\s*(?:\+\s*)?years?',
        r'(\d+)\s*(?:\+\s*)?years?\s*(?:in|as)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0


def preprocess_for_classification(text):
    """Preprocess text specifically for ML classification."""
    return preprocess_text(text)
