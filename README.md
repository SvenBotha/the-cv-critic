# The CV Critic
Crafting Resumes That Get Noticed

### About
The CV Critic is a Django web application that utilizes the OpenAI API to generate a rating and provide recommendations for improving a CV.

# Getting started

### Prerequisites
Before deploying this application, ensure you have the following installed:

- **Python 3.10+**  
- **pip** (Python package manager)  
- **virtualenv** (for managing Python environments)  
---

### 1. Clone the Repository
Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/SvenBotha/the-cv-critic
cd the-cv-critic
```

### 2. Set Up a Virtual Environment
Create a virtual environment inside the project folder:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

**For Linux/macOS:**

```bash
source .venv/bin/activate
```

**For Windows (Command Prompt):**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a .env file in the project root and add your environment variables:

```env
DEBUG=True
OPENAI_API_KEY=your_openai_api_key
CONVERTAPI_API_KEY=your_convertapi_key
DJANGO_SECRET_KEY=your_django_secret_key
```

### 5. Run the Development Server
To start the Django development server, run:

```bash
python manage.py runserver
```
Then visit: http://127.0.0.1:8000
