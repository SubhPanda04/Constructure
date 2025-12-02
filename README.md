# AI Email Assistant 📧

A smart email dashboard that integrates with Gmail to provide AI-powered summaries, reply generation, and email management. Built with FastAPI, React, and Groq's Llama 3 model for lightning-fast inference.

## 🚀 Features

- **Google OAuth2 Integration**: Secure login with Gmail permissions.
- **AI Email Summaries**: Automatically fetches and summarizes the last 5 emails using Llama 3.
- **Smart Replies**: Generates context-aware, professional replies with a single click.
- **Email Management**: Read, reply to, and delete emails directly from the dashboard.
- **Real-time Status**: Granular status updates for long-running AI operations.
- **Resilience**: Built-in retry logic and structured logging for reliability.

## 🛠️ Technologies Used

- **Frontend**: React.js, Vite, TailwindCSS
- **Backend**: FastAPI, Python 3.8+
- **AI Provider**: Groq (Llama-3.3-70b-versatile)
- **Authentication**: Google OAuth2
- **APIs**: Gmail API
- **Deployment**: Vercel (Frontend), Render/Railway (Backend)

## 📋 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Console Project with Gmail API enabled

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5173
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
FRONTEND_URL=http://localhost:5173
```

Run the server:
```bash
uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

Run the development server:
```bash
npm run dev
```

## 🔐 Google OAuth Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **Gmail API**.
4. Configure **OAuth Consent Screen**:
   - User Type: External (for testing) or Internal.
   - Add Test Users: Add the email addresses you want to test with.
   - Scopes: `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.trash`.
5. Create **Credentials** (OAuth Client ID):
   - Application Type: Web Application.
   - Authorized Javascript Origins: `http://localhost:5173` (and your production URL).
   - Authorized Redirect URIs: `http://localhost:5173` (and your production URL).

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | OAuth Client ID from Google Cloud | Yes |
| `GOOGLE_CLIENT_SECRET` | OAuth Client Secret from Google Cloud | Yes |
| `GOOGLE_REDIRECT_URI` | URL where Google redirects after login | Yes |
| `GROQ_API_KEY` | API Key for Groq AI | Yes |
| `SECRET_KEY` | Secret key for session management | Yes |
| `FRONTEND_URL` | URL of the frontend application | Yes |

## 🔗 Live Demo

Live Vercel URL: [https://constructure-three.vercel.app/](https://constructure-three.vercel.app)

## ⚠️ Assumptions & Limitations

- **Test Mode**: The app is currently in Google OAuth "Testing" mode, requiring users to be manually added to the "Test Users" list in Google Cloud Console.
- **Token Storage**: Access tokens are stored in-memory on the backend for simplicity. For production, a database (PostgreSQL/Redis) is recommended.
- **Rate Limits**: Subject to Gmail API and Groq API rate limits.
- **Email Rendering**: Basic HTML parsing is implemented; complex email layouts may be simplified.
