import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import random

class CertificationSystem:
    def __init__(self, questions_df=None):
        self.questions_df = questions_df
        self.certifications = self.load_certifications()
        self.user_certifications = {}
        self.assessments = self.load_assessments()

    def load_certifications(self):
        """Load available certifications"""
        csv_certifications = self.load_certifications_from_questions()
        if csv_certifications:
            return csv_certifications

        return {
            'python_basic': {
                'id': 'python_basic',
                'name': 'Python Programming Basics',
                'description': 'Fundamental Python programming skills',
                'skills_tested': ['python', 'programming_fundamentals'],
                'difficulty': 'Beginner',
                'duration_minutes': 45,
                'passing_score': 70,
                'validity_years': 2,
                'badge_color': '#3776AB'
            },
            'data_analysis': {
                'id': 'data_analysis',
                'name': 'Data Analysis Fundamentals',
                'description': 'Basic data analysis and visualization skills',
                'skills_tested': ['data_analysis', 'statistics', 'excel'],
                'difficulty': 'Intermediate',
                'duration_minutes': 60,
                'passing_score': 75,
                'validity_years': 2,
                'badge_color': '#1F77B4'
            },
            'machine_learning': {
                'id': 'machine_learning',
                'name': 'Machine Learning Essentials',
                'description': 'Core machine learning concepts and algorithms',
                'skills_tested': ['machine_learning', 'python', 'statistics'],
                'difficulty': 'Advanced',
                'duration_minutes': 90,
                'passing_score': 80,
                'validity_years': 1,
                'badge_color': '#FF6B35'
            },
            'communication': {
                'id': 'communication',
                'name': 'Professional Communication',
                'description': 'Business communication and presentation skills',
                'skills_tested': ['communication', 'presentation', 'leadership'],
                'difficulty': 'Intermediate',
                'duration_minutes': 50,
                'passing_score': 70,
                'validity_years': 3,
                'badge_color': '#4CAF50'
            },
            'project_management': {
                'id': 'project_management',
                'name': 'Project Management Fundamentals',
                'description': 'Basic project management methodologies',
                'skills_tested': ['project_management', 'agile', 'scrum'],
                'difficulty': 'Intermediate',
                'duration_minutes': 55,
                'passing_score': 75,
                'validity_years': 2,
                'badge_color': '#9C27B0'
            }
        }

    def load_assessments(self):
        """Load assessment questions"""
        csv_assessments = self.load_assessments_from_questions()
        if csv_assessments:
            return csv_assessments

        return {
            'python_basic': [
                {
                    'id': 'q1',
                    'question': 'What is the output of print(2 + 3 * 4)?',
                    'options': ['14', '20', '24', '26'],
                    'correct_answer': 1,
                    'explanation': 'Multiplication has higher precedence than addition'
                },
                {
                    'id': 'q2',
                    'question': 'Which of the following is used to define a function in Python?',
                    'options': ['def', 'function', 'func', 'define'],
                    'correct_answer': 0,
                    'explanation': 'The def keyword is used to define functions in Python'
                }
            ],
            'data_analysis': [
                {
                    'id': 'q1',
                    'question': 'What does CSV stand for?',
                    'options': ['Computer System Values', 'Comma Separated Values', 'Common Style Variables', 'Calculated Statistical Values'],
                    'correct_answer': 1,
                    'explanation': 'CSV stands for Comma Separated Values'
                }
            ],
            'machine_learning': [
                {
                    'id': 'q1',
                    'question': 'What is supervised learning?',
                    'options': [
                        'Learning without labeled data',
                        'Learning with labeled training data',
                        'Learning from unstructured data',
                        'Learning from reinforcement signals'
                    ],
                    'correct_answer': 1,
                    'explanation': 'Supervised learning uses labeled training data'
                }
            ]
        }

    def load_certifications_from_questions(self):
        """Create certifications from Placement_Interview_Quiz_Questions.csv."""
        if self.questions_df is None or self.questions_df.empty:
            return {}

        required_columns = {"id", "section", "difficulty", "topic", "question", "a", "b", "c", "d", "answer"}
        if not required_columns.issubset(set(self.questions_df.columns)):
            return {}

        certifications = {}
        for section, rows in self.questions_df.groupby("section", sort=False):
            cert_id = self.slugify(section)
            topics = self.unique_values(rows["topic"])
            difficulties = self.unique_values(rows["difficulty"])

            certifications[cert_id] = {
                "id": cert_id,
                "name": f"{section} Certification",
                "description": f"Placement interview certification covering {', '.join(topics[:4])}.",
                "skills_tested": topics[:8],
                "difficulty": self.certification_difficulty(difficulties),
                "duration_minutes": min(90, max(30, len(rows.head(10)) * 3)),
                "passing_score": 70,
                "validity_years": 2,
                "badge_color": "#2563EB",
                "prerequisites": "None",
                "source_dataset": "Placement_Interview_Quiz_Questions.csv"
            }

        return certifications

    def load_assessments_from_questions(self):
        """Create MCQ assessments from Placement_Interview_Quiz_Questions.csv."""
        if self.questions_df is None or self.questions_df.empty:
            return {}

        required_columns = {"id", "section", "difficulty", "topic", "question", "a", "b", "c", "d", "answer"}
        if not required_columns.issubset(set(self.questions_df.columns)):
            return {}

        assessments = {}
        for section, rows in self.questions_df.groupby("section", sort=False):
            cert_id = self.slugify(section)
            questions = []

            for _, row in rows.head(25).iterrows():
                options = [
                    str(row.get("a", "")).strip(),
                    str(row.get("b", "")).strip(),
                    str(row.get("c", "")).strip(),
                    str(row.get("d", "")).strip()
                ]
                answer_letter = str(row.get("answer", "")).strip().upper()
                correct_index = {"A": 0, "B": 1, "C": 2, "D": 3}.get(answer_letter, 0)

                questions.append({
                    "id": str(row.get("id", "")),
                    "question": str(row.get("question", "")).strip(),
                    "type": "multiple_choice",
                    "options": options,
                    "correct_answer": options[correct_index],
                    "correct_option": answer_letter,
                    "skill": str(row.get("topic", "")).strip(),
                    "difficulty": str(row.get("difficulty", "")).strip()
                })

            assessments[cert_id] = questions

        return assessments

    def get_available_certifications(self, user_profile=None):
        """Get certifications available to user"""
        certifications = []

        for cert_id, cert in self.certifications.items():
            # Check if user meets prerequisites
            eligible = self.check_eligibility(user_profile, cert) if user_profile else True

            certifications.append({
                **cert,
                'eligible': eligible,
                'user_has_cert': self.user_has_certification(user_profile.get('id') if user_profile else None, cert_id) if user_profile else False
            })

        return certifications

    def check_eligibility(self, user_profile, certification):
        """Check if user is eligible for certification"""
        if certification.get("source_dataset") == "Placement_Interview_Quiz_Questions.csv":
            return True

        if not user_profile:
            return True

        user_skills = user_profile.get('skill_scores', {})

        # Check skill requirements
        for skill in certification['skills_tested']:
            required_level = 1.5 if certification['difficulty'] == 'Beginner' else 2.0 if certification['difficulty'] == 'Intermediate' else 2.5
            if user_skills.get(skill, 0) < required_level:
                return False

        return True

    def start_assessment(self, user_id, certification_id):
        """Start a certification assessment"""
        if certification_id not in self.certifications:
            raise ValueError(f"Certification {certification_id} not found")

        if certification_id not in self.assessments:
            raise ValueError(f"Assessment for {certification_id} not available")

        certification = self.certifications[certification_id]
        questions = self.assessments[certification_id]

        # Shuffle questions for randomization
        assessment_questions = random.sample(questions, min(10, len(questions)))

        assessment = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'certification_id': certification_id,
            'questions': assessment_questions,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'answers': {},
            'time_remaining': certification['duration_minutes'] * 60  # seconds
        }

        return assessment

    def submit_assessment(self, assessment_id, answers):
        """Submit assessment answers and calculate score"""
        # In a real implementation, this would retrieve the assessment from storage
        # For now, we'll simulate with the provided data

        # Mock assessment data (in real implementation, retrieve from database)
        mock_assessment = {
            'certification_id': 'python_basic',
            'questions': [
                {'id': 'q1', 'correct_answer': 1},
                {'id': 'q2', 'correct_answer': 0}
            ]
        }

        certification = self.certifications[mock_assessment['certification_id']]
        questions = mock_assessment['questions']

        # Calculate score
        correct_answers = 0
        total_questions = len(questions)

        for question in questions:
            q_id = question['id']
            if q_id in answers and answers[q_id] == question['correct_answer']:
                correct_answers += 1

        score_percentage = (correct_answers / total_questions) * 100
        passed = score_percentage >= certification['passing_score']

        result = {
            'assessment_id': assessment_id,
            'score': round(score_percentage, 1),
            'passed': passed,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'certification': certification['name'],
            'completed_at': datetime.now().isoformat()
        }

        if passed:
            # Issue certificate
            certificate = self.issue_certificate('mock_user_id', certification['id'], score_percentage)
            result['certificate'] = certificate

        return result

    def issue_certificate(self, user_id, certification_id, score):
        """Issue a certificate to the user"""
        certification = self.certifications[certification_id]
        certificate_id = str(uuid.uuid4())

        certificate = {
            'id': certificate_id,
            'user_id': user_id,
            'certification_id': certification_id,
            'certification_name': certification['name'],
            'score': score,
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=365 * certification['validity_years'])).isoformat(),
            'badge_url': f"/badges/{certification_id}.png",
            'verification_url': f"/verify/{certificate_id}",
            'status': 'active'
        }

        # Store certificate
        if user_id not in self.user_certifications:
            self.user_certifications[user_id] = []
        self.user_certifications[user_id].append(certificate)

        return certificate

    def get_user_certifications(self, user_id):
        """Get user's certifications"""
        return self.user_certifications.get(user_id, [])

    def user_has_certification(self, user_id, certification_id):
        """Check if user has a specific certification"""
        if not user_id:
            return False

        user_certs = self.user_certifications.get(user_id, [])
        return any(cert['certification_id'] == certification_id and cert['status'] == 'active' for cert in user_certs)

    def verify_certificate(self, certificate_id):
        """Verify a certificate's authenticity"""
        for user_certs in self.user_certifications.values():
            for cert in user_certs:
                if cert['id'] == certificate_id:
                    return {
                        'valid': cert['status'] == 'active',
                        'certificate': cert,
                        'verification_date': datetime.now().isoformat()
                    }
        return {'valid': False, 'error': 'Certificate not found'}

    def get_certification_stats(self, certification_id):
        """Get statistics for a certification"""
        certification = self.certifications.get(certification_id)
        if not certification:
            return None

        # Count holders
        holders = 0
        for user_certs in self.user_certifications.values():
            if any(cert['certification_id'] == certification_id for cert in user_certs):
                holders += 1

        return {
            'certification': certification,
            'total_holders': holders,
            'average_score': 75.5,  # Mock data
            'completion_rate': 68.2,  # Mock data
            'popularity_rank': 3  # Mock data
        }

    def get_recommended_certifications(self, user_profile):
        """Get recommended certifications based on user profile"""
        user_skills = user_profile.get('skill_scores', {})
        user_certs = self.get_user_certifications(user_profile.get('id', ''))

        completed_certs = {cert['certification_id'] for cert in user_certs}

        recommendations = []

        for cert_id, cert in self.certifications.items():
            if cert_id in completed_certs:
                continue

            # Calculate relevance score
            skill_match = 0
            for skill in cert['skills_tested']:
                skill_match += user_skills.get(skill, 0)

            avg_skill_match = skill_match / len(cert['skills_tested']) if cert['skills_tested'] else 0

            # Check eligibility
            eligible = self.check_eligibility(user_profile, cert)

            if eligible or avg_skill_match >= 1.0:  # Show if eligible or has some relevant skills
                recommendations.append({
                    'certification': cert,
                    'relevance_score': round(avg_skill_match * 33.33, 1),  # Convert to percentage
                    'eligible': eligible,
                    'estimated_completion_time': f"{cert['duration_minutes']} minutes",
                    'difficulty_match': self.get_difficulty_match(user_profile, cert)
                })

        return sorted(recommendations, key=lambda x: x['relevance_score'], reverse=True)

    def get_difficulty_match(self, user_profile, certification):
        """Get difficulty match for user"""
        experience_years = user_profile.get('experience_years', 0)

        difficulty_levels = {
            'Beginner': 0,
            'Intermediate': 2,
            'Advanced': 4
        }

        cert_level = difficulty_levels.get(certification['difficulty'], 2)

        if experience_years >= cert_level:
            return 'Good Match'
        elif experience_years >= cert_level - 1:
            return 'Stretch Goal'
        else:
            return 'Challenging'

    def get_certification_progress(self, user_id):
        """Get user's certification progress"""
        user_certs = self.get_user_certifications(user_id)

        progress = {
            'completed': len([c for c in user_certs if c['status'] == 'active']),
            'in_progress': 0,  # Mock data
            'available': len(self.certifications) - len(user_certs),
            'recent_certificates': user_certs[-3:] if user_certs else []
        }

        return progress

    def get_certification_quiz(self, certification_id):
        """Get quiz questions for a certification"""
        if certification_id not in self.certifications:
            raise ValueError(f"Certification {certification_id} not found")

        if certification_id in self.assessments:
            return [
                {
                    "id": question["id"],
                    "question": question["question"],
                    "type": question.get("type", "multiple_choice"),
                    "options": question.get("options", []),
                    "skill": question.get("skill", ""),
                    "difficulty": question.get("difficulty", "")
                }
                for question in self.assessments[certification_id][:10]
            ]

        cert = self.certifications[certification_id]
        skills = cert.get('skills_tested', [])

        # Create simple quiz based on skills
        questions = []
        for i, skill in enumerate(skills[:5]):  # Limit to 5 questions
            questions.append({
                'id': f"{certification_id}_q{i+1}",
                'question': f"What is your proficiency level in {skill.replace('_', ' ')}?",
                'type': 'rating',
                'options': ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
                'skill': skill
            })

        return questions

    def get_assessment_questions(self, certification_id):
        return self.assessments.get(certification_id, [])

    def unique_values(self, values):
        result = []
        for value in values:
            normalized = str(value or "").strip()
            if normalized and normalized not in result:
                result.append(normalized)
        return result

    def certification_difficulty(self, difficulties):
        difficulty_order = {
            "easy": "Beginner",
            "medium": "Intermediate",
            "hard": "Advanced"
        }
        lowered = {difficulty.lower() for difficulty in difficulties}
        if "hard" in lowered:
            return difficulty_order["hard"]
        if "medium" in lowered:
            return difficulty_order["medium"]
        return difficulty_order["easy"]

    def slugify(self, value):
        text = str(value or "certification").strip().lower().replace("&", "and")
        slug = "".join(char if char.isalnum() else "_" for char in text)
        return "_".join(part for part in slug.split("_") if part)

    def create_custom_assessment(self, certification_id, questions):
        """Create a custom assessment (admin function)"""
        if certification_id not in self.certifications:
            raise ValueError(f"Certification {certification_id} not found")

        self.assessments[certification_id] = questions
        return True

    def update_certification(self, certification_id, updates):
        """Update certification details (admin function)"""
        if certification_id not in self.certifications:
            raise ValueError(f"Certification {certification_id} not found")

        self.certifications[certification_id].update(updates)
        return self.certifications[certification_id]
