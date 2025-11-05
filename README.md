
````markdown
# 🤖 Gemini AI Support Ticket System (Assignment)

This project is a detailed **Django-based web application** designed to manage customer support tickets. It implements distinct user roles (`customer` and `admin`) and integrates the **Google Gemini API** to provide instant, AI-generated response suggestions for administrators, significantly streamlining the support workflow.

---

## 🛠️ Installations & Setup Instructions

Follow these steps to set up and run the project locally.

### Prerequisites

You must have **Python 3.8+** and `pip` installed.
````

### 1\. Repository Setup

Clone the repository and navigate into the project directory:

```bash
git clone [https://github.com/Navangs23/Assignment.git](https://github.com/Navangs23/Assignment.git)
cd Assignment
```


### 2\. Virtual Environment

It's highly recommended to use a virtual environment:

```bash
# Create and activate the environment (Linux/macOS)
python -m venv venv
source venv/bin/activate
# For Windows: .\venv\Scripts\activate
```

### 3\. Install Dependencies

Install the required Python packages, including Django, `python-dotenv`, and the Google Generative AI SDK:

```bash
pip install django python-dotenv google-generativeai
```

### 4\. Configure Environment Variables

Create a file named **`.env`** in the project root directory (next to `manage.py`) and add your configuration details.

Obtain your valid API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```.env
# .env file content
SECRET_KEY='your-strong-django-secret-key'
DEBUG=True
GEMINI_API_KEY='YOUR_GENERATIVE_AI_API_KEY'
```

### 5\. Database and Migrations

Apply the database migrations to set up the necessary tables for Users, Tickets, and Profiles:

```bash
python manage.py makemigrations gemini_support
python manage.py migrate
```

### 6\. Create User Accounts

  * **Admin User:** Create a superuser to manage the system and access the AI-powered response tools:
    ```bash
    python manage.py createsuperuser
    ```
  * **Customer User(s):** Customers must register via the application's `/register/` endpoint.

### 7\. Run the Application

Start the Django development server:

```bash
python manage.py runserver
```

The application is accessible at: `http://127.0.0.1:8000/`

-----

## 🛑 Assumptions and Limitations

### Assumptions

  * **Django Profile Model:** It is assumed that a **`Profile`** model is correctly defined in `gemini_support/models.py` and linked to the built-in Django `User` model, containing the crucial `user_type` field (`admin` or `customer`).
  * **CKEditor Configuration:** CKEditor 4 is expected to be configured and correctly integrated into the admin template to support the rich text editing required for AI-generated HTML responses.

### Current Limitations

  * **CKEditor Version Lock:** The project uses the **last free open-source version, CKEditor 4.22.1**. Upgrading to 4.23.0 or higher will require purchasing a commercial Extended Support Model (ESM) license to avoid an initialization error.
  * **Synchronous AI Calls:** The current AI generation (`generate_ai_reply`) runs synchronously, meaning the HTTP request blocks while waiting for the Gemini API response. For high-traffic use, this could lead to performance bottlenecks.
  * **Attachment Handling:** The system does not currently pass attached files (images, documents) to the Gemini model for contextual analysis.

-----

## 🚀 Future Scope

The following features and improvements are planned for future development to enhance the system's robustness and AI capabilities:

### Core Improvements

1.  **Asynchronous Processing:** Migrate the AI generation process to an **asynchronous task queue** (e.g., Celery) to improve server responsiveness and user experience during long API calls.
2.  **Email Notifications:** Implement comprehensive email and/or SMS alerts for users upon ticket status changes and for administrators upon new ticket submission.
3.  **Modern Editor Migration:** Replace the legacy CKEditor 4 with a modern, open-source alternative (like **TinyMCE 6** or **Quill**) to mitigate security risks and licensing concerns.

### Advanced AI Features

1.  **Contextual History:** Modify the Gemini prompt to include the entire **ticket reply history** before generating a new response, leading to more accurate and informed suggestions.
2.  **Auto-Triage and Routing:** Utilize the Gemini API to analyze the initial ticket description and automatically assign a **category** (e.g., 'Billing', 'Technical') and a **priority** (High, Medium, Low).
3.  **Multimodal Analysis:** If policy permits, integrate a multimodal Gemini model to analyze attached images or documents when responding to complex issues.

<!-- end list -->

```
```
