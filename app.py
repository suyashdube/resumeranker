from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import os
import re
from typing import List
import PyPDF2
from docx import Document
from dotenv import load_dotenv
import logging
import google.generativeai as genai  # Import Google Generative AI SDK

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Helper function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")

# Helper function to extract text from DOCX
def extract_text_from_docx(file):
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise HTTPException(status_code=400, detail="Failed to extract text from DOCX.")

# Extract text from file (PDF or DOCX)
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        return extract_text_from_pdf(file.file)
    elif file.filename.endswith(".docx"):
        return extract_text_from_docx(file.file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX are supported.")

# Preprocess text to improve readability
def preprocess_text(text: str):
    # Remove extra whitespace and normalize formatting
    text = " ".join(text.split())
    # Remove special characters (optional)
    text = re.sub(r"[^\w\s.,-]", "", text)
    return text

# Extract ranking criteria from job description
@app.post("/extract-criteria", response_model=dict)
async def extract_criteria(file: UploadFile = File(...)):
    try:
        # Extract text from the uploaded file
        text = extract_text(file)
        text = preprocess_text(text)

        # Use Google Generative AI to extract ranking criteria
        model = genai.GenerativeModel("gemini-pro")  # Use Gemini Pro model
        response = model.generate_content(
            f"Extract key ranking criteria from the job description. Return only a list of criteria as strings.\n\nJob Description:\n{text}"
        )

        # Parse the response
        criteria = response.text.strip().split("\n")
        return {"criteria": criteria}
    except Exception as e:
        logger.error(f"Error extracting criteria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Score resumes against extracted criteria
# Score resumes against extracted criteria
@app.post("/score-resumes")
async def score_resumes(criteria: List[str] = Form(...), files: List[UploadFile] = File(...)):
    try:
        results = []
        for file in files:
            # Extract text from the resume
            text = extract_text(file)
            text = preprocess_text(text)

            # Score the resume against each criterion
            scores = []
            for criterion in criteria:
                model = genai.GenerativeModel("gemini-pro")  # Use Gemini Pro model
                response = model.generate_content(
                    f"Score the resume based on the criterion: {criterion}. Return only a single integer score between 0 and 5, with no additional text.\n\nResume:\n{text}"
                )

                # Parse the response to extract the score
                try:
                    # Extract the first integer from the response
                    score = int(re.search(r"\d+", response.text).group())
                    scores.append(score)
                except (ValueError, AttributeError):
                    # If parsing fails, default to 0
                    scores.append(0)

            # Calculate total score
            total_score = sum(scores)
            results.append({
                "Candidate Name": file.filename,
                **{criterion: score for criterion, score in zip(criteria, scores)},
                "Total Score": total_score
            })

        # Convert results to a DataFrame and save as CSV
        df = pd.DataFrame(results)
        df.to_csv("scores.csv", index=False)

        # Return the CSV file
        return FileResponse("scores.csv", media_type="text/csv", filename="scores.csv")
    except Exception as e:
        logger.error(f"Error scoring resumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)