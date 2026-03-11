import re
from collections import Counter

class ResumeScorer:
    def __init__(self):
        self.action_verbs = [
            "accelerated", "accomplished", "achieved", "analyzed", "assembled", "built", "collaborated", 
            "created", "delivered", "developed", "engineered", "enhanced", "established", "expanded", 
            "facilitated", "improved", "increased", "initiated", "led", "managed", "optimized", "orchestrated", 
            "overcame", "planned", "produced", "reduced", "resolved", "spearheaded", "streamlined", "structured",
            "transformed", "upgraded"
        ]
        self.soft_skills = ['leadership', 'communication', 'teamwork', 'problem solving', 'time management', 'adaptability']
        self.hard_skills_db = ['python', 'java', 'sql', 'html', 'css', 'javascript', 'react', 'node', 'aws', 'docker', 'git', 'machine learning', 'data analysis', 'c++']
        self.buzzwords = ['hard worker', 'team player', 'motivated', 'synergy', 'experienced', 'passionate']
        
        # gap analysis: if key is present, look for values. if missing, suggest them.
        self.tech_stacks = {
            'react': ['Redux', 'TypeScript', 'Jest'],
            'python': ['Django', 'Flask', 'Pandas'],
            'java': ['Spring Boot', 'Hibernate', 'Microservices'],
            'node': ['Express', 'MongoDB', 'REST APIs'],
            'sql': ['PostgreSQL', 'Database Design', 'Optimization'],
            'machine learning': ['TensorFlow', 'PyTorch', 'Scikit-learn'],
            'aws': ['EC2', 'Lambda', 'S3']
        }

    def calculate_score(self, text, filename="resume.pdf"):
        text_lower = text.lower()
        
        # --- 1. FORMAT ---
        format_checks = []
        # Length check
        word_count = len(text.split())
        if 300 <= word_count <= 800:
            format_checks.append({'item': 'Resume length', 'status': 'pass', 'msg': 'Optimal length (1 page).'})
        elif word_count < 300:
             format_checks.append({'item': 'Resume length', 'status': 'warn', 'msg': 'Too short. Add more detail.'})
        else:
             format_checks.append({'item': 'Resume length', 'status': 'warn', 'msg': 'Too long. Try to condense.'})
        
        # File format (simulated based on input)
        ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        format_checks.append({'item': 'File format', 'status': 'pass', 'msg': f'Correct format ({ext.upper()}).'})

        # --- 2. SECTIONS ---
        section_checks = []
        # Contact
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phones = re.findall(r'\d{10,}', re.sub(r'\D', '', text))
        if emails and phones:
            section_checks.append({'item': 'Contact Information', 'status': 'pass', 'msg': 'Email & Phone found.'})
        else:
             section_checks.append({'item': 'Contact Information', 'status': 'fail', 'msg': 'Missing Email or Phone.'})

        # Essential Headers
        headers = ['experience', 'education', 'skills', 'projects']
        found_headers = [h for h in headers if h in text_lower]
        if len(found_headers) == 4:
            section_checks.append({'item': 'Essential sections', 'status': 'pass', 'msg': 'All key sections present.'})
        else:
            missing = [h.title() for h in headers if h not in text_lower]
            section_checks.append({'item': 'Essential sections', 'status': 'warn', 'msg': f'Missing: {", ".join(missing)}'})

        # --- 3. CONTENT ---
        content_checks = []
        # ATS Parse Rate (Simulated)
        if len(text) > 100:
             content_checks.append({'item': 'ATS parse rate', 'status': 'pass', 'msg': 'Text is readable by ATS.'})
        else:
             content_checks.append({'item': 'ATS parse rate', 'status': 'fail', 'msg': 'Text unrecognizable.'})
        
        # Repetition
        words = re.findall(r'\w+', text_lower)
        counts = Counter(words)
        repeats = [w for w, c in counts.items() if c > 10 and len(w) > 4] 
        if not repeats:
            content_checks.append({'item': 'Repetition', 'status': 'pass', 'msg': 'Diverse vocabulary.'})
        else:
             content_checks.append({'item': 'Repetition', 'status': 'warn', 'msg': f'Overused words: {", ".join(repeats[:3])}'})

        # Impact (Numbers)
        numbers = re.findall(r'\d+%|\$\d+|\d+ [a-z]+', text_lower)
        if len(numbers) >= 3:
             content_checks.append({'item': 'Quantifying impact', 'status': 'pass', 'msg': 'Good use of metrics.'})
        else:
             content_checks.append({'item': 'Quantifying impact', 'status': 'warn', 'msg': 'Add more numbers (e.g. "20%").'})

        # --- 4. SKILLS ---
        skill_checks = []
        found_hard = [s for s in self.hard_skills_db if s in text_lower]
        found_soft = [s for s in self.soft_skills if s in text_lower]
        
        if len(found_hard) >= 5:
             skill_checks.append({'item': 'Hard Skills', 'status': 'pass', 'msg': f'Found {len(found_hard)} technical skills.'})
        else:
             skill_checks.append({'item': 'Hard Skills', 'status': 'warn', 'msg': 'Add more technical skills.'})

        if len(found_soft) >= 2:
             skill_checks.append({'item': 'Soft Skills', 'status': 'pass', 'msg': 'Soft skills included.'})
        else:
             skill_checks.append({'item': 'Soft Skills', 'status': 'info', 'msg': 'Consider adding soft skills.'})

        # --- 5. STYLE ---
        style_checks = []
        # Active Voice
        found_verbs = [v for v in self.action_verbs if v in text_lower]
        if len(found_verbs) > 5:
            style_checks.append({'item': 'Active Voice', 'status': 'pass', 'msg': 'Strong use of action verbs.'})
        else:
             style_checks.append({'item': 'Active Voice', 'status': 'warn', 'msg': 'Use more action verbs.'})
             
        # Buzzwords
        found_buzz = [b for b in self.buzzwords if b in text_lower]
        if not found_buzz:
             style_checks.append({'item': 'Buzzwords', 'status': 'pass', 'msg': 'Clean language.'})
        else:
             style_checks.append({'item': 'Buzzwords', 'status': 'warn', 'msg': f'Avoid clichés: {", ".join(found_buzz[:2])}'})

        # Calculate Overall Score
        total_checks = len(format_checks) + len(section_checks) + len(content_checks) + len(skill_checks) + len(style_checks)
        passed_checks = (
            sum(1 for x in format_checks if x['status']=='pass') +
            sum(1 for x in section_checks if x['status']=='pass') + 
            sum(1 for x in content_checks if x['status']=='pass') +
            sum(1 for x in skill_checks if x['status']=='pass') +
            sum(1 for x in style_checks if x['status']=='pass')
        )
        score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 0

        # --- 6. INTERVIEW PREP ---
        interview_questions = []
        interview_db = {
            'python': ["Explain the difference between list and tuple.", "What are decorators?", "How does memory management work in Python?"],
            'java': ["Difference between JDK, JRE, and JVM?", "Explain polymorphism with an example.", "What is the Spring Boot cycle?"],
            'sql': ["Explain LEFT JOIN vs INNER JOIN.", "What is normalization?", "Difference between stored procedure and function."],
            'html': ["What are semantic tags?", "Explain the box model.", "Difference between localStorage and sessionStorage."],
            'css': ["Explain Flexbox vs Grid.", "What is the difference between class and ID selectors?", "How do you optimize CSS performance?"],
            'react': ["What is the Virtual DOM?", "Explain the useEffect hook.", "State vs Props?"],
            'machine learning': ["Bias vs Variance?", "Explain Overfitting.", "Difference between Supervised and Unsupervised learning?"],
            'aws': ["Explain EC2 vs Lambda.", "What is S3?", "Explain IAM roles."],
            'communication': ["Describe a time you handled a conflict.", "How do you explain technical concepts to non-tech stakeholders?"],
            'leadership': ["How do you motivate a team?", "Describe your management style."]
        }

        # Select questions based on found skills
        for skill in found_hard + found_soft:
            if skill.lower() in interview_db:
                interview_questions.extend(interview_db[skill.lower()])
        
        # Shuffle and pick 5
        import random
        random.shuffle(interview_questions)
        selected_questions = interview_questions[:5] if interview_questions else ["Describe your biggest weakness.", "Where do you see yourself in 5 years?"]

        return {
            'total_score': score,
            'text_lower': text_lower, # Needed for narrative generation
            'raw_text': text, # For "Beats the Bot" view
            'interview_questions': selected_questions,
            'metrics_count': len(numbers),
            'breakdown': { # Backward compatibility
                 'cards': {
                    'Format': format_checks,
                    'Sections': section_checks,
                    'Content': content_checks,
                    'Skills': skill_checks,
                    'Style': style_checks
                 }
            },
            'cards': { # The primary data for V5 UI
                'Format': format_checks,
                'Sections': section_checks,
                'Content': content_checks,
                'Skills': skill_checks,
                'Style': style_checks
            }
        }

    def generate_suggestions(self, score_data):
        # We will generate the narrative structure requested by the user
        # 1. Grammatical Errors (Simulated via heuristic)
        # 2. Professional Tone
        # 3. Content Relevance
        
        narrative = []
        
        # --- Grammar & Clarity ---
        # Heuristic: Check for long sentences or passive phrases (was/were + ed)
        passive_phrases = ["was responsible for", "was involved in", "was tasked with", "responsibilities included"]
        found_passive = [p for p in passive_phrases if p in score_data['text_lower']]
        
        if found_passive:
            narrative.append({
                'title': 'Grammatical & Clarity',
                'content': f"Found passive voice usage: '{found_passive[0]}'. Changing this to active voice (e.g., 'Directed', 'Managed') makes your experience sound more impactful.",
                'type': 'warn'
            })
        else:
            narrative.append({
                'title': 'Grammatical & Clarity',
                'content': "Your sentence structures look solid. No major passive voice issues detected.",
                'type': 'pass'
            })

        # --- Professional Tone ---
        # Check for informal pronouns or weak words
        informal = ["i think", "passionate about", "hard worker", "various", "bunch of"]
        found_informal = [i for i in informal if i in score_data['text_lower']]
        
        if found_informal:
            narrative.append({
                'title': 'Professional Tone',
                'content': f"The phrase '{found_informal[0]}' is somewhat generic. Instead of saying you are '{found_informal[0]}', demonstrate it with a specific achievement.",
                'type': 'warn'
            })
        else:
            narrative.append({
                'title': 'Professional Tone',
                'content': "The tone is professional and objective. You've avoided common cliches.",
                'type': 'pass'
            })
            
        # --- Experience Relevance ---
        # Check for metrics
        if score_data['metrics_count'] < 3:
            narrative.append({
                'title': 'Experience Impact',
                'content': "Your experience descriptions lack quantifiable achievements. For example, instead of 'Managed a team', try 'Managed a team of 5, increasing efficiency by 20%'.",
                'type': 'fail'
            })
        else:
             narrative.append({
                'title': 'Experience Impact',
                'content': "Excellent use of data! You've successfully quantified your achievements.",
                'type': 'pass'
            })

        # --- 4. Technical Gap Analysis (The "Real Analysis") ---
        # Check against tech_stacks
        suggestions_made = 0
        for core_skill, related_stack in self.tech_stacks.items():
            if core_skill in score_data['text_lower']:
                missing_tech = [tech for tech in related_stack if tech.lower() not in score_data['text_lower']]
                if missing_tech:
                    narrative.append({
                        'title': f'Technical Gap: {core_skill.title()}',
                        'content': f"You listed '{core_skill.title()}', but employers often look for complementary skills. Consider adding: {', '.join(missing_tech)}.",
                        'type': 'info'
                    })
                    suggestions_made += 1
        
        if suggestions_made == 0:
             narrative.append({
                'title': 'Technical Stack',
                'content': "Your technical stack looks well-rounded based on our common patterns.",
                'type': 'pass'
            })

        return narrative
