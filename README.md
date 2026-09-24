# 🎓 Clubify – College Club Collaboration Platform

Clubify is a Django-based web application designed to help students
explore college clubs, discover events, and connect with campus communities.

## 🚀 Features

- Browse college clubs and explore their details.
- Discover upcoming and past club events.
- Club administration and management.
- User authentication and login.
- Event creation and management.
- Contact form for communication.
- Responsive web interface.

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Version Control:** Git and GitHub

## 📂 Project Structure

    Clubify/
    ├── clubapp/       # Main Django application
    ├── clubify/       # Django project configuration
    ├── static/        # CSS, JavaScript, and images
    ├── templates/     # HTML templates
    ├── manage.py
    └── requirements.txt

## ⚙️ Installation and Setup

### 1. Clone the repository

    git clone https://github.com/krishna-chandore/clubify-.git

### 2. Navigate to the project directory

    cd clubify-

### 3. Create a virtual environment

    python -m venv .venv

### 4. Activate the environment

Windows:

    .venv\Scripts\activate

Linux / macOS:

    source .venv/bin/activate

### 5. Install dependencies

    pip install -r requirements.txt

### 6. Apply database migrations

    python manage.py migrate

### 7. Start the development server

    python manage.py runserver

Open http://127.0.0.1:8000/ in your browser.

## 🔐 Environment Configuration

Configure the following environment variables before running the project:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `EMAIL_HOST_PASSWORD`

Never commit secret keys, passwords, or private credentials.

## 👨‍💻 Developer

**Krishna Chandore**

GitHub: [krishna-chandore](https://github.com/krishna-chandore)

## 📌 Project Status

Currently under development.

## 🌐 Live Demo

Coming soon.