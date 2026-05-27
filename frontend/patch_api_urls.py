from pathlib import Path
import re

root = Path('.')
src = root / 'src'

files = [
    src / 'pages' / 'Login.jsx',
    src / 'pages' / 'Signup.jsx',
    src / 'pages' / 'Profile.jsx',
    src / 'pages' / 'Dashboard.jsx',
    src / 'pages' / 'CompetencyQuiz.jsx',
    src / 'pages' / 'LearningPathways.jsx',
    src / 'pages' / 'MarketInsights.jsx',
    src / 'pages' / 'ResumeWizard.jsx',
    src / 'pages' / 'Settings.jsx',
    src / 'pages' / 'SkillGapAnalysis.jsx',
    src / 'components' / 'UploadAndSummary.jsx',
    src / 'pages' / 'CommunityForum.jsx',
    src / 'pages' / 'Certifications.jsx',
]

url_pattern = re.compile(r'(["\'`])http://localhost:5000([^"\'`]*)\1')

for path in files:
    if not path.exists():
        print(f"MISSING: {path}")
        continue

    text = path.read_text(encoding='utf-8')
    original = text

    # Remove any malformed API_BASE_URL import lines inserted inside import blocks
    text = re.sub(r'import\s*\{\s*API_BASE_URL\s*\}\s*from\s*["\"]\.\./config["\"];?\s*', '', text)

    # Ensure the helper import exists at the top of the file after other imports
    if 'API_BASE_URL' in text and 'import { API_BASE_URL } from "../config";' not in text and "import { API_BASE_URL } from '../config';" not in text:
        lines = text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith('import '):
                insert_at = i + 1
        lines.insert(insert_at, 'import { API_BASE_URL } from "../config";')
        text = '\n'.join(lines) + ('\n' if original.endswith('\n') else '')

    # Replace all localhost backend URLs with the environment-driven base URL
    text = url_pattern.sub(lambda m: f'`${{API_BASE_URL}}{m.group(2)}`', text)

    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f"Patched: {path.relative_to(root)}")
    else:
        print(f"No change: {path.relative_to(root)}")
