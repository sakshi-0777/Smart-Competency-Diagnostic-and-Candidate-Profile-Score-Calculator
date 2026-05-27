import json
import re
from pathlib import Path
from datetime import datetime
import uuid

class ResumeWizard:
    def __init__(self):
        self.templates = self.load_templates()

    def load_templates(self):
        """Load resume templates"""
        return {
            'modern': {
                'name': 'Modern Professional',
                'sections': ['header', 'summary', 'experience', 'education', 'skills', 'projects'],
                'style': 'clean, modern design with subtle colors'
            },
            'technical': {
                'name': 'Technical Focus',
                'sections': ['header', 'skills', 'experience', 'projects', 'education', 'certifications'],
                'style': 'emphasizes technical skills and projects'
            },
            'creative': {
                'name': 'Creative Portfolio',
                'sections': ['header', 'portfolio', 'experience', 'skills', 'education'],
                'style': 'showcases creative work and visual elements'
            },
            'executive': {
                'name': 'Executive Level',
                'sections': ['header', 'executive_summary', 'experience', 'achievements', 'education', 'board_memberships'],
                'style': 'focuses on leadership and strategic achievements'
            }
        }

    def generate_resume(self, user_profile, job_title=None, template='modern'):
        """Generate a complete resume from user profile"""
        template = template or 'modern'
        template_config = self.templates.get(template, self.templates['modern'])

        resume_data = {
            'id': str(uuid.uuid4()),
            'template': template,
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }

        # Generate each section
        for section in template_config['sections']:
            resume_data['sections'][section] = self.generate_section(section, user_profile, job_title)

        # Optimize for job title if provided
        if job_title:
            resume_data = self.optimize_for_job(resume_data, job_title)

        return resume_data

    def generate_section(self, section_name, user_profile, job_title=None):
        """Generate content for a specific resume section"""
        generators = {
            'header': self.generate_header,
            'summary': self.generate_summary,
            'experience': self.generate_experience,
            'education': self.generate_education,
            'skills': self.generate_skills,
            'projects': self.generate_projects,
            'certifications': self.generate_certifications,
            'executive_summary': self.generate_executive_summary,
            'achievements': self.generate_achievements,
            'portfolio': self.generate_portfolio
        }

        generator = generators.get(section_name, lambda *args: {})
        return generator(user_profile, job_title)

    def generate_header(self, user_profile, job_title=None):
        """Generate resume header"""
        return {
            'name': user_profile.get('name', ''),
            'title': job_title or user_profile.get('current_title', 'Professional'),
            'email': user_profile.get('email', ''),
            'phone': user_profile.get('phone', ''),
            'location': user_profile.get('location', ''),
            'linkedin': user_profile.get('linkedin', ''),
            'github': user_profile.get('github', ''),
            'portfolio': user_profile.get('portfolio', '')
        }

    def generate_summary(self, user_profile, job_title=None):
        """Generate professional summary"""
        custom_summary = self.clean_text(user_profile.get('summary', ''))
        if custom_summary:
            return {
                'content': custom_summary,
                'highlights': self.generate_highlights(user_profile, job_title)
            }

        skills = user_profile.get('skill_scores', {})
        experience_years = user_profile.get('experience_years', 0)

        # Identify top skills
        top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
        skill_names = [skill for skill, _ in top_skills]

        summary = f"Experienced professional with {experience_years} years of expertise"

        if skill_names:
            summary += f" in {', '.join(skill_names)}"

        if job_title:
            summary += f", seeking {job_title} position"

        summary += ". Proven track record of delivering high-quality results and driving team success."

        return {
            'content': summary,
            'highlights': self.generate_highlights(user_profile, job_title)
        }

    def generate_highlights(self, user_profile, job_title=None):
        """Generate key highlights for summary"""
        highlights = []

        # Experience highlight
        exp_years = user_profile.get('experience_years', 0)
        if exp_years > 0:
            highlights.append(f"{exp_years}+ years of professional experience")

        # Skills highlights
        skills = user_profile.get('skill_scores', {})
        if skills:
            top_skill = max(skills.items(), key=lambda x: x[1])
            highlights.append(f"Expert in {top_skill[0].replace('_', ' ').title()}")

        # Education highlight
        education = user_profile.get('education', [])
        if education:
            latest_edu = education[0] if education else {}
            degree = latest_edu.get('degree', '')
            if degree:
                highlights.append(f"{degree} graduate")

        return highlights[:3]  # Limit to 3 highlights

    def generate_experience(self, user_profile, job_title=None):
        """Generate work experience section"""
        experiences = user_profile.get('experience', [])

        formatted_experiences = []
        for exp in experiences:
            formatted_exp = {
                'company': exp.get('company', ''),
                'position': exp.get('position', ''),
                'duration': f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}",
                'location': exp.get('location', ''),
                'responsibilities': self.format_responsibilities(exp.get('responsibilities', [])),
                'achievements': exp.get('achievements', [])
            }
            formatted_experiences.append(formatted_exp)

        return formatted_experiences

    def format_responsibilities(self, responsibilities):
        """Format job responsibilities"""
        if isinstance(responsibilities, list):
            return [self.clean_text(resp) for resp in responsibilities]
        elif isinstance(responsibilities, str):
            return [self.clean_text(line) for line in responsibilities.split('\n') if line.strip()]
        return []

    def generate_education(self, user_profile, job_title=None):
        """Generate education section"""
        education = user_profile.get('education', [])

        formatted_education = []
        for edu in education:
            formatted_edu = {
                'institution': edu.get('institution', ''),
                'degree': edu.get('degree', ''),
                'field': edu.get('field_of_study', ''),
                'graduation_year': edu.get('graduation_year', ''),
                'gpa': edu.get('gpa', ''),
                'honors': edu.get('honors', [])
            }
            formatted_education.append(formatted_edu)

        return formatted_education

    def generate_skills(self, user_profile, job_title=None):
        """Generate skills section"""
        skill_scores = user_profile.get('skill_scores', {})

        # Categorize skills
        skill_categories = {
            'Technical': [],
            'Soft Skills': [],
            'Tools & Technologies': [],
            'Languages': []
        }

        skill_mappings = {
            'python': 'Technical',
            'javascript': 'Technical',
            'java': 'Technical',
            'sql': 'Technical',
            'html': 'Technical',
            'css': 'Technical',
            'react': 'Technical',
            'node.js': 'Technical',
            'communication': 'Soft Skills',
            'leadership': 'Soft Skills',
            'teamwork': 'Soft Skills',
            'problem_solving': 'Soft Skills',
            'git': 'Tools & Technologies',
            'docker': 'Tools & Technologies'
        }

        for skill, score in skill_scores.items():
            category = skill_mappings.get(skill, 'Technical')
            level = self.score_to_level(score)
            skill_categories[category].append({
                'name': skill.replace('_', ' ').title(),
                'level': level,
                'score': score
            })

        # Remove empty categories
        return {k: v for k, v in skill_categories.items() if v}

    def score_to_level(self, score):
        """Convert numeric score to proficiency level"""
        if score >= 2.5:
            return 'Expert'
        elif score >= 1.5:
            return 'Advanced'
        elif score >= 0.5:
            return 'Intermediate'
        else:
            return 'Beginner'

    def generate_projects(self, user_profile, job_title=None):
        """Generate projects section"""
        projects = user_profile.get('projects', [])

        formatted_projects = []
        for project in projects:
            formatted_project = {
                'name': project.get('name', ''),
                'description': project.get('description', ''),
                'technologies': project.get('technologies', []),
                'url': project.get('url', ''),
                'duration': project.get('duration', ''),
                'role': project.get('role', '')
            }
            formatted_projects.append(formatted_project)

        return formatted_projects

    def generate_certifications(self, user_profile, job_title=None):
        """Generate certifications section"""
        certifications = user_profile.get('certifications', [])

        formatted_certs = []
        for cert in certifications:
            formatted_cert = {
                'name': cert.get('name', ''),
                'issuer': cert.get('issuer', ''),
                'date': cert.get('date', ''),
                'url': cert.get('url', ''),
                'expires': cert.get('expires', '')
            }
            formatted_certs.append(formatted_cert)

        return formatted_certs

    def generate_executive_summary(self, user_profile, job_title=None):
        """Generate executive summary for senior roles"""
        return self.generate_summary(user_profile, job_title)  # Similar to regular summary

    def generate_achievements(self, user_profile, job_title=None):
        """Generate achievements section"""
        achievements = user_profile.get('achievements', [])
        return achievements

    def generate_portfolio(self, user_profile, job_title=None):
        """Generate portfolio section"""
        portfolio_items = user_profile.get('portfolio', [])
        return portfolio_items

    def optimize_for_job(self, resume_data, job_title):
        """Optimize resume content for specific job"""
        # Reorder skills based on job requirements
        # Highlight relevant experience
        # Adjust summary to match job keywords

        job_keywords = self.extract_job_keywords(job_title)

        # Boost relevant skills in summary
        summary = resume_data['sections'].get('summary', {})
        if 'content' in summary:
            # Add job-relevant keywords to summary
            relevant_skills = [skill for skill in job_keywords if skill in str(resume_data)]
            if relevant_skills:
                summary['content'] += f" Specializing in {', '.join(relevant_skills[:2])}."

        return resume_data

    def extract_job_keywords(self, job_title):
        """Extract relevant keywords for job title"""
        job_keywords = {
            'software engineer': ['python', 'javascript', 'java', 'algorithms', 'system design'],
            'data scientist': ['python', 'machine learning', 'statistics', 'data analysis'],
            'frontend developer': ['javascript', 'react', 'html', 'css', 'ui/ux'],
            'backend developer': ['python', 'java', 'sql', 'api', 'database'],
            'product manager': ['product strategy', 'agile', 'analytics', 'stakeholder management']
        }

        job_lower = job_title.lower()
        for job_key, keywords in job_keywords.items():
            if job_key in job_lower:
                return keywords

        return ['communication', 'problem solving', 'teamwork']

    def clean_text(self, text):
        """Clean and format text for resume"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Capitalize first letter of sentences
        text = re.sub(r'(^|[.!?]\s*)(\w)', lambda m: m.group(1) + m.group(2).upper(), text)
        return text

    def export_resume(self, resume_data, format='json'):
        """Export resume in different formats"""
        if format == 'json':
            return json.dumps(resume_data, indent=2)
        elif format == 'text':
            return self.resume_to_text(resume_data)
        elif format == 'markdown':
            return self.resume_to_markdown(resume_data)
        else:
            return json.dumps(resume_data)

    def resume_to_text(self, resume_data):
        """Convert resume to plain text format"""
        text = ""

        # Header
        header = resume_data['sections'].get('header', {})
        text += f"{header.get('name', '')}\n"
        text += f"{header.get('title', '')}\n"
        text += f"{header.get('email', '')} | {header.get('phone', '')}\n\n"

        # Summary
        summary = resume_data['sections'].get('summary', {})
        if summary.get('content'):
            text += "PROFESSIONAL SUMMARY\n"
            text += f"{summary['content']}\n\n"

        # Experience
        experience = resume_data['sections'].get('experience', [])
        if experience:
            text += "PROFESSIONAL EXPERIENCE\n"
            for exp in experience:
                text += f"{exp.get('position', '')} at {exp.get('company', '')}\n"
                text += f"{exp.get('duration', '')}\n"
                for resp in exp.get('responsibilities', []):
                    text += f"• {resp}\n"
                text += "\n"

        # Skills
        skills = resume_data['sections'].get('skills', {})
        if skills:
            text += "SKILLS\n"
            for category, skill_list in skills.items():
                text += f"{category}:\n"
                for skill in skill_list:
                    text += f"• {skill['name']} ({skill['level']})\n"
                text += "\n"

        return text

    def resume_to_markdown(self, resume_data):
        """Convert resume to markdown format"""
        md = "# Resume\n\n"

        # Header
        header = resume_data['sections'].get('header', {})
        md += f"## {header.get('name', '')}\n"
        md += f"**{header.get('title', '')}**\n\n"
        md += f"📧 {header.get('email', '')} | 📱 {header.get('phone', '')}\n\n"

        # Summary
        summary = resume_data['sections'].get('summary', {})
        if summary.get('content'):
            md += "## Professional Summary\n\n"
            md += f"{summary['content']}\n\n"

        # Experience
        experience = resume_data['sections'].get('experience', [])
        if experience:
            md += "## Professional Experience\n\n"
            for exp in experience:
                md += f"### {exp.get('position', '')}\n"
                md += f"**{exp.get('company', '')}** | {exp.get('duration', '')}\n\n"
                for resp in exp.get('responsibilities', []):
                    md += f"- {resp}\n"
                md += "\n"

        return md
