# AI-Based Digital Repository & Report Intelligence System  
### QR Report System – NSTL

---

## 📌 Project Overview

The **AI-Based Digital Repository & Report Intelligence System** is a secure, LAN-based platform developed for the QR Division (NSTL) to digitize, store, manage, and intelligently retrieve technical reports.

The system centralizes physical and digital reports, enables OCR-based text extraction, generates AI-powered summaries, and provides role-based access control for secure internal usage.

---

## 🎯 Key Objectives

- Digitize legacy paper reports
- Centralize document storage
- Enable OCR-based searchable text
- Generate AI-powered report summaries
- Support keyword-based search
- Enforce role-based access control (RBAC)
- Operate within a secure LAN environment

---

## 🏗️ System Architecture

Upload → File Storage → OCR → AI Summary → MongoDB → Search

### Components

- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Flask (Python)
- Database: MongoDB
- OCR Engine: Tesseract OCR
- AI Engine: Hugging Face Transformers (DistilBART Model)
- Deployment: Docker + NGINX + Gunicorn (Planned)

---

## 📂 Project Structure

QR_REPORT_SYSTEM/
│
├── app.py
├── config.py
├── requirements.txt
│
├── models/
│   ├── report_model.py
│   └── user_model.py
│
├── routes/
│   ├── report_routes.py
│   └── auth_routes.py
│
├── services/
│   ├── ocr_service.py
│   ├── storage_service.py
│   └── ai_service.py
│
├── uploads/
└── venv/

---

## 🧠 AI Module

The AI module:

- Uses the model: sshleifer/distilbart-cnn-12-6
- Generates concise summaries from OCR extracted text
- Handles long technical documents using chunking
- Loads the model once for performance efficiency
- Runs offline after the initial model download

### AI Workflow

1. OCR extracts raw text from uploaded document  
2. Text is cleaned and preprocessed  
3. Long documents are split into chunks  
4. Each chunk is summarized  
5. Final compressed summary is generated  
6. Summary is stored in MongoDB under `ai_summary`

---

## 🔐 Role-Based Access Control

| Role     | Access Level |
|----------|--------------|
| Admin    | Full access |
| Manager  | Restricted access |
| Operator | Limited upload/view access |

All upload, view, and edit actions are logged for auditing.

---

## 🚀 How to Run the Project

### 1. Clone the Repository

git clone <your-repository-url>  
cd QR_Report_System  

---

### 2. Create Virtual Environment

python -m venv venv  
venv\Scripts\activate   (Windows)

---

### 3. Install Dependencies

pip install -r requirements.txt  
pip install transformers torch sentencepiece  

---

### 4. Run the Application

python app.py  

Open in browser:  
http://127.0.0.1:5000  

---

## 📤 Upload API

Endpoint:  
POST /upload-report  

Required Fields:

- document_id
- report_name
- report_type
- prepared_by
- report_date
- file (PDF/Image)

---

## 🔎 Search API

Endpoint:  
GET /search?q=keyword  

Searches across:
- Report name
- OCR extracted text

---

## 🗄️ MongoDB Document Structure

{
  "document_id": "TEST001",
  "report_name": "Vibration Analysis Report",
  "report_type": "Technical",
  "prepared_by": "Engineer",
  "report_date": "2026-02-26",
  "file_path": "uploads/reports/...",
  "ocr_text": "...",
  "ai_summary": "Generated AI summary...",
  "created_at": "timestamp"
}

---

## 🧪 Testing Scenarios

- Validate mandatory fields before upload
- Prevent duplicate document IDs
- Verify OCR text extraction
- Verify AI summary generation
- Verify MongoDB insertion
- Verify search functionality

---

## 🔒 Security Features

- LAN-based deployment
- Role-based authentication
- Secure file handling
- Encrypted document storage
- Audit logging of user actions
- Regular backup support

---

## 📈 Future Enhancements

- Natural language query search
- AI-powered ranking
- Summary preview in UI
- Advanced filtering options
- Dockerized production deployment

---

## 👩‍💻 Contributors

QR Division Report Management System Development Team

---

## 📜 License

For academic and internal organizational use only.
