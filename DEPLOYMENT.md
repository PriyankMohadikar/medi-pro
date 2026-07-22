# 🌐 MediPrice Pro — Complete Production Deployment Guide

This guide covers step-by-step instructions for deploying **MediPrice Pro** to production using **Render**, **Vercel**, **Railway**, or **Docker/VPS**.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    Client[User Browser] -->|HTTP / HTTPS| Frontend[Vite React App]
    Frontend -->|API Requests| Backend[FastAPI Backend Server]
    Backend -->|PostgreSQL Protocol| Supabase[(Supabase Database)]
    Backend -->|HTTPS API| AI[Groq / OpenRouter / Gemini AI]
```

---

## 🎯 Option 1: Render / Vercel (Recommended & Easiest)

### Step 1: Deploy Database (Supabase)
Your database is already created and populated on **Supabase**!
Connection URI format:
```text
postgresql://postgres.bnccejadsruqxkniiwrn:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require
```

---

### Step 2: Deploy Backend API (Render / Railway)

1. Push your repository to **GitHub** (Ensure `.env` is NOT uploaded; `.gitignore` handles this automatically).
2. Log in to [Render.com](https://render.com/) or [Railway.app](https://railway.app/).
3. Click **New Web Service** and connect your GitHub repository.
4. Configure settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api_server:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables in the Render Dashboard:
   - `DATABASE_URL` = `postgresql://postgres.bnccejadsruqxkniiwrn:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require`
   - `AI_PROVIDER` = `groq`
   - `GROQ_API_KEY` = `your_groq_api_key`
   - `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app,http://localhost:3000`
6. Click **Deploy**. Copy your deployed backend URL (e.g., `https://mediprice-api.onrender.com`).

---

### Step 3: Deploy Frontend (Vercel or Netlify)

1. Log in to [Vercel.com](https://vercel.com/) or [Netlify.com](https://netlify.com/).
2. Import your GitHub repository.
3. Settings:
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://mediprice-api.onrender.com`
5. Click **Deploy**. Your app will be live at `https://your-app.vercel.app`.

---

## 🐳 Option 2: VPS / Docker Compose Deployment

If deploying to a virtual private server (DigitalOcean, AWS EC2, Linode, Hetzner):

### Step 1: Install Docker & Docker Compose on your server
```bash
sudo apt update && sudo apt install -y docker.io docker-compose
```

### Step 2: Clone repository & create `.env`
```bash
git clone https://github.com/your-username/mediprice-pro.git
cd mediprice-pro
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your Supabase database string and Groq API keys.

### Step 3: Launch with Docker Compose
```bash
docker-compose up -d --build
```
Your app will now run:
- Frontend: `http://your-server-ip:3000`
- Backend: `http://your-server-ip:8000`

---

## 🔐 Environment Variables Security Checklist

| Variable | Description | Safe for Git? |
| :--- | :--- | :--- |
| `DATABASE_URL` | Supabase PostgreSQL Connection String | ❌ **No (Secret)** |
| `GROQ_API_KEY` | Groq AI Model Key | ❌ **No (Secret)** |
| `OPENROUTER_API_KEY` | OpenRouter Fallback Key | ❌ **No (Secret)** |
| `ALLOWED_ORIGINS` | Permitted Frontend URLs for CORS | ✅ Yes |
| `VITE_API_BASE_URL` | Public API URL for Frontend | ✅ Yes |

---

## ⚡ Post-Deployment Verification

1. Test API Health Endpoint:
   `GET https://your-backend-url/api/health`
2. Test Pricing Search & Filter on Frontend.
3. Test AI Package Insights / Chatbot logic.
