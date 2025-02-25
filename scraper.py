import requests
from bs4 import BeautifulSoup

def scrape_jobs():
    url = "https://www.example.com/jobs"  # Replace with an actual job board URL
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        for job_elem in soup.find_all('div', class_='job'):
            title = job_elem.find('h2').get_text(strip=True) if job_elem.find('h2') else "Unknown Title"
            company = job_elem.find('span', class_='company').get_text(strip=True) if job_elem.find('span', class_='company') else "Unknown Company"
            jobs.append({'title': title, 'company': company})
        return jobs
    except Exception as e:
        return [{"error": str(e)}]
