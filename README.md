# soft_skills

Certainly! Below is a comprehensive setup guide that you can share with your collaborators, including setting up Django, creating a virtual environment, writing a requirements.txt file, and optionally installing the Django Debug Toolbar:


### Setup Guide for Collaborators (yotam - for django form project)

#### 1. Prerequisites
- Python 3.x installed on your system ([Download Python](https://www.python.org/downloads/))

#### 2. Clone the Repository
- Clone the project repository from the provided Git URL:
  ```
  git clone <repository_url>
  ```

#### 3. Create and Activate Virtual Environment
- Navigate to the project directory:
  ```
  cd <project_directory>
  ```
- Create a virtual environment named `venv`:
  ```
  python -m venv venv
  ```
- Activate the virtual environment:
  - On Windows:
    ```
    venv\Scripts\activate
    ```
  - On macOS/Linux:
    ```
    source venv/bin/activate
    ```

#### 4. Install Django and Dependencies
- Install Django and other project dependencies:
  ```
  pip install django
  ```

#### 5. install requirements.txt File
- requirements.txt file listing all project dependencies:
  ```
  pip install -r requirements.txt
  ```

#### 6. Run Django Migrations (If Applicable)
- If the project includes migrations, apply them to the database:
  ```
  python manage.py makemigrations

  python manage.py migrate
  
  ```

#### 7. Run the Django Development Server
- Start the Django development server:
  ```
  python manage.py runserver
  ```



