import re
from pdfminer.high_level import extract_text
import docx

class ResumeParser:
    def extract_text(self, filepath, file_ext):
        text = ""
        try:
            if file_ext == 'pdf':
                text = extract_text(filepath)
            elif file_ext == 'docx':
                doc = docx.Document(filepath)
                text = '\n'.join([para.text for para in doc.paragraphs])
            else:
                text = "" # Fallback or error
        except Exception as e:
            print(f"Error parsing file: {e}")
        return text

    def extract_details(self, text):
        details = {
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text)
        }
        return details

    def _extract_email(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text):
        # Basic phone extraction
        phone_pattern = r'(\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
        matches = re.findall(phone_pattern, text)
        # Filter matches that are too short to be phone numbers
        valid_matches = [m for m in matches if len(re.sub(r'\D', '', m)) >= 10]
        return valid_matches[0] if valid_matches else None
    
    def _extract_skills(self, text):
        # In a real app, use a predefined skill database or NLP
        # For this MVP, we look for common tech keywords
        common_skills = [
            'python', 'java', 'c++', 'javascript', 'html', 'css', 'react', 'angular', 
            'vue', 'flask', 'django', 'sql', 'mysql', 'postgresql', 'aws', 'docker', 
            'kubernetes', 'git', 'machine learning', 'data science', 'nlp', 'pandas', 
            'numpy', 'tensorflow', 'pytorch'
        ]
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.capitalize())
        return list(set(found_skills))
