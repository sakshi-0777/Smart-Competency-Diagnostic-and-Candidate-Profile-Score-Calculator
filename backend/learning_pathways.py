import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

class LearningPathways:
    def __init__(self, courses_df=None):
        self.courses_df = courses_df
        self.learning_paths = self.load_learning_paths()

    def load_learning_paths(self):
        """Load predefined learning paths"""
        return {
            'software_engineer': {
                'name': 'Software Engineering Path',
                'duration_weeks': 24,
                'modules': [
                    {
                        'name': 'Programming Fundamentals',
                        'skills': ['python', 'javascript', 'java'],
                        'duration': 8,
                        'courses': ['Python for Everybody', 'JavaScript Basics', 'Java Programming']
                    },
                    {
                        'name': 'Web Development',
                        'skills': ['html', 'css', 'react', 'node.js'],
                        'duration': 8,
                        'courses': ['HTML & CSS', 'React Development', 'Node.js Backend']
                    },
                    {
                        'name': 'Databases & Tools',
                        'skills': ['sql', 'git'],
                        'duration': 4,
                        'courses': ['SQL Fundamentals', 'Git Version Control']
                    },
                    {
                        'name': 'Advanced Topics',
                        'skills': ['algorithms', 'system_design'],
                        'duration': 4,
                        'courses': ['Data Structures', 'System Design']
                    }
                ]
            },
            'data_scientist': {
                'name': 'Data Science Path',
                'duration_weeks': 20,
                'modules': [
                    {
                        'name': 'Python & Statistics',
                        'skills': ['python', 'statistics'],
                        'duration': 6,
                        'courses': ['Python for Data Science', 'Statistics Fundamentals']
                    },
                    {
                        'name': 'Data Analysis',
                        'skills': ['pandas', 'numpy', 'data_analysis'],
                        'duration': 6,
                        'courses': ['Data Analysis with Pandas', 'NumPy for Data Science']
                    },
                    {
                        'name': 'Machine Learning',
                        'skills': ['machine_learning', 'scikit_learn'],
                        'duration': 8,
                        'courses': ['Machine Learning Basics', 'Scikit-learn Essentials']
                    }
                ]
            },
            'frontend_developer': {
                'name': 'Frontend Development Path',
                'duration_weeks': 16,
                'modules': [
                    {
                        'name': 'Web Fundamentals',
                        'skills': ['html', 'css', 'javascript'],
                        'duration': 4,
                        'courses': ['HTML & CSS', 'JavaScript Fundamentals']
                    },
                    {
                        'name': 'Modern Frameworks',
                        'skills': ['react', 'ui_ux'],
                        'duration': 8,
                        'courses': ['React Development', 'UI/UX Design Principles']
                    },
                    {
                        'name': 'Advanced Topics',
                        'skills': ['typescript', 'testing'],
                        'duration': 4,
                        'courses': ['TypeScript Essentials', 'Frontend Testing']
                    }
                ]
            }
        }

    def create_personalized_pathway(self, user_profile, skill_gaps, target_role):
        """Create a personalized learning pathway"""
        base_path = self.learning_paths.get(target_role.lower().replace(' ', '_'))

        if not base_path:
            return self.create_custom_pathway(skill_gaps, target_role)

        # Customize based on skill gaps
        personalized_modules = []
        total_duration = 0

        for module in base_path['modules']:
            # Check if user needs this module
            module_relevant = any(
                gap['skill'] in module['skills']
                for gap in skill_gaps
                if gap['priority'] in ['high', 'medium']
            )

            if module_relevant or not skill_gaps:  # Include if relevant or no gaps specified
                # Adjust duration based on user's current level
                adjusted_duration = self.adjust_module_duration(module, user_profile)
                personalized_modules.append({
                    **module,
                    'duration': adjusted_duration,
                    'status': 'pending',
                    'progress': 0
                })
                total_duration += adjusted_duration

        pathway = {
            'name': f"Personalized {base_path['name']}",
            'target_role': target_role,
            'total_duration_weeks': total_duration,
            'modules': personalized_modules,
            'created_at': datetime.now().isoformat(),
            'skill_gaps_addressed': [gap['skill'] for gap in skill_gaps],
            'estimated_completion': (datetime.now() + timedelta(weeks=total_duration)).isoformat()
        }

        return pathway

    def create_custom_pathway(self, skill_gaps, target_role):
        """Create a custom pathway based on skill gaps"""
        modules = []
        total_duration = 0

        # Group skill gaps by category
        skill_categories = {}
        for gap in skill_gaps:
            category = self.get_skill_category(gap['skill'])
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(gap)

        # Create modules for each category
        for category, gaps in skill_categories.items():
            module_duration = sum(
                self.estimate_skill_learning_time(gap['gap_size'], gap['difficulty'])
                for gap in gaps
            )

            modules.append({
                'name': f"{category.title()} Skills Development",
                'skills': [gap['skill'] for gap in gaps],
                'duration': max(2, min(module_duration, 8)),  # 2-8 weeks
                'courses': self.get_courses_for_skills([gap['skill'] for gap in gaps]),
                'status': 'pending',
                'progress': 0
            })
            total_duration += modules[-1]['duration']

        return {
            'name': f"Custom Pathway for {target_role}",
            'target_role': target_role,
            'total_duration_weeks': total_duration,
            'modules': modules,
            'created_at': datetime.now().isoformat(),
            'skill_gaps_addressed': [gap['skill'] for gap in skill_gaps],
            'estimated_completion': (datetime.now() + timedelta(weeks=total_duration)).isoformat()
        }

    def adjust_module_duration(self, module, user_profile):
        """Adjust module duration based on user's current skill level"""
        user_skills = user_profile.get('skill_scores', {})

        # Calculate average skill level for module skills
        module_skills = [user_skills.get(skill, 0) for skill in module['skills']]
        avg_skill_level = sum(module_skills) / len(module_skills) if module_skills else 0

        # Adjust duration: higher skill level = shorter duration
        if avg_skill_level >= 2.5:  # Advanced
            return max(2, module['duration'] // 2)
        elif avg_skill_level >= 1.5:  # Intermediate
            return max(3, module['duration'] * 3 // 4)
        else:  # Beginner
            return module['duration']

    def get_skill_category(self, skill):
        """Get category for a skill"""
        categories = {
            'technical': ['python', 'javascript', 'java', 'sql', 'html', 'css', 'git', 'react', 'node.js'],
            'data_science': ['pandas', 'numpy', 'machine_learning', 'statistics', 'data_analysis'],
            'design': ['ui_ux', 'graphic_design', 'prototyping'],
            'business': ['project_management', 'agile', 'marketing', 'communication'],
            'soft_skills': ['leadership', 'teamwork', 'problem_solving']
        }

        for category, skills in categories.items():
            if skill in skills:
                return category
        return 'general'

    def estimate_skill_learning_time(self, gap_size, difficulty):
        """Estimate learning time for a skill"""
        base_time = {
            'easy': 2,
            'medium': 4,
            'hard': 6
        }

        return base_time.get(difficulty, 4) * (gap_size / 3)  # Scale by gap size

    def get_courses_for_skills(self, skills):
        """Get recommended courses for skills"""
        course_map = {
            'python': ['Python for Everybody', 'Python Bootcamp'],
            'javascript': ['JavaScript Fundamentals', 'Modern JavaScript'],
            'java': ['Java Programming', 'Spring Framework'],
            'sql': ['SQL Fundamentals', 'Database Design'],
            'communication': ['Business Communication', 'Presentation Skills'],
            'leadership': ['Leadership Fundamentals', 'Team Management'],
            'project_management': ['Project Management Basics', 'Agile Methodology']
        }

        courses = []
        for skill in skills:
            courses.extend(course_map.get(skill, [f"{skill.title()} Fundamentals"]))

        return list(set(courses))[:3]  # Return up to 3 unique courses

    def update_pathway_progress(self, pathway_id, module_index, progress):
        """Update progress for a learning pathway"""
        # In a real implementation, this would update a database
        # For now, return updated pathway
        pathway = self.get_pathway_by_id(pathway_id)
        if pathway and 0 <= module_index < len(pathway['modules']):
            pathway['modules'][module_index]['progress'] = min(100, max(0, progress))

            # Update overall progress
            total_progress = sum(m['progress'] for m in pathway['modules']) / len(pathway['modules'])
            pathway['overall_progress'] = round(total_progress, 1)

        return pathway

    def get_pathway_by_id(self, pathway_id):
        """Get pathway by ID (mock implementation)"""
        # In real implementation, fetch from database
        return None

    def build_pathways_from_courses(self):
        """Build learning pathways from the courses CSV dataframe."""
        if self.courses_df is None or self.courses_df.empty:
            return {}

        learning_index_pathways = self.build_pathways_from_learning_index()
        if learning_index_pathways:
            return learning_index_pathways

        required_columns = {"course name", "difficulty level", "course url", "skills"}
        if not required_columns.issubset(set(self.courses_df.columns)):
            return {}

        courses = self.courses_df.copy()
        courses["course rating"] = pd.to_numeric(
            courses.get("course rating", 0),
            errors="coerce"
        ).fillna(0)
        courses["difficulty level"] = courses["difficulty level"].fillna("Beginner")
        courses["pathway_category"] = courses["skills"].apply(self.extract_course_category)

        # Keep categories with enough material to feel like real pathways.
        category_counts = courses["pathway_category"].value_counts()
        categories = category_counts[category_counts >= 8].index.tolist()

        pathways = {}
        for category in categories[:12]:
            category_courses = courses[courses["pathway_category"] == category]
            modules = []

            for difficulty in ["Beginner", "Intermediate", "Advanced", "Conversant"]:
                difficulty_courses = category_courses[
                    category_courses["difficulty level"].str.lower() == difficulty.lower()
                ].sort_values("course rating", ascending=False).head(5)

                if difficulty_courses.empty:
                    continue

                modules.append({
                    "name": f"{difficulty} Courses",
                    "skills": self.extract_common_skills(difficulty_courses),
                    "duration": max(1, len(difficulty_courses) * 2),
                    "courses": [
                        {
                            "title": row.get("course name", "Course"),
                            "url": row.get("course url", ""),
                            "provider": row.get("university", ""),
                            "rating": row.get("course rating", 0),
                            "description": row.get("course description", "")
                        }
                        for _, row in difficulty_courses.iterrows()
                    ]
                })

            if not modules:
                continue

            pathway_id = self.slugify(category)
            duration_weeks = sum(module["duration"] for module in modules)
            pathways[pathway_id] = {
                "name": f"{category} Path",
                "duration_weeks": duration_weeks,
                "description": f"Top-rated courses from Courses.csv for {category.lower()}.",
                "modules": modules
            }

        return pathways

    def build_pathways_from_learning_index(self):
        """Build learning pathways from Learning_Pathway_Index.csv."""
        required_columns = {
            "module_code",
            "course_learning_material",
            "source",
            "course_level",
            "module",
            "duration",
            "difficulty_level",
            "keywords_tags_skills_interests_categories",
            "links"
        }
        if not required_columns.issubset(set(self.courses_df.columns)):
            return {}

        rows = self.courses_df.copy().fillna("")
        rows["_duration_minutes"] = rows["duration"].apply(self.duration_to_minutes)

        pathways = {}
        grouped_rows = rows.groupby(["module_code", "course_learning_material"], sort=False)

        for (module_code, material_name), material_rows in grouped_rows:
            modules = []
            for index, (_, row) in enumerate(material_rows.iterrows()):
                duration_minutes = row.get("_duration_minutes", 0)
                duration_label = row.get("duration") or self.minutes_to_label(duration_minutes)
                tags = self.split_tags(row.get("keywords_tags_skills_interests_categories", ""))
                module_title = row.get("module") or f"Module {index + 1}"
                link = row.get("links", "")

                modules.append({
                    "name": module_title,
                    "skills": tags,
                    "duration": max(1, round(duration_minutes / 60, 1)) if duration_minutes else 1,
                    "duration_label": duration_label,
                    "courses": [
                        {
                            "title": module_title,
                            "url": link,
                            "provider": row.get("source", ""),
                            "rating": "",
                            "description": f"{row.get('type_free_paid', 'Learning material')} from {row.get('source', 'the pathway index')}"
                        }
                    ]
                })

            if not modules:
                continue

            pathway_id = self.slugify(f"{module_code}_{material_name}")
            total_minutes = float(material_rows["_duration_minutes"].sum())
            course_level = self.normalize_level(material_rows["course_level"].iloc[0])
            difficulty = self.normalize_level(material_rows["difficulty_level"].iloc[0])
            source = material_rows["source"].iloc[0]
            all_tags = self.split_tags(
                ", ".join(material_rows["keywords_tags_skills_interests_categories"].astype(str).tolist())
            )

            pathways[pathway_id] = {
                "name": material_name,
                "duration_weeks": max(1, round(total_minutes / 60, 1)) if total_minutes else len(modules),
                "duration_label": self.minutes_to_label(total_minutes) if total_minutes else f"{len(modules)} modules",
                "difficulty": course_level or difficulty or "Beginner",
                "description": f"{course_level or difficulty or 'Structured'} pathway from {source} covering {', '.join(all_tags[:3]) or 'career skills'}.",
                "modules": modules
            }

        return pathways

    def duration_to_minutes(self, value):
        text = str(value or "").strip().lower()
        if not text:
            return 0

        try:
            amount = float(text.split()[0])
        except (ValueError, IndexError):
            return 0

        if "hour" in text:
            return amount * 60
        if "week" in text:
            return amount * 60 * 5
        return amount

    def minutes_to_label(self, minutes):
        minutes = float(minutes or 0)
        if minutes >= 60:
            hours = round(minutes / 60, 1)
            return f"{hours:g} hours"
        return f"{round(minutes):g} minutes"

    def split_tags(self, value):
        tags = []
        for tag in str(value or "").replace(";", ",").split(","):
            normalized = tag.strip()
            if normalized and normalized not in tags:
                tags.append(normalized)
        return tags[:6]

    def normalize_level(self, value):
        value = str(value or "").strip()
        if not value:
            return ""
        return value[:1].upper() + value[1:].lower()

    def extract_course_category(self, skills):
        """Infer a pathway category from the CSV skills/category text."""
        tokens = str(skills or "").split()
        category_tokens = [
            token for token in tokens
            if "-" in token and any(char.isalpha() for char in token)
        ]

        if len(category_tokens) >= 2:
            return self.titleize(category_tokens[-2])
        if category_tokens:
            return self.titleize(category_tokens[-1])
        return "General"

    def extract_common_skills(self, courses):
        """Pull a small readable skill list from the highest-rated rows."""
        ignored_tokens = {
            "and", "or", "the", "with", "for", "in", "of", "to", "a",
            "business", "computer-science", "data-science", "personal-development",
            "information-technology", "arts-and-humanities", "social-sciences",
            "physical-science-and-engineering", "life-sciences", "language-learning"
        }
        skills = []

        for raw_skills in courses["skills"].head(3):
            for skill in str(raw_skills or "").replace("  ", ",").split(","):
                normalized = skill.strip()
                if not normalized:
                    continue

                normalized_key = normalized.lower()
                if normalized_key in ignored_tokens or "-" in normalized_key:
                    continue

                if normalized not in skills:
                    skills.append(normalized)

                if len(skills) == 5:
                    return skills

        return skills or ["Career Skills"]

    def slugify(self, value):
        text = (
            str(value or "pathway")
            .strip()
            .lower()
            .replace("&", "and")
        )
        slug = "".join(char if char.isalnum() else "_" for char in text)
        return "_".join(part for part in slug.split("_") if part)

    def titleize(self, value):
        return str(value or "General").replace("-", " ").replace("_", " ").title()

    def get_all_pathways(self):
        """Get all available learning pathways"""
        csv_pathways = self.build_pathways_from_courses()
        return csv_pathways or self.learning_paths

    def get_recommended_pathways(self, user_profile):
        """Get recommended learning pathways based on user profile"""
        recommendations = []

        # Analyze user skills to recommend suitable career paths
        skill_scores = user_profile.get('skill_scores', {})

        # Simple recommendation logic
        if skill_scores.get('python', 0) >= 2 and skill_scores.get('data_analysis', 0) >= 2:
            recommendations.append({
                'role': 'Data Scientist',
                'confidence': 0.8,
                'reason': 'Strong foundation in Python and data analysis'
            })

        if skill_scores.get('javascript', 0) >= 2 and skill_scores.get('react', 0) >= 1:
            recommendations.append({
                'role': 'Frontend Developer',
                'confidence': 0.7,
                'reason': 'Good JavaScript and React skills'
            })

        if skill_scores.get('communication', 0) >= 2 and skill_scores.get('leadership', 0) >= 2:
            recommendations.append({
                'role': 'Project Manager',
                'confidence': 0.6,
                'reason': 'Strong soft skills for management roles'
            })

        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
