# Recipe Management System

This project allows admins to manage recipes and gives users reading access to recipes through API. It is built with Python and Flask on the backend and TypeScript, React, Refine, and Ant Design on the admin panel frontend


## Prerequisites

- Python 3.x
- Docker

## Running with docker compose

1. **Open backend folder:**
   ```bash
   cd backend
   ```

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

1. **Build and run the Docker containers:**
   ```bash
   cd ..
   docker compose up
   # or (if you made changes in backend or frontend source code)
   docker compose up --build
   ```

1. **Create the database:**
   ```bash
   ./devmanage.sh create_db
   ```

1. **Create manager and editor admin users:**
   ```bash
   ./devmanage.sh create_admins
   ```

1. **Access Swagger UI:**
   ```bash
   http://127.0.0.1:8001/apidocs/
   ```

1. **Access the database using SQL commands:**
   ```bash
   docker compose exec db psql --username=recipes_db_user --dbname=recipes_db
   ```


## Running in development mode
1. **Make sure that the app is not runing wihtin docker:**
   ```bash
   docker compose down
   ```
1. **Run only db with docker compose:**
   ```bash
   docker compose up db
   ```
1. **Run backend:**
   ```bash
   cd backend
   ./devbackend.sh
   ```
1. **Run frontend:**
   ```bash
   cd admin_dashboard
   npm run dev
   ```
