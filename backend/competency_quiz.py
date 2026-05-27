import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import os
from pathlib import Path

class CompetencyQuiz:
    HR_QUESTION_OPTIONS = ["Needs Practice", "Basic Answer", "Strong Answer", "Excellent STAR Answer"]
    MAX_QUESTIONS_PER_CATEGORY = 5
    MAX_QUESTIONS_TOTAL = 24
    MAX_DATASET_RECORDS_TO_SCAN = 5000

    def __init__(self):
        self.questions = self.load_questions()
        self.skill_categories = {
            'technical': ['python', 'javascript', 'java', 'sql', 'html', 'css', 'react', 'node.js', 'git'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem_solving', 'time_management',
                            'adaptability', 'culture_fit', 'motivation', 'work_style', 'conflict_resolution'],
            'business': ['project_management', 'agile', 'scrum', 'data_analysis', 'marketing', 'career_planning'],
            'design': ['ui_ux', 'graphic_design', 'prototyping', 'user_research']
        }

    def load_questions(self):
        """Load competency questions from the HR interview dataset."""
        questions_file = Path(__file__).parent / "data" / "hr_interview_questions_dataset.json"

        if not questions_file.exists():
            return self.create_default_questions()

        questions = self.load_hr_interview_questions(questions_file)
        return questions or self.create_default_questions()

    def load_hr_interview_questions(self, questions_file):
        """Sample interview prompts and adapt them to the existing rating-quiz UI."""
        sampled = {}
        seen_questions = set()
        skill_counts = {}

        scanned_records = 0
        for item in self.iter_json_array(questions_file):
            scanned_records += 1
            if scanned_records > self.MAX_DATASET_RECORDS_TO_SCAN:
                break

            category = item.get("category") or "General"
            prompt = item.get("question")
            if not prompt or prompt in seen_questions:
                continue

            quiz_category, skill = self.map_hr_category(category)
            if skill_counts.get(skill, 0) >= self.MAX_QUESTIONS_PER_CATEGORY:
                continue

            seen_questions.add(prompt)
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            question_number = skill_counts[skill]
            category_questions = sampled.setdefault(quiz_category, [])
            category_questions.append({
                "id": f"hr_{skill}_{question_number}",
                "question": f"How confident are you answering this interview question: {prompt}",
                "category": quiz_category,
                "skill": skill,
                "type": "rating",
                "options": self.HR_QUESTION_OPTIONS,
                "source_category": category,
                "role": item.get("role"),
                "experience": item.get("experience"),
                "difficulty": item.get("difficulty"),
                "keywords": item.get("keywords", [])
            })

            total_questions = sum(len(questions) for questions in sampled.values())
            if total_questions >= self.MAX_QUESTIONS_TOTAL:
                break

        return sampled

    def iter_json_array(self, file_path):
        """Yield items from a large JSON array without loading the full dataset."""
        decoder = json.JSONDecoder()
        buffer = ""
        inside_array = False

        with open(file_path, "r", encoding="utf-8") as file:
            while True:
                chunk = file.read(65536)
                if not chunk and not buffer.strip():
                    break

                buffer += chunk
                index = 0

                while True:
                    while index < len(buffer) and buffer[index].isspace():
                        index += 1

                    if not inside_array:
                        if index < len(buffer) and buffer[index] == "[":
                            inside_array = True
                            index += 1
                        else:
                            break

                    while index < len(buffer) and buffer[index] in " \r\n\t,":
                        index += 1

                    if index < len(buffer) and buffer[index] == "]":
                        return

                    try:
                        item, end = decoder.raw_decode(buffer, index)
                    except json.JSONDecodeError:
                        buffer = buffer[index:]
                        break

                    yield item
                    index = end

                if not chunk:
                    break

    def map_hr_category(self, category):
        """Map HR interview categories into competency quiz skills."""
        normalized = category.strip().lower().replace(" ", "_").replace("-", "_")
        category_map = {
            "adaptability": ("soft_skills", "adaptability"),
            "culture_fit": ("soft_skills", "culture_fit"),
            "motivation": ("soft_skills", "motivation"),
            "work_style": ("soft_skills", "work_style"),
            "team_collaboration": ("soft_skills", "teamwork"),
            "leadership": ("soft_skills", "leadership"),
            "career_goals": ("business", "career_planning"),
            "conflict_resolution": ("soft_skills", "conflict_resolution")
        }
        return category_map.get(normalized, ("soft_skills", normalized))

    def create_default_questions(self):
        """Create default competency questions"""
        return {
            "technical": [
                {
                    "id": "tech_1",
                    "question": "How would you rate your proficiency in Python programming?",
                    "category": "technical",
                    "skill": "python",
                    "type": "rating",
                    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
                },
                {
                    "id": "tech_2",
                    "question": "How comfortable are you with SQL database queries?",
                    "category": "technical",
                    "skill": "sql",
                    "type": "rating",
                    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
                },
                {
                    "id": "tech_3",
                    "question": "How would you rate your experience with web development (HTML/CSS/JS)?",
                    "category": "technical",
                    "skill": "web_development",
                    "type": "rating",
                    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
                }
            ],
            "soft_skills": [
                {
                    "id": "soft_1",
                    "question": "How would you rate your communication skills?",
                    "category": "soft_skills",
                    "skill": "communication",
                    "type": "rating",
                    "options": ["Poor", "Fair", "Good", "Excellent"]
                },
                {
                    "id": "soft_2",
                    "question": "How effective are you at problem-solving?",
                    "category": "soft_skills",
                    "skill": "problem_solving",
                    "type": "rating",
                    "options": ["Poor", "Fair", "Good", "Excellent"]
                }
            ],
            "business": [
                {
                    "id": "bus_1",
                    "question": "How familiar are you with project management methodologies?",
                    "category": "business",
                    "skill": "project_management",
                    "type": "rating",
                    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
                }
            ]
        }

    def get_questions_by_category(self, category=None):
        """Get questions by category or all questions"""
        if category and category in self.questions:
            return self.questions[category]
        # Return all questions as a flat list
        all_questions = []
        for cat_questions in self.questions.values():
            all_questions.extend(cat_questions)
        return all_questions

    def calculate_competency_score(self, responses):
        """Calculate competency scores from quiz responses"""
        scores = {}
        category_scores = {}

        for response in responses:
            question_id = response.get('question_id')
            answer = response.get('answer')

            # Find the question
            question = None
            for cat_questions in self.questions.values():
                for q in cat_questions:
                    if q['id'] == question_id:
                        question = q
                        break
                if question:
                    break

            if not question:
                continue

            # Convert answer to score (0-3 for ratings)
            if isinstance(answer, str):
                score_map = {"Beginner": 0, "Poor": 0, "Intermediate": 1, "Fair": 1,
                           "Advanced": 2, "Good": 2, "Expert": 3, "Excellent": 3,
                           "Needs Practice": 0, "Basic Answer": 1,
                           "Strong Answer": 2, "Excellent STAR Answer": 3}
                score = score_map.get(answer, 0)
            else:
                score = min(max(int(answer), 0), 3)

            skill = question['skill']
            category = question['category']

            if skill not in scores:
                scores[skill] = []
            scores[skill].append(score)

            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)

        # Average scores. Keep 0-3 levels for downstream analysis and expose
        # percentages for the frontend results view.
        skill_levels = {}
        final_skill_scores = []
        for skill, collected_scores in scores.items():
            level = round(sum(collected_scores) / len(collected_scores), 2)
            skill_levels[skill] = level
            final_skill_scores.append({
                'skill': skill.replace('_', ' ').title(),
                'score': round((level / 3) * 100, 1),
                'level': level
            })

        category_levels = {}
        final_category_scores = []
        for category, collected_scores in category_scores.items():
            level = round(sum(collected_scores) / len(collected_scores), 2)
            category_levels[category] = level
            final_category_scores.append({
                'category': category.replace('_', ' ').title(),
                'score': round((level / 3) * 100, 1),
                'level': level
            })

        if not category_levels:
            return {
                'skill_scores': [],
                'skill_levels': {},
                'category_scores': [],
                'category_levels': {},
                'overall_score': 0,
                'competency_level': 'Not Assessed',
                'recommendations': ['Complete the quiz to receive competency recommendations.']
            }

        overall_level = round(sum(category_levels.values()) / len(category_levels), 2)
        overall_score = round((overall_level / 3) * 100, 1)

        return {
            'skill_scores': final_skill_scores,
            'skill_levels': skill_levels,
            'category_scores': final_category_scores,
            'category_levels': category_levels,
            'overall_score': overall_score,
            'competency_level': self.get_competency_level(overall_score),
            'recommendations': self.generate_recommendations(final_skill_scores)
        }

    def get_competency_level(self, overall_score):
        if overall_score >= 85:
            return "Advanced"
        if overall_score >= 65:
            return "Proficient"
        if overall_score >= 40:
            return "Developing"
        return "Needs Practice"

    def generate_recommendations(self, skill_scores):
        weak_skills = [score for score in skill_scores if score["score"] < 65]
        if not weak_skills:
            return ["You show strong interview readiness across the assessed competency areas."]

        return [
            f"Practice structured STAR responses for {score['skill']}."
            for score in weak_skills[:3]
        ]

    def identify_skill_gaps(self, user_scores, job_requirements):
        """Identify skill gaps based on user scores and job requirements"""
        gaps = []

        for skill, required_level in job_requirements.items():
            user_level = user_scores.get(skill, 0)
            if user_level < required_level:
                gap_size = required_level - user_level
                gaps.append({
                    'skill': skill,
                    'current_level': user_level,
                    'required_level': required_level,
                    'gap_size': gap_size,
                    'priority': 'high' if gap_size >= 2 else 'medium' if gap_size >= 1 else 'low'
                })

        return sorted(gaps, key=lambda x: x['gap_size'], reverse=True)

    def recommend_learning_path(self, skill_gaps, user_profile):
        """Recommend learning pathways based on skill gaps"""
        pathways = []

        for gap in skill_gaps:
            skill = gap['skill']
            priority = gap['priority']

            # Get courses for this skill
            courses = self.get_courses_for_skill(skill, priority)

            pathways.append({
                'skill': skill,
                'gap_size': gap['gap_size'],
                'priority': priority,
                'recommended_courses': courses[:3],  # Top 3 courses
                'estimated_time': self.estimate_learning_time(gap['gap_size'])
            })

        return pathways

    def get_courses_for_skill(self, skill, priority):
        """Get relevant courses for a specific skill"""
        # This would integrate with the course recommendation system
        # For now, return mock data
        course_templates = {
            'python': [
                {'title': 'Python for Everybody', 'platform': 'Coursera', 'duration': '8 weeks'},
                {'title': 'Complete Python Bootcamp', 'platform': 'Udemy', 'duration': '12 weeks'},
                {'title': 'Python Programming Fundamentals', 'platform': 'edX', 'duration': '6 weeks'}
            ],
            'javascript': [
                {'title': 'JavaScript Algorithms and Data Structures', 'platform': 'freeCodeCamp', 'duration': '4 weeks'},
                {'title': 'Modern JavaScript', 'platform': 'Udemy', 'duration': '10 weeks'}
            ],
            'communication': [
                {'title': 'Business Communication Skills', 'platform': 'Coursera', 'duration': '4 weeks'},
                {'title': 'Effective Communication', 'platform': 'LinkedIn Learning', 'duration': '2 weeks'}
            ]
        }

        return course_templates.get(skill, [
            {'title': f'Introduction to {skill.title()}', 'platform': 'Various', 'duration': '4 weeks'}
        ])

    def estimate_learning_time(self, gap_size):
        """Estimate learning time based on gap size"""
        if gap_size >= 2:
            return "8-12 weeks"
        elif gap_size >= 1:
            return "4-6 weeks"
        else:
            return "2-4 weeks"
