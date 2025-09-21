from resume_parser import extract_text
def extract_skills_from_jd(jd_file, jd_filename):
    
    """
    Extracts a list of predefined skills from a Job Description file.
    """

    SKILL_KEYWORDS = ["Python", "Java", "C++", "SQL", "AWS", "TensorFlow", "React", "Node.js"]
    jd_text = extract_text(jd_file, jd_filename).lower()
    skills_found = [skill for skill in SKILL_KEYWORDS if skill.lower() in jd_text]
    return skills_found, jd_text