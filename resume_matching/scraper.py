import requests
import feedparser
import time
from datetime import datetime
import json
import os
import urllib.parse

class JobScraper:
    def __init__(self):
        self.cache_file = 'jobs_cache_v3.json'
        self.cache_duration = 3600
        # Target specific companies requested by user
        self.target_companies = [
            "Infosys", "Wipro", "TCS", "HCL", "Accenture", 
            "Cognizant", "Google", "Microsoft", "Amazon", 
            "Oracle", "IBM"
        ]

    def scrape_jobs(self, query):
        all_jobs = self._load_cache()
        
        if not all_jobs:
            print("Fetching corporate jobs...")
            all_jobs = []
            
            # 1. Fetch from RemoteOK (Good API for tech/startups, sometimes big corp)
            remote_jobs = self.fetch_remoteok()
            all_jobs.extend(remote_jobs)

            # 2. Fetch specific Company Jobs via Google News RSS (Aggregator Trick)
            # Since we can't scrape career pages directly without Selenium/blocking,
            # this finds active listings on aggregators (LinkedIn, Indeed, etc.) via News/Search RSS
            corp_jobs = self.fetch_corporate_jobs()
            all_jobs.extend(corp_jobs)

            self._save_cache(all_jobs)
        
        # Filter logic
        filtered_jobs = []
        q = query.lower() if query else ""
        
        for job in all_jobs:
            # If query exists, match it (strict filter)
            if q:
                if q not in job['title'].lower() and q not in str(job['tags']).lower() and q not in job['company'].lower():
                    continue
            filtered_jobs.append(job)
        
        # Fallback: If strict filter killed everything, return ALL jobs so the NLP matcher can try its best
        if not filtered_jobs and all_jobs:
            return all_jobs
            
        return filtered_jobs

    def fetch_corporate_jobs(self):
        jobs = []
        # Construct a targeted RSS for big companies in India/Global
        # Using "intitle:hiring" or "intitle:job" to be more specific
        companies_str = " OR ".join(f'"{c}"' for c in self.target_companies)
        # q=hiring + company + when:3d (last 3 days only for freshness)
        rss_url = f"https://news.google.com/rss/search?q=(hiring OR job) AND ({urllib.parse.quote(companies_str)}) when:7d&hl=en-IN&gl=IN&ceid=IN:en"
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                title = entry.title
                company = "Unknown"
                
                # Identify company
                for c in self.target_companies:
                    if c.lower() in title.lower():
                        company = c
                        break
                
                # Date Parsing & Filtering (Critical for "Real Data")
                published_time = entry.parsed_published_time
                if published_time:
                    dt = datetime.fromtimestamp(time.mktime(published_time))
                    days_ago = (datetime.now() - dt).days
                    if days_ago > 7: continue # Skip old news
                    date_str = dt.strftime("%Y-%m-%d")
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")

                if company != "Unknown":
                    jobs.append({
                        'title': title.split('-')[0].strip(),
                        'company': company,
                        'location': 'Multiple Locations',
                        'url': entry.link,
                        'description': entry.summary,
                        'date': date_str,
                        'tags': [company, 'Corporate', 'Fresh'],
                        'source': 'Corporate Feed',
                        'logo': self._get_logo_url(company)
                    })
        except Exception as e:
            print(f"Error fetching corporate feed: {e}")
            
        return jobs

    def fetch_remoteok(self):
        jobs = []
        url = "https://remoteok.com/api"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data[1:]: 
                    title = item.get('position', '')
                    if not title: continue
                    
                    # Date Filter
                    date_str = item.get('date', '').split('T')[0]
                    try:
                        job_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if (datetime.now() - job_date).days > 14: continue # Skip > 2 weeks old
                    except: continue # Skip if bad date

                    company = item.get('company', '')
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': item.get('location', 'Remote'),
                        'url': item.get('url'),
                        'description': item.get('description', ''),
                        'date': date_str,
                        'tags': item.get('tags', []),
                        'source': 'RemoteOK',
                        'logo': item.get('company_logo') or self._get_logo_url(company)
                    })
        except: pass
        return jobs

    def _get_logo_url(self, company_name):
        # Clearbit Logo API is free and reliable
        domain = f"{company_name.lower().replace(' ', '')}.com"
        return f"https://logo.clearbit.com/{domain}"

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            if time.time() - os.path.getmtime(self.cache_file) < self.cache_duration:
                try:
                    with open(self.cache_file, 'r') as f: return json.load(f)
                except: return None
        return None

    def _save_cache(self, jobs):
        try:
            with open(self.cache_file, 'w') as f: json.dump(jobs, f)
        except: pass
