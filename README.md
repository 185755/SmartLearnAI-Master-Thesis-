# 📚 SmartLearnAI

SmartLearnAI is an intelligent learning application that transforms various educational materials (audio, PDFs, text, presentations) into interactive flashcards and quizzes powered by artificial intelligence.

## 🚀 Key Features

- 🎙️ Transcription of lecture recordings  
- 📄 Analysis of slides, notes, and articles  
- 🧠 AI-generated flashcards and quizzes  
- 🔁 Review system based on the Leitner algorithm  
- 📊 Learning history and smart topic search  

## 🛠️ Technologies

- **Backend:** Python + Django  
- **Frontend:** React / React Native  
- **Database:** PostgreSQL / Firebase  
- **AI:** OpenAI API, Whisper, NLP  

---

# ⚙️ Installation Guide (Backend)

Below is a complete step‑by‑step guide for running the backend locally after downloading the project from GitHub.

---

## 1️⃣ Clone the repository

```bash
git clone https://github.com/<your_repo>/smartlearn_backend.git
cd smartlearn_backend

 ## 2️⃣ Create and activate virtual environment

### Windows:

    python -m venv venv
    venv\Scripts\activate

### macOS / Linux:

    python3 -m venv venv
    source venv/bin/activate

## 3️⃣ Install dependencies

### Using requirements.txt:

    pip install -r requirements.txt

### OR install manually:

    pip install Django==4.2.24 psycopg2-binary pillow pytesseract python-docx PyPDF2 numpy openai

## 4️⃣ Install PostgreSQL

Download PostgreSQL:  
https://www.postgresql.org/download/

During installation:

- set password for user `postgres`
- leave port `5432`
- install `pgAdmin` (recommended)

## 5️⃣ Create database

In pgAdmin:

1. Go to `Servers → PostgreSQL → Databases`
2. Click `Create → Database`
3. Set:
   - Name: `smartlearn_db`
   - Owner: `postgres`

## 6️⃣ Configure database in Django

Open:

    smartlearn_backend/smartlearn_backend/settings.py

Set the `DATABASES` section:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'smartlearn_db',
            'USER': 'postgres',
            'PASSWORD': '<your_password>',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

## 7️⃣ Apply migrations

    python manage.py migrate

## 8️⃣ Create admin user

    python manage.py createsuperuser

## 9️⃣ Run the development server

    python manage.py runserver

## 🔟 Project is ready to use

You can now:

- log into Django Admin
- add materials
- test API
- integrate with frontend
