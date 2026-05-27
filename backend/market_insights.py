import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import defaultdict

class MarketInsights:
    def __init__(self, job_df=None):
        self.job_df = job_df
        self.insights_cache = {}
        self.cache_expiry = timedelta(hours=24)

    def get_job_market_trends(self, location=None, timeframe='month'):
        """Get current job market trends"""
        if self.job_df is None:
            return self.generate_mock_trends()

        trends = {
            'timestamp': datetime.now().isoformat(),
            'location': location or 'Global',
            'timeframe': timeframe,
            'trending_jobs': self.get_trending_jobs(),
            'skill_demand': self.get_skill_demand(),
            'salary_insights': self.get_salary_insights(),
            'industry_growth': self.get_industry_growth(),
            'remote_work_trends': self.get_remote_work_trends()
        }

        return trends

    def get_trending_jobs(self):
        """Get trending job titles"""
        if self.job_df is None:
            return [
                {'title': 'Software Engineer', 'growth': 15.2, 'demand': 'High'},
                {'title': 'Data Scientist', 'growth': 12.8, 'demand': 'High'},
                {'title': 'Product Manager', 'growth': 8.5, 'demand': 'Medium'},
                {'title': 'UI/UX Designer', 'growth': 9.1, 'demand': 'Medium'}
            ]

        # Analyze job postings frequency
        job_counts = self.job_df['job_title'].value_counts().head(10)

        trending = []
        for job_title, count in job_counts.items():
            growth_rate = np.random.uniform(5, 20)  # Mock growth calculation
            demand_level = 'High' if count > 10 else 'Medium' if count > 5 else 'Low'

            trending.append({
                'title': job_title,
                'count': int(count),
                'growth': round(growth_rate, 1),
                'demand': demand_level
            })

        return sorted(trending, key=lambda x: x['growth'], reverse=True)

    def get_skill_demand(self):
        """Get in-demand skills analysis"""
        skills_demand = [
            {'skill': 'Python', 'demand_score': 95, 'growth': 18.5, 'industries': ['Tech', 'Finance', 'Healthcare']},
            {'skill': 'Machine Learning', 'demand_score': 92, 'growth': 22.1, 'industries': ['Tech', 'Finance']},
            {'skill': 'Cloud Computing', 'demand_score': 88, 'growth': 15.8, 'industries': ['Tech', 'All']},
            {'skill': 'Data Analysis', 'demand_score': 85, 'growth': 12.3, 'industries': ['Tech', 'Business']},
            {'skill': 'JavaScript', 'demand_score': 82, 'growth': 8.9, 'industries': ['Tech', 'E-commerce']},
            {'skill': 'Communication', 'demand_score': 78, 'growth': 6.7, 'industries': ['All']},
            {'skill': 'Project Management', 'demand_score': 75, 'growth': 9.2, 'industries': ['Business', 'Tech']},
            {'skill': 'UI/UX Design', 'demand_score': 72, 'growth': 11.4, 'industries': ['Tech', 'Design']}
        ]

        return sorted(skills_demand, key=lambda x: x['demand_score'], reverse=True)

    def get_salary_insights(self):
        """Get salary insights by role and location"""
        salary_data = {
            'Software Engineer': {
                'entry': 65000,
                'mid': 95000,
                'senior': 135000,
                'growth': 8.5
            },
            'Data Scientist': {
                'entry': 70000,
                'mid': 105000,
                'senior': 150000,
                'growth': 9.2
            },
            'Product Manager': {
                'entry': 75000,
                'mid': 115000,
                'senior': 165000,
                'growth': 7.8
            },
            'UI/UX Designer': {
                'entry': 55000,
                'mid': 80000,
                'senior': 120000,
                'growth': 6.9
            },
            'Data Analyst': {
                'entry': 55000,
                'mid': 75000,
                'senior': 105000,
                'growth': 7.1
            }
        }

        return salary_data

    def get_industry_growth(self):
        """Get industry growth projections"""
        industries = [
            {'name': 'Technology', 'growth_rate': 12.5, 'job_openings': 450000, 'trend': 'Growing'},
            {'name': 'Healthcare', 'growth_rate': 8.9, 'job_openings': 320000, 'trend': 'Growing'},
            {'name': 'Finance', 'growth_rate': 6.7, 'job_openings': 180000, 'trend': 'Stable'},
            {'name': 'E-commerce', 'growth_rate': 15.2, 'job_openings': 280000, 'trend': 'Growing'},
            {'name': 'Education', 'growth_rate': 5.4, 'job_openings': 150000, 'trend': 'Stable'},
            {'name': 'Manufacturing', 'growth_rate': 4.1, 'job_openings': 120000, 'trend': 'Declining'},
            {'name': 'Energy', 'growth_rate': 3.8, 'job_openings': 90000, 'trend': 'Stable'}
        ]

        return sorted(industries, key=lambda x: x['growth_rate'], reverse=True)

    def get_remote_work_trends(self):
        """Get remote work availability trends"""
        return {
            'overall_remote_percentage': 35.2,
            'by_role': {
                'Software Engineer': 65.8,
                'Data Scientist': 58.3,
                'Product Manager': 45.7,
                'Designer': 52.1,
                'Marketing': 38.9
            },
            'by_industry': {
                'Technology': 62.5,
                'Finance': 42.3,
                'Healthcare': 28.7,
                'Education': 35.1
            },
            'trending': 'Increasing remote work opportunities'
        }

    def get_personalized_insights(self, user_profile):
        """Get personalized market insights based on user profile"""
        user_skills = user_profile.get('skill_scores', {})
        user_experience = user_profile.get('experience_years', 0)

        insights = {
            'skill_market_value': self.calculate_skill_market_value(user_skills),
            'career_opportunities': self.get_career_opportunities(user_skills, user_experience),
            'salary_potential': self.calculate_salary_potential(user_skills, user_experience),
            'skill_gaps_market': self.identify_market_skill_gaps(user_skills),
            'next_best_roles': self.suggest_next_roles(user_profile)
        }

        return insights

    def calculate_skill_market_value(self, user_skills):
        """Calculate market value of user's skills"""
        skill_values = {
            'python': 95,
            'machine_learning': 98,
            'javascript': 85,
            'react': 82,
            'sql': 78,
            'communication': 75,
            'leadership': 80,
            'project_management': 77,
            'data_analysis': 88,
            'ui_ux': 76
        }

        total_value = 0
        skill_count = 0

        for skill, level in user_skills.items():
            if skill in skill_values:
                # Value decreases with lower proficiency
                value = skill_values[skill] * (level / 3.0)  # Normalize to 0-3 scale
                total_value += value
                skill_count += 1

        if skill_count == 0:
            return 0

        return round(total_value / skill_count, 1)

    def get_career_opportunities(self, user_skills, experience_years):
        """Get career opportunities based on skills and experience"""
        opportunities = []

        # Define career paths and their skill requirements
        career_paths = {
            'Software Engineer': {
                'required_skills': ['python', 'javascript', 'java'],
                'min_experience': 0,
                'market_demand': 'High'
            },
            'Data Scientist': {
                'required_skills': ['python', 'machine_learning', 'data_analysis'],
                'min_experience': 1,
                'market_demand': 'High'
            },
            'Product Manager': {
                'required_skills': ['communication', 'project_management', 'leadership'],
                'min_experience': 2,
                'market_demand': 'Medium'
            },
            'Frontend Developer': {
                'required_skills': ['javascript', 'react', 'ui_ux'],
                'min_experience': 0,
                'market_demand': 'High'
            },
            'Data Analyst': {
                'required_skills': ['sql', 'data_analysis', 'python'],
                'min_experience': 0,
                'market_demand': 'Medium'
            }
        }

        for career, requirements in career_paths.items():
            if experience_years >= requirements['min_experience']:
                # Calculate match score
                required_skills = requirements['required_skills']
                user_skill_levels = [user_skills.get(skill, 0) for skill in required_skills]
                avg_skill_level = sum(user_skill_levels) / len(user_skill_levels) if user_skill_levels else 0

                match_score = min(100, avg_skill_level * 33.33)  # Convert to percentage

                opportunities.append({
                    'career': career,
                    'match_score': round(match_score, 1),
                    'market_demand': requirements['market_demand'],
                    'required_experience': requirements['min_experience']
                })

        return sorted(opportunities, key=lambda x: x['match_score'], reverse=True)

    def calculate_salary_potential(self, user_skills, experience_years):
        """Calculate potential salary range based on skills and experience"""
        base_salaries = {
            'Software Engineer': {'entry': 65000, 'mid': 95000, 'senior': 135000},
            'Data Scientist': {'entry': 70000, 'mid': 105000, 'senior': 150000},
            'Product Manager': {'entry': 75000, 'mid': 115000, 'senior': 165000},
            'Frontend Developer': {'entry': 55000, 'mid': 80000, 'senior': 120000}
        }

        # Determine experience level
        if experience_years < 2:
            level = 'entry'
        elif experience_years < 5:
            level = 'mid'
        else:
            level = 'senior'

        # Calculate skill bonus
        skill_bonus = sum(user_skills.values()) * 2000  # $2000 per skill level

        potential = {}
        for role, salaries in base_salaries.items():
            base_salary = salaries[level]
            total_potential = base_salary + skill_bonus
            potential[role] = {
                'base': base_salary,
                'with_skills': round(total_potential),
                'level': level
            }

        return potential

    def identify_market_skill_gaps(self, user_skills):
        """Identify skills that are in high demand but user lacks"""
        high_demand_skills = ['machine_learning', 'cloud_computing', 'data_analysis', 'ai_ethics']

        gaps = []
        for skill in high_demand_skills:
            if user_skills.get(skill, 0) < 1.5:  # Below intermediate level
                gaps.append({
                    'skill': skill.replace('_', ' ').title(),
                    'current_level': user_skills.get(skill, 0),
                    'market_importance': 'High',
                    'learning_priority': 'High'
                })

        return gaps

    def suggest_next_roles(self, user_profile):
        """Suggest next career moves based on profile"""
        current_skills = user_profile.get('skill_scores', {})
        experience_years = user_profile.get('experience_years', 0)

        suggestions = []

        # Career progression logic
        if current_skills.get('python', 0) >= 2 and experience_years >= 2:
            if current_skills.get('machine_learning', 0) < 2:
                suggestions.append({
                    'role': 'Machine Learning Engineer',
                    'reason': 'Strong Python foundation, add ML expertise',
                    'required_skills': ['machine_learning', 'tensorflow', 'statistics'],
                    'time_to_transition': '6-12 months'
                })

        if current_skills.get('javascript', 0) >= 2 and experience_years >= 1:
            suggestions.append({
                'role': 'Full Stack Developer',
                'reason': 'Frontend expertise, add backend skills',
                'required_skills': ['node.js', 'sql', 'api_design'],
                'time_to_transition': '3-6 months'
            })

        if current_skills.get('communication', 0) >= 2 and experience_years >= 3:
            suggestions.append({
                'role': 'Technical Project Manager',
                'reason': 'Communication skills and experience qualify for management',
                'required_skills': ['project_management', 'agile', 'leadership'],
                'time_to_transition': '6-9 months'
            })

        return suggestions

    def generate_mock_trends(self):
        """Generate mock market trends for testing"""
        return {
            'timestamp': datetime.now().isoformat(),
            'location': 'Global',
            'timeframe': 'month',
            'trending_jobs': [
                {'title': 'AI Engineer', 'growth': 25.5, 'demand': 'Very High'},
                {'title': 'Cloud Architect', 'growth': 18.2, 'demand': 'High'},
                {'title': 'Data Engineer', 'growth': 15.8, 'demand': 'High'},
                {'title': 'DevOps Engineer', 'growth': 14.3, 'demand': 'High'}
            ],
            'skill_demand': [
                {'skill': 'Artificial Intelligence', 'demand_score': 98, 'growth': 28.5},
                {'skill': 'Cloud Computing', 'demand_score': 95, 'growth': 22.1},
                {'skill': 'Cybersecurity', 'demand_score': 93, 'growth': 19.8}
            ],
            'industry_growth': [
                {'name': 'Artificial Intelligence', 'growth_rate': 35.2},
                {'name': 'Cloud Computing', 'growth_rate': 28.7},
                {'name': 'Cybersecurity', 'growth_rate': 24.1}
            ]
        }
