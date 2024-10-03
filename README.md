# ML_backend_assignment

# FastAPI OCR Document QA Application

This is a FastAPI application that allows users to upload files, perform Optical Character Recognition (OCR) on the documents, and ask questions related to the content of the uploaded files. The application also implements user authentication.

## Features

- **User Authentication**: Users can sign up and log in to access the application.
- **File Upload**: Supports multiple file formats including `.png`, `.jpg`, `.jpeg`, `.pdf`, `.txt`, and `.docx`.
- **OCR Processing**: Extracts text from uploaded documents using OCR techniques.
- **Question Answering**: Users can ask questions about the content of the uploaded documents.

## Requirements

- Python 3.7 or higher
- FastAPI
- Uvicorn
- Pillow
- PyPDF2
- pytesseract
- python-docx
- langchain (including necessary components)
- other dependencies as defined in `requirements.txt`

## Installation

1. Clone the repository:
   ```git clone https://github.com/harshavardhan198/ML_backend_assignment.git```
   ```cd ML_backend_assignment```

2. Install the required dependencies:
    pip install -r requirements.txt

3. Set up Tesseract OCR:
    brew install tesseract

4. Create a .env file in the root directory with your respective api key

## Usage
Start the FastAPI server:
```uvicorn app:app --reload```
Open your browser and navigate to http://127.0.0.1:8000/docs to access the interactive API documentation provided by FastAPI.

## Endpoints
### POST /signup: Create a new user account.

#### Body: 
{"email": "user@example.com", "password": "your_password"}

### POST /login: Authenticate a user and obtain access/refresh tokens.

#### Body: {"username": "user@example.com", "password": "your_password"}

### POST /file/upload: Upload a file for OCR processing.

#### Body: File upload
##### Headers: Authorization: Bearer {your_access_token}

### POST /ask: Ask a question related to the uploaded document.

#### Body: {"question": "Your question here"}
##### Headers: Authorization: Bearer {your_access_token}


## License
This project is licensed under the MIT License - see the LICENSE file for details.





   
