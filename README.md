# Student Manager

A simple student management web app with an HTML/CSS/JavaScript frontend and a Python FastAPI backend.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend:app --reload
```

Open http://127.0.0.1:8000 in your browser.

The app includes Add, Display, Search, Update, Delete, Grade Calculation, CSV Save, CSV Load, Reports, and Exit.

## Publish on GitHub

From this folder, create a Git repository and make the first commit:

```powershell
git init
git add .
git commit -m "Initial student manager app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your GitHub details. The `.gitignore` file keeps `.venv`, Python cache files, and secrets out of GitHub.

## Deploy the GitHub repository

GitHub Pages cannot run the Python API. To deploy the complete app, use Render:

1. Push this project to GitHub.
2. In Render, choose **New +** and **Web Service**.
3. Connect the GitHub repository.
4. Render will read `render.yaml`, install the dependencies, and run the FastAPI server.

The deployed Render URL is the browser URL for the complete application.
