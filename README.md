# resumeranker

Resume Ranker is a FastAPI-based application that automates the process of ranking resumes based on job descriptions. It uses Google's Generative AI SDK (Gemini) to extract ranking criteria from job descriptions and score resumes against those criteria. The application supports PDF and DOCX files and returns the results in a structured CSV format.

## Features
Extract Ranking Criteria:
- Upload a job description (PDF or DOCX).
- Extract key ranking criteria (e.g., skills, experience, certifications) using Google's Gemini model.

Score Resumes:
- Upload multiple resumes (PDF or DOCX).
- Score each resume against the extracted criteria.
- Generate a CSV file with individual and total scores for each candidate.

User-Friendly API:
- Built with FastAPI.
- Includes Swagger UI for easy testing and documentation.

## Setup
Prerequisites:
- Python 3.8 or higher.
- A Google API key (obtain from Google AI Studio).

Install Dependencies
- Clone the repository and install the required dependencies:
  ```console
  git clone https://github.com/your-username/resume-ranker.git
  cd resume-ranker
  pip install -r requirements.txt
  ```
Set Up Environment Variables
- Create a .env file in the root directory and add your Google API key:
  ```console
  GOOGLE_API_KEY=your_google_api_key_here
  ```
## Usage
Run the Application
Start the FastAPI server:
```console
python app.py
```
The application will be available at http://127.0.0.1:8000.

Access Swagger UI
- Open your browser and go to http://127.0.0.1:8000/docs. You will see the Swagger UI with documentation for both endpoints.

TASK 1: Extract Criteria
- Use the POST /extract-criteria endpoint.
- Upload a job description file (PDF or DOCX).
- The API will return a list of extracted criteria.
  ```console
  curl -X POST "http://127.0.0.1:8000/extract-criteria" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@job_description.pdf"
  ```
  example response:
  ```console
  {
  "criteria": [
    "3 yrs of software engineering background",
    "Degree in Computer Science, ML, or related field",
    "1 yrs of experience with large language models LLMs and their practical applications"
   ]
  }
  ```
TASK 2: Score Resumes
- Use the POST /score-resumes endpoint.
- Provide the extracted criteria as a list of strings.
- Upload multiple resume files (PDF or DOCX).
- The API will return a CSV file with scores for each candidate.

Example request:
```console
curl -X POST "http://127.0.0.1:8000/score-resumes" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F 'criteria=["3 yrs of software engineering background", "Degree in Computer Science, ML, or related field", "1 yrs of experience with large language models LLMs and their practical applications"]' \
-F "files=@resume1.pdf" \
-F "files=@resume2.docx"
```
Example Response:
A CSV file (scores.csv) with the following content:
```console
Candidate Name,3 yrs of software engineering background,Degree in Computer Science, ML, or related field,1 yrs of experience with large language models LLMs and their practical applications,Total Score
resume1.pdf,5,4,3,12
resume2.docx,3,5,4,12
```

Contact info: 
Name: Suyash Dubey
email: dsuyash57@gmail.com






