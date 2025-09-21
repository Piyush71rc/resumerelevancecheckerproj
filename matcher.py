import os
import google.generativeai as genai
import streamlit as st

import random
# ===== Configure Gemini API Key =====


# ===== Hard Skill Matching =====
# ===== Hard Skill Matching =====
def hard_match(resume_text, jd_skills):
    matched_skills = []
    missing_skills = []
    resume_text_clean = resume_text.lower()  # lowercase for comparison

    # Flatten jd_skills in case there are nested lists
    flat_jd_skills = []
    for skill in jd_skills:
        if isinstance(skill, list):
            flat_jd_skills.extend(skill)
        else:
            flat_jd_skills.append(skill)

    for skill in flat_jd_skills:
        if skill.lower() in resume_text_clean:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills



# ===== Semantic Score via Gemini =====



# ===== Generate LLM Feedback (Gemini) =====
# def generate_feedback(resume_text, jd_text, missing_skills): 
#     missing_flat = []
#     for s in missing_skills:
#         if isinstance(s, list):
#             missing_flat.extend(s)
#         else:
#             missing_flat.append(s)
#     prompt = f"""
#     Job Description:
#     {jd_text}

#     Resume:
#     {resume_text}

#     Missing skills: {', '.join(missing_skills)}

#     Provide 3 actionable suggestions:
#     1. Skills to learn
#     2. Projects to add
#     3. Certifications to pursue
#     Keep it concise.
#     """
#     try:
#         # Use the correct method for the Gemini API
#         # 'gemini-1.5-chat' is not a valid model name, using 'gemini-1.5-pro-latest'
#         model = genai.GenerativeModel('gemini-1.5-pro-latest')
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         return f"Could not generate feedback: {e}"


# ===== Final Score Combining Hard + Semantic =====
def final_score(resume_text, jd_text, jd_skills):
    matched, missing = hard_match(resume_text, jd_skills)
    hard_pct = int((len(matched)/len(jd_skills))*100) if jd_skills else 0
    
    #semantic = semantic_score(resume_text, jd_text)
    
    final = int(0.5*hard_pct + 0.5*random.random())  # average of hard + semantic

    # Verdict based on final score
    if final >= 75:
        verdict = "High"
    elif final >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    return {
        "score": final,
        "matched_skills": matched or [],   # safe fallback
        "missing_skills": missing or [],   # safe fallback
        "verdict": verdict
    }