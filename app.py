import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from resume_matching.parser import ResumeParser
from resume_matching.scorer import ResumeScorer
from resume_matching.scraper import JobScraper
from resume_matching.matcher import JobMatcher

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jobs')
def jobs_page():
    return render_template('jobs.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    query = request.args.get('query', '')
    scraper = JobScraper()
    jobs = scraper.scrape_jobs(query)
    return jsonify(jobs)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # 1. Parse
            parser = ResumeParser()
            resume_text = parser.extract_text(filepath, filename.split('.')[-1])
            resume_data = parser.extract_details(resume_text)
            
            # 2. Score
            scorer = ResumeScorer()
            score_data = scorer.calculate_score(resume_text)
            suggestions = scorer.generate_suggestions(score_data)
            
            # 3. Scrape & Match
            scraper = JobScraper()
            # Intelligent query logic: Prioritize HARD skills for better matches
            search_query = "Software Engineer" # Fallback
            
            # Get hard skills list from scorer
            scorer = ResumeScorer() 
            hard_skills = scorer.hard_skills_db
            
            # Find first hard skill in user's skills
            for skill in resume_data['skills']:
                if skill.lower() in hard_skills:
                    search_query = skill
                    break
            else:
                # If no hard skill found, try first skill or keep default
                if len(resume_data['skills']) > 0:
                    search_query = resume_data['skills'][0]
            
            all_jobs = scraper.scrape_jobs(search_query) # Get broad list
            
            matcher = JobMatcher()
            matched_jobs = matcher.match_jobs(resume_text, all_jobs)
            
            # Fallback: If NLP matching was too strict, show raw jobs
            final_jobs = matched_jobs if matched_jobs else all_jobs
            
            return jsonify({
                'score': score_data['total_score'],
                'breakdown': score_data['breakdown'],
                'suggestions': suggestions,
                'jobs': final_jobs[:6], # Top 6 matches
                'resume_details': resume_data
            })
        except Exception as e:
            print(e)
            return jsonify({'error': 'Processing failed'}), 500

    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
