# Trade Tracker
![Frontend CI](https://github.com/XxDrancerxX/trade-tracker/actions/workflows/frontend-ci.yml/badge.svg)
[![Backend CI](https://github.com/XxDrancerxX/trade-tracker/actions/workflows/pytest.yml/badge.svg)](https://github.com/XxDrancerxX/trade-tracker/actions/workflows/pytest.yml)



## Backend Setup: Using Python Virtual Environments (.venv)

👉 See detailed developer notes in [noteBookProject.md](./noteBookProjectBackEnd.md)
👉 In plain editor mode, Ctrl+Click (or Cmd+Click on Mac) should open the file.
👉 In Markdown Preview (Ctrl+Shift+V), clicking the link opens the file inside VS Code too.

To keep backend dependencies isolated and avoid conflicts with other projects or the frontend, use a Python virtual environment (.venv):

1. **Create a virtual environment** (inside the `backend` folder):
	```bash
	cd backend
	python3 -m venv .venv
	```

2. **Activate the virtual environment** (every time you start working):
	- On Linux/macOS:
	  ```bash
	  source .venv/bin/activate
	  ```
	- On Windows:
	  ```cmd
	  .venv\Scripts\activate
	  ```

3. **Install dependencies** (only needed once per environment):
	```bash
	pip install -r requirements.txt
	```

4. **Note:**
	- The `.venv` folder is not included in version control (see `.gitignore`).
	- If you clone this repo or use a new codespace, repeat steps 1–3 to set up your environment.
	- All dependencies you install while the virtual environment is active will remain in `.venv` until you delete it.

This ensures your backend dependencies are always isolated and easy to manage.



## Reminder: Running the Backend Server

To run or test your Django backend server, make sure you are in the correct folder and have your virtual environment activated:

1. **Navigate to the backend folder** (if you are not already there):
   ```bash
   cd backend
   ```

2. **Activate your virtual environment**:
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```cmd
     .venv\Scripts\activate
     ```

3. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```

**Note:**  
You must be inside the `backend` folder and have your virtual environment activated before running any Django management commands (like `runserver`, `makemigrations`, or `migrate`). This ensures all dependencies are available and your project runs correctly.



## Reminder: Updating Dependencies

If you install a new Python package (dependency) in your virtual environment, remember to update `requirements.txt` so others can install the same dependencies:

1. Install the package:
	```bash
	pip install package-name
	```
2. Update `requirements.txt`:
	```bash
	pip freeze > requirements.txt
	```

This step is manual and not automatic. Always commit the updated `requirements.txt` to version control after adding new dependencies.

## Django Superuser Setup

To access the Django admin panel and manage users or trades, you need a superuser account. This account is stored in your project's database (e.g., `db.sqlite3`).

### How to Create a Superuser

1. In the `backend` folder, run:
	```bash
	python manage.py createsuperuser
	```
2. Follow the prompts to set a username, email, and password.

### Important Notes
- The superuser is saved in your database file (e.g., `db.sqlite3`).
- If you start a new Codespace, clone the repo elsewhere, or reset/delete your database, you will need to create a new superuser.
- The database file is not tracked by git (see `.gitignore`).
- As long as you keep the same database file, your superuser will remain available.

### How to Check for Existing Superusers
You can check if a superuser exists by running:
```bash
python manage.py shell
```
Then, in the Python shell:
```python
from django.contrib.auth.models import User
User.objects.filter(is_superuser=True)
```
If the result is empty, create a new superuser as shown above.


## Running Django Migrations

Migrations are how Django updates your database schema to match your models. You should run migrations whenever you clone the project, create new models, or make changes to existing models.

### How to Run Migrations

1. Make sure your virtual environment is activated and you are in the `backend` folder.
2. Run the following commands:
	```bash
	python manage.py makemigrations
	python manage.py migrate
	```

**makemigrations** creates new migration files based on the changes you made to your models.

**migrate** applies those changes to your database.

You should run these commands any time you:
- Pull new changes that affect models
- Change or add models
- Set up the project in a new environment

### Commands:
python manage.py check:
Runs Django’s system check framework. It validates settings and common mistakes without touching the DB or running migrations.

pytest -q:
Runs your tests in quiet mode (less noise; still fails fast on errors).
Keeping those comments in YAML is fine—comments don’t affect execution.



