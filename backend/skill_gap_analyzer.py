import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
from pathlib import Path
import re

class SkillGapAnalyzer:
    def __init__(self, job_df=None, courses_df=None):
        self.job_df = self.prepare_job_df(job_df)
        self.courses_df = courses_df
        self.skill_mapping = self.load_skill_mapping()
        self.skill_keywords = self.load_skill_keywords()

    def prepare_job_df(self, job_df=None):
        """Load and normalize the job_title_des dataset."""
        if job_df is None:
            job_path = Path(__file__).parent / "data" / "job_title_des.csv"
            if not job_path.exists():
                return None
            job_df = pd.read_csv(job_path)

        job_df = job_df.copy()
        job_df.columns = [c.strip().lower() for c in job_df.columns]

        rename_map = {
            "job_title": "job_title",
            "job_description": "job_description",
            "job title": "job_title",
            "job description": "job_description"
        }
        job_df = job_df.rename(columns={
            column: rename_map.get(column, column)
            for column in job_df.columns
        })

        required_columns = {"job_title", "job_description"}
        if not required_columns.issubset(job_df.columns):
            return None

        return job_df.dropna(subset=["job_title", "job_description"])

    def load_skill_mapping(self):
        """Load skill to job mapping"""
        return {
            'python': ['Data Scientist', 'Software Engineer', 'ML Engineer', 'Backend Developer'],
            'javascript': ['Frontend Developer', 'Full Stack Developer', 'Web Developer'],
            'java': ['Software Engineer', 'Android Developer', 'Backend Developer'],
            'sql': ['Data Analyst', 'Database Administrator', 'Data Engineer'],
            'communication': ['Project Manager', 'Business Analyst', 'Product Manager'],
            'leadership': ['Team Lead', 'Project Manager', 'Engineering Manager'],
            'project_management': ['Project Manager', 'Product Manager', 'Scrum Master'],
            'data_analysis': ['Data Analyst', 'Data Scientist', 'Business Analyst'],
            'ui_ux': ['UI/UX Designer', 'Product Designer', 'Frontend Developer'],
            'marketing': ['Marketing Manager', 'Product Manager', 'Business Development']
        }

    def load_skill_keywords(self):
        """Keywords used to extract skill requirements from job descriptions."""
        return {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', ' js ', 'react', 'angular', 'vue', 'node', 'node.js'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'database', 'dbms'],
            'html': ['html', 'html5'],
            'css': ['css', 'css3', 'sass', 'bootstrap', 'tailwind'],
            'react': ['react', 'redux', 'next.js'],
            'flutter': ['flutter'],
            'dart': ['dart'],
            'android': ['android', 'kotlin'],
            'ios': ['ios', 'swift'],
            'mobile_development': ['mobile app', 'mobile application', 'cross platform', 'app development'],
            'git': ['git', 'github', 'gitlab', 'version control'],
            'machine_learning': ['machine learning', 'ml ', 'deep learning', 'tensorflow', 'pytorch', 'keras'],
            'data_analysis': ['data analysis', 'analytics', 'statistics', 'excel', 'power bi', 'tableau'],
            'statistics': ['statistics', 'statistical', 'probability', 'hypothesis testing'],
            'excel': ['excel', 'spreadsheet', 'pivot table'],
            'communication': ['communication', 'presentation', 'stakeholder', 'verbal', 'written'],
            'leadership': ['leadership', 'team lead', 'management', 'mentor', 'supervise'],
            'project_management': ['project management', 'agile', 'scrum', 'kanban', 'jira'],
            'problem_solving': ['problem solving', 'troubleshoot', 'analytical', 'debug'],
            'ui_ux': ['ui', 'ux', 'figma', 'sketch', 'user experience', 'wireframe'],
            'marketing': ['marketing', 'seo', 'content', 'social media', 'campaign'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'aws', 'azure'],
            'testing': ['testing', 'qa', 'selenium', 'unit testing', 'automation testing']
        }

    def analyze_skill_gaps(self, user_skills, target_job_title):
        """Analyze skill gaps for a specific job"""
        user_skills = self.normalize_user_skills(user_skills)

        if self.job_df is None or self.job_df.empty:
            return self.mock_gap_analysis(user_skills, target_job_title)

        job_requirements = self.extract_job_requirements(target_job_title)

        gaps = []
        for skill, required_level in job_requirements.items():
            user_level = self.normalize_user_level(user_skills.get(skill, 0))
            if user_level < required_level:
                gap_size = required_level - user_level
                gaps.append({
                    'skill': skill,
                    'current_level': user_level,
                    'required_level': required_level,
                    'gap_size': gap_size,
                    'priority': self.determine_priority(gap_size, skill),
                    'difficulty': self.assess_difficulty(skill)
                })

        return sorted(gaps, key=lambda x: (x['priority'] == 'high', x['gap_size']), reverse=True)

    def analyze_job_fit(self, target_job_title, user_skills=None):
        """Return a frontend-friendly skill gap analysis for a selected job."""
        user_skills = self.normalize_user_skills(user_skills or {})
        requirements = self.extract_job_requirements(target_job_title)
        gaps = self.analyze_skill_gaps(user_skills, target_job_title)

        matching_skills = []
        skill_details = []
        total_fit = 0

        for skill, required_level in requirements.items():
            user_level = self.normalize_user_level(user_skills.get(skill, 0))
            fit_ratio = 1 if required_level <= 0 else min(user_level / required_level, 1)
            total_fit += fit_ratio

            if user_level >= required_level:
                status = "matched"
            elif user_level > 0:
                status = "partial"
            else:
                status = "missing"

            if user_level > 0:
                matching_skills.append(self.format_skill_name(skill))

            skill_details.append({
                "skill": self.format_skill_name(skill),
                "current_level": user_level,
                "required_level": required_level,
                "completion": round(fit_ratio * 100),
                "status": status
            })

        skill_details = sorted(
            skill_details,
            key=lambda item: (
                {"matched": 0, "partial": 1, "missing": 2}.get(item["status"], 3),
                item["skill"]
            )
        )

        fully_matched_skills = [
            detail["skill"]
            for detail in skill_details
            if detail["status"] == "matched"
        ]

        partial_skills = [
            detail["skill"]
            for detail in skill_details
            if detail["status"] == "partial"
        ]

        missing_skills = [
            detail["skill"]
            for detail in skill_details
            if detail["status"] == "missing"
        ]

        skill_gaps = [self.format_skill_name(gap["skill"]) for gap in gaps]
        total_required = len(requirements) or 1
        match_percentage = round((total_fit / total_required) * 100)

        return {
            "job_title": target_job_title,
            "matching_skills": matching_skills,
            "fully_matched_skills": fully_matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "skill_gaps": skill_gaps,
            "match_percentage": match_percentage,
            "skill_details": skill_details,
            "required_skills": [
                {
                    "skill": self.format_skill_name(skill),
                    "level": level
                }
                for skill, level in requirements.items()
            ],
            "learning_path": [
                {
                    "skill": self.format_skill_name(gap["skill"]),
                    "description": f"Build {self.format_skill_name(gap['skill'])} from level {gap['current_level']} to {gap['required_level']} for this role.",
                    "current_level": gap["current_level"],
                    "required_level": gap["required_level"],
                    "priority": gap["priority"].title(),
                    "duration": self.estimate_learning_time(gap["gap_size"]),
                    "difficulty": gap["difficulty"].title()
                }
                for gap in gaps[:6]
            ]
        }

    def get_available_jobs(self, limit=200):
        """Return unique job titles from job_title_des.csv."""
        if self.job_df is None or self.job_df.empty:
            return []

        titles = (
            self.job_df["job_title"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        titles = titles[titles != ""].drop_duplicates().sort_values()
        return titles.head(limit).tolist()

    def extract_job_requirements(self, job_title):
        """Extract skill requirements from job descriptions"""
        title_requirements = self.get_title_based_requirements(job_title)
        requirements = title_requirements.copy()

        if self.job_df is None or self.job_df.empty:
            return requirements or self.get_default_requirements(job_title)

        normalized_job_title = str(job_title or "").lower().strip()
        title_series = self.job_df['job_title'].fillna("").astype(str).str.lower()
        job_matches = self.job_df[title_series.str.contains(normalized_job_title, na=False, regex=False)]

        if job_matches.empty:
            title_tokens = [
                token
                for token in re.findall(r"[a-z0-9]+", normalized_job_title)
                if len(token) > 2 and token not in {"and", "the", "for", "with"}
            ]
            if title_tokens:
                token_mask = title_series.apply(lambda value: all(token in value for token in title_tokens))
                job_matches = self.job_df[token_mask]

        if job_matches.empty:
            return requirements or self.get_default_requirements(job_title)

        job_text = " ".join(
            job_matches.head(5)["job_description"].fillna("").astype(str).str.lower().tolist()
        )

        for skill, keywords in self.skill_keywords.items():
            if title_requirements and skill not in title_requirements:
                continue

            matched_keywords = [
                keyword
                for keyword in keywords
                if self.keyword_in_text(keyword, job_text)
            ]
            if matched_keywords:
                skill_context = self.get_keyword_context(job_text, matched_keywords)
                inferred_level = self.infer_required_level(skill_context, matched_keywords)
                requirements[skill] = max(requirements.get(skill, 0), inferred_level)

        return requirements or self.get_default_requirements(job_title)

    def normalize_user_skills(self, user_skills):
        """Normalize API skill keys from labels, dropdown values, or older payloads."""
        normalized = {}

        for skill, level in (user_skills or {}).items():
            key = self.normalize_skill_key(skill)
            normalized[key] = self.normalize_user_level(level)

        return normalized

    def normalize_skill_key(self, skill):
        skill = str(skill or "").strip().lower()
        skill = re.sub(r"[^a-z0-9]+", "_", skill).strip("_")

        aliases = {
            "js": "javascript",
            "node_js": "javascript",
            "node": "javascript",
            "machine_learning_ml": "machine_learning",
            "ml": "machine_learning",
            "data_analytics": "data_analysis",
            "analytics": "data_analysis",
            "ui": "ui_ux",
            "ux": "ui_ux",
            "uiux": "ui_ux",
            "project_management": "project_management",
            "mobile": "mobile_development",
            "mobile_app_development": "mobile_development",
            "app_development": "mobile_development",
        }

        return aliases.get(skill, skill)

    def get_title_based_requirements(self, job_title):
        """Infer strong baseline skills from the role title before scanning noisy descriptions."""
        title = str(job_title or "").lower()
        role_rules = [
            (["flutter"], {"flutter": 3, "dart": 2, "mobile_development": 2, "android": 1, "ios": 1, "git": 1}),
            (["android"], {"android": 3, "java": 2, "mobile_development": 2, "git": 1}),
            (["ios"], {"ios": 3, "mobile_development": 2, "git": 1}),
            (["frontend", "front end", "react"], {"javascript": 3, "html": 3, "css": 3, "react": 2, "git": 1}),
            (["backend", "back end"], {"python": 2, "java": 2, "sql": 2, "git": 1}),
            (["full stack", "fullstack"], {"javascript": 3, "react": 2, "python": 2, "sql": 2, "git": 2}),
            (["data scientist"], {"python": 3, "sql": 2, "data_analysis": 3, "statistics": 2, "machine_learning": 2}),
            (["data analyst", "business analyst"], {"sql": 2, "excel": 2, "data_analysis": 2, "communication": 2}),
            (["machine learning", "ml engineer", "ai engineer"], {"python": 3, "machine_learning": 3, "statistics": 2, "sql": 1}),
            (["java"], {"java": 3, "sql": 2, "git": 2, "testing": 1}),
            (["project manager", "product manager"], {"communication": 3, "leadership": 2, "project_management": 3}),
            (["devops"], {"devops": 3, "git": 2, "testing": 1}),
            (["qa", "test"], {"testing": 3, "problem_solving": 2, "git": 1}),
            (["ui", "ux", "designer"], {"ui_ux": 3, "communication": 2}),
        ]

        requirements = {}
        for keywords, skills in role_rules:
            if any(keyword in title for keyword in keywords):
                for skill, level in skills.items():
                    requirements[skill] = max(requirements.get(skill, 0), level)

        return requirements

    def infer_required_level(self, job_desc, matched_keywords):
        """Infer 1-3 required level from seniority language and keyword density."""
        senior_terms = ['expert', 'senior', 'advanced', 'lead', 'architect', '5+ years', '6+ years', '7+ years']
        mid_terms = ['intermediate', 'mid-level', '3+ years', '4+ years', '2 years', '3 years']

        if any(term in job_desc for term in senior_terms):
            return 3
        if any(term in job_desc for term in mid_terms) or len(matched_keywords) >= 3:
            return 2
        return 1

    def keyword_in_text(self, keyword, text):
        """Match complete skill keywords so Java does not match JavaScript."""
        keyword = keyword.strip().lower()
        if not keyword:
            return False

        if re.search(r"[a-z0-9]", keyword):
            pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
        else:
            pattern = re.escape(keyword)

        return re.search(pattern, text) is not None

    def get_keyword_context(self, text, keywords, window=120):
        """Collect local text around matched skill keywords for level inference."""
        contexts = []

        for keyword in keywords:
            keyword = keyword.strip().lower()
            if re.search(r"[a-z0-9]", keyword):
                pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
            else:
                pattern = re.escape(keyword)

            for match in re.finditer(pattern, text):
                start = max(match.start() - window, 0)
                end = min(match.end() + window, len(text))
                contexts.append(text[start:end])

        return " ".join(contexts) or text

    def normalize_user_level(self, value):
        """Accept numeric levels or common quiz labels."""
        try:
            return min(max(float(value), 0), 3)
        except (TypeError, ValueError):
            pass

        if isinstance(value, str):
            level_map = {
                "beginner": 0,
                "poor": 0,
                "needs practice": 0,
                "intermediate": 1,
                "fair": 1,
                "basic answer": 1,
                "advanced": 2,
                "good": 2,
                "strong answer": 2,
                "expert": 3,
                "excellent": 3,
                "excellent star answer": 3
            }
            return level_map.get(value.strip().lower(), 0)

        return 0

    def format_skill_name(self, skill):
        display_names = {
            "ios": "iOS",
            "ui_ux": "UI/UX",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS",
        }
        return display_names.get(skill, skill.replace("_", " ").title())

    def get_default_requirements(self, job_title):
        """Get default skill requirements for common job titles"""
        defaults = {
            'software engineer': {
                'python': 2, 'javascript': 2, 'java': 2, 'sql': 1, 'git': 2
            },
            'data scientist': {
                'python': 3, 'sql': 2, 'data_analysis': 3, 'statistics': 2, 'machine_learning': 2
            },
            'frontend developer': {
                'javascript': 3, 'html': 3, 'css': 3, 'react': 2
            },
            'backend developer': {
                'python': 2, 'java': 2, 'sql': 3, 'javascript': 1
            },
            'data analyst': {
                'sql': 2, 'excel': 2, 'data_analysis': 2, 'python': 1
            },
            'flutter developer': {
                'flutter': 3, 'dart': 2, 'mobile_development': 2, 'git': 1
            },
            'product manager': {
                'communication': 3, 'leadership': 2, 'project_management': 3, 'marketing': 2
            }
        }

        job_lower = job_title.lower()
        for job_key, reqs in defaults.items():
            if job_key in job_lower:
                return reqs

        return {'communication': 1, 'problem_solving': 1}  # Minimal defaults

    def determine_priority(self, gap_size, skill):
        """Determine priority level for skill gap"""
        if gap_size >= 2:
            return 'high'
        elif gap_size >= 1:
            return 'medium'
        else:
            return 'low'

    def assess_difficulty(self, skill):
        """Assess learning difficulty for a skill"""
        difficulty_map = {
            'python': 'medium',
            'javascript': 'medium',
            'java': 'medium',
            'sql': 'easy',
            'html': 'easy',
            'css': 'easy',
            'communication': 'medium',
            'leadership': 'hard',
            'project_management': 'medium',
            'data_analysis': 'medium',
            'ui_ux': 'medium',
            'marketing': 'medium',
            'machine_learning': 'hard',
            'devops': 'hard',
            'testing': 'medium',
            'git': 'easy',
            'react': 'medium',
            'flutter': 'medium',
            'dart': 'medium',
            'android': 'medium',
            'ios': 'medium',
            'mobile_development': 'medium',
            'statistics': 'medium',
            'excel': 'easy'
        }
        return difficulty_map.get(skill, 'medium')

    def estimate_learning_time(self, gap_size):
        """Estimate learning time based on gap size."""
        if gap_size >= 2:
            return "8-12 weeks"
        if gap_size >= 1:
            return "4-6 weeks"
        return "2-4 weeks"

    def generate_learning_plan(self, skill_gaps, time_available='medium'):
        """Generate a personalized learning plan"""
        time_multipliers = {
            'limited': 0.5,
            'medium': 1.0,
            'plenty': 1.5
        }

        multiplier = time_multipliers.get(time_available, 1.0)

        plan = {
            'total_weeks': 0,
            'phases': [],
            'milestones': []
        }

        # Group gaps by priority
        high_priority = [g for g in skill_gaps if g['priority'] == 'high']
        medium_priority = [g for g in skill_gaps if g['priority'] == 'medium']
        low_priority = [g for g in skill_gaps if g['priority'] == 'low']

        current_week = 0

        # Phase 1: High priority skills
        if high_priority:
            phase_duration = max(4, len(high_priority) * 2) * multiplier
            plan['phases'].append({
                'name': 'Foundation Building',
                'duration_weeks': round(phase_duration),
                'skills': high_priority,
                'focus': 'Build core competencies'
            })
            current_week += phase_duration

        # Phase 2: Medium priority skills
        if medium_priority:
            phase_duration = max(3, len(medium_priority) * 1.5) * multiplier
            plan['phases'].append({
                'name': 'Skill Enhancement',
                'duration_weeks': round(phase_duration),
                'skills': medium_priority,
                'focus': 'Enhance existing skills'
            })
            current_week += phase_duration

        # Phase 3: Low priority skills
        if low_priority:
            phase_duration = max(2, len(low_priority) * 1) * multiplier
            plan['phases'].append({
                'name': 'Advanced Development',
                'duration_weeks': round(phase_duration),
                'skills': low_priority,
                'focus': 'Master advanced concepts'
            })
            current_week += phase_duration

        plan['total_weeks'] = round(current_week)

        # Generate milestones
        plan['milestones'] = self.generate_milestones(plan['phases'])

        return plan

    def generate_milestones(self, phases):
        """Generate learning milestones"""
        milestones = []
        current_week = 0

        for phase in phases:
            milestones.append({
                'week': current_week + phase['duration_weeks'] // 2,
                'title': f"Complete {phase['name']} Phase",
                'description': phase['focus'],
                'skills_covered': [s['skill'] for s in phase['skills']]
            })
            current_week += phase['duration_weeks']

        return milestones

    def mock_gap_analysis(self, user_skills, target_job):
        """Mock gap analysis for testing"""
        mock_requirements = {
            'python': 2,
            'javascript': 2,
            'communication': 2,
            'problem_solving': 2
        }

        gaps = []
        for skill, required in mock_requirements.items():
            user_level = user_skills.get(skill, 0)
            if user_level < required:
                gaps.append({
                    'skill': skill,
                    'current_level': user_level,
                    'required_level': required,
                    'gap_size': required - user_level,
                    'priority': 'high' if required - user_level >= 1.5 else 'medium',
                    'difficulty': 'medium'
                })

        return gaps
