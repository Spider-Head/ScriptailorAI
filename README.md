# Scriptailor.AI

Scriptailor.AI is a versatile AI-powered content generation tool designed to help various industries quickly produce high-quality written content. The tool allows users to generate articles, blogs, reports, scripts, stories, and other types of content with minimal steps using AI, offering options to customize templates, edit or regenerate paragraphs, and incorporate images. This project leverages Django for the main website and Flask for the AI generator.

## Features

- Generate various types of content using AI
- Customize templates and edit generated content
- Incorporate client-provided or AI-generated images
- User authentication and database management

## Tech Dependencies

- **Django**: Handles the main website, including user authentication and database management.
- **Flask**: Manages the AI content generation functionalities.
- **CKEditor**: Rich text editor for content customization.
- **Python**: Programming language for backend development.
- **HTML, CSS, JavaScript**: Frontend technologies for building the user interface.
- **Google Fonts**: For the 'Poppins' font family used in the project.

## Prerequisites

- Python 3.x
- Virtualenv (optional but recommended)

## Installation and Setup

Follow these steps to set up and run the project on your local machine:

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/scriptailor-ai.git
cd scriptailor-ai

### 2. Create and Activate a Virtual Environment (Optional)
```sh
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
```sh
pip install -r requirements.txt

### 4. Set Up Django
```sh
cd scriptailor
python manage.py makemigrations
python manage.py migrate

### 5. Set Up and run Flask
```sh
cd flask
python app.py

### 6. Run django server
(open another terminal)
```sh
cd scriptailor
python manage.py runserver

### 7. access the application
Open your web browser and go to http://127.0.0.1:8000/ to access the main website.




















