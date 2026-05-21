import re
from typing import Dict, List, Set

SKILL_TAXONOMY = {
    "programming_languages": ["python","java","javascript","typescript","c++","c#","golang","go","rust","ruby","php","swift","kotlin","scala","r","matlab","perl","bash","shell","powershell"],
    "web_frameworks": ["django","flask","fastapi","react","angular","vue","nextjs","express","spring","rails","laravel","asp.net","svelte"],
    "databases": ["sql","mysql","postgresql","postgres","mongodb","redis","elasticsearch","sqlite","oracle","cassandra","dynamodb","neo4j","firebase"],
    "cloud_devops": ["aws","azure","gcp","google cloud","docker","kubernetes","k8s","terraform","ansible","jenkins","ci/cd","git","github","gitlab","bitbucket","linux","nginx","apache"],
    "data_ml": ["machine learning","deep learning","nlp","natural language processing","computer vision","tensorflow","pytorch","keras","scikit-learn","sklearn","pandas","numpy","scipy","matplotlib","seaborn","xgboost","lightgbm","spark","hadoop","airflow","dbt","tableau","power bi","looker"],
    "soft_skills": ["leadership","communication","teamwork","problem solving","critical thinking","project management","agile","scrum","kanban","time management","collaboration","mentoring"],
    "other_tech": ["rest api","graphql","microservices","grpc","kafka","rabbitmq","celery","websocket","oauth","jwt","html","css","sass","tailwind","bootstrap"],
}

_FLAT = {skill: cat for cat, skills in SKILL_TAXONOMY.items() for skill in skills}

class SkillExtractor:
    def __init__(self):
        self._patterns = {skill: re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE) for skill in _FLAT}

    def extract_skills(self, text):
        found = {cat: set() for cat in SKILL_TAXONOMY}
        for skill, pattern in self._patterns.items():
            if pattern.search(text):
                found[_FLAT[skill]].add(skill)
        return {cat: sorted(skills) for cat, skills in found.items() if skills}

    def extract_skill_list(self, text):
        result = []
        for skills in self.extract_skills(text).values():
            result.extend(skills)
        return sorted(set(result))

    def skill_overlap(self, resume_text, job_text):
        resume_skills = set(self.extract_skill_list(resume_text))
        job_skills = set(self.extract_skill_list(job_text))
        matched = resume_skills & job_skills
        missing = job_skills - resume_skills
        ratio = len(matched) / len(job_skills) if job_skills else 0.0
        return {"matched_skills": sorted(matched), "missing_skills": sorted(missing), "total_job_skills": len(job_skills), "matched_count": len(matched), "skill_match_ratio": round(ratio, 4)}
