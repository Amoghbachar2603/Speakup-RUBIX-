# 🛡️ Anonymous Whistleblower Web Application

This is a secure, anonymous whistleblowing system that allows users to submit voice or text-based reports. It uses Google Gemini via a Retrieval-Augmented Generation (RAG) pipeline to auto-fill key details like location, time, category, and accused person based on the user's description.

---

## 🔧 Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Speech-to-Text:** Whisper (local or Hugging Face)
- **RAG Pipeline:** Python + Gemini API
- **Database:** SQLite (via SQLAlchemy)
- **Environment Variables:** `.env` file for API keys

---

## ✨ Key Features

- 🎙️ Voice or Text Input for Descriptions
- 🧠 RAG-powered field autofill (location, time, accused, category)
- 🔐 Anonymous user access with generated reference ID + password
- 🗃️ Admin panel to view all reports
- 📄 Save final report as a PDF
- 🧪 Integrated frontend and backend in a single Flask app
