# ADFF — Deployment & Hosting Guide

This guide explains how to deploy the **ADFF (Agentic Document Tampering Detection & Forensics)** platform across different environments:

1. **Local Network / Presentation Mode** (Fastest for in-class professor presentation)
2. **Instant Public HTTPS URL** (via Localtunnel / Ngrok)
3. **Docker Container Deployment** (Docker / Docker Compose)
4. **Cloud Platforms** (Render, Railway, Hugging Face Spaces)

---

## 1. Local Network / Presentation Mode (Recommended for Demos)

To show the project on your laptop or allow a professor/classmate on the same Wi-Fi to open it from their phone/laptop:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

1. Find your local IP on Windows:
   ```powershell
   ipconfig
   # Look for IPv4 Address, e.g. 192.168.1.45
   ```
2. Anyone on your local Wi-Fi can now open:
   ```
   http://192.168.1.45:8000
   ```

---

## 2. Instant Free Public HTTPS URL (No Cloud Account Needed)

If you need a live public link right now without setting up servers:

### Option A: Using Localtunnel (Free, no login required)
```bash
npx localtunnel --port 8000
```
It gives you an instant public HTTPS URL like:
`https://curly-lions-jump.loca.lt`

### Option B: Using Ngrok
```bash
ngrok http 8000
```

---

## 3. Docker Deployment (Standard Production)

The project includes a production `Dockerfile` and `docker-compose.yml`.

### Build & Run with Docker:
```bash
docker build -t adff-forensics .
docker run -p 8000:8000 adff-forensics
```

### Or using Docker Compose:
```bash
docker compose up --build
```
Navigate to: `http://localhost:8000/`

---

## 4. Free Cloud Hosting Options

### A. Render.com (Easiest 1-Click Free Web Service)
1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for ADFF"
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. Go to [https://render.com](https://render.com) and click **"New Web Service"**.
3. Select your GitHub repository.
4. Render will automatically detect `render.yaml` or you can enter:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Within 2-3 minutes, you have a free live URL (e.g., `https://adff-forensics.onrender.com`).

---

### B. Railway.app
1. Go to [https://railway.app](https://railway.app).
2. Click **"New Project" $\rightarrow$ "Deploy from GitHub repo"**.
3. Railway automatically detects the `Dockerfile` and builds it.
4. Under **Settings $\rightarrow$ Networking**, click **"Generate Domain"** to get your public URL.

---

### C. Hugging Face Spaces (Great for AI / Academic Projects)
1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Space SDK: Select **Docker** (Blank).
3. Clone your Space repo and push this codebase.
4. Hugging Face automatically builds the container and embeds your interactive dashboard in a public link.
