import re

class JobMatcher:
    def match_jobs(self, resume_text, jobs):
        resume_text_lower = resume_text.lower()
        matched_results = []
        
        # Extract potential skills/keywords from resume for comparison
        # Using a simple tokenizer 
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text_lower))
        
        for job in jobs:
            score = 0
            reasons = []
            
            # 1. Title Match (30 pts)
            # Check if job title words are in resume
            title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job['title'].lower()))
            overlap = title_words.intersection(resume_words)
            if overlap:
                match_p = len(overlap) / len(title_words)
                score += 30 * match_p
                reasons.append(f"Role match: {job['title']}")

            # 2. Skill/Tag Match (40 pts)
            job_tags = job.get('tags', [])
            matched_tags = []
            if job_tags:
                for tag in job_tags:
                    # Clean tag
                    tag_clean = tag.lower().strip()
                    if tag_clean in resume_text_lower:
                        matched_tags.append(tag)
                
                if matched_tags:
                    tag_p = len(matched_tags) / len(job_tags)
                    score += 40 * tag_p
                    reasons.append(f"Skills matched: {', '.join(matched_tags[:3])}")
            else:
                # Fallback to description analysis if no tags
                job_desc = job.get('description', '').lower()
                desc_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_desc))
                # Jaccard similarity very basic
                intersection = len(resume_words.intersection(desc_words))
                union = len(resume_words.union(desc_words))
                jaccard = intersection / union if union > 0 else 0
                score += 40 * min(1.0, jaccard * 10) # boosting jaccard which is usually low

            # 3. Location Match (bonus 10 pts)
            # Not strictly possible without user preference, assume if 'remote' in both it's good
            if 'remote' in job['location'].lower() and 'remote' in resume_text_lower:
                 score += 10
                 reasons.append("Remote compatible")

            # Final Score normalization
            # Baseline compatibility boost if we have some match
            if score > 0:
                 score += 20 # Base fit
            
            final_match_score = min(98, int(score))
            
            # Lower threshold to ensure users see results even if weak match
            if final_match_score > 15:
                job['match_score'] = final_match_score
                job['match_reason'] = reasons if reasons else ["General fit based on profile"]
                matched_results.append(job)
            
        # Sort by match score descending
        matched_results.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_results
