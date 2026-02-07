import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resume_matching.parser import ResumeParser
from resume_matching.scorer import ResumeScorer

def test_resume_flow():
    print("Running Resume Flow Test...")
    
    # Create a dummy resume text if file doesn't exist
    # In a real scenario we'd use a sample pdf, but here we test the logic functions
    
    dummy_text = """
    John Doe
    john.doe@example.com
    (555) 123-4567
    
    Summary
    Experienced Software Engineer with 5 years of experience in Python and Flask.
    
    Skills
    Python, Java, Git, SQL, Flask
    
    Experience
    Senior Developer at Tech Co.
    Developed web applications using Flask and React.
    """
    
    print("\n--- 1. Testing Parser Logic (Mocked Text) ---")
    parser = ResumeParser()
    details = parser.extract_details(dummy_text)
    print("Extracted Details:", details)
    
    assert details['email'] == 'john.doe@example.com'
    assert 'Python' in details['skills']
    
    print("\n--- 2. Testing Scorer Logic ---")
    scorer = ResumeScorer()
    score_data = scorer.calculate_score(dummy_text)
    print("Score Data:", score_data)
    
    suggestions = scorer.generate_suggestions(score_data)
    print("Suggestions:", suggestions)
    
    assert score_data['total_score'] > 0
    assert len(suggestions) > 0
    
    print("\n✅ Test Passed!")

if __name__ == "__main__":
    test_resume_flow()
