# Setup Instructions

## Quick Start

**For Mac (including M1):**
1. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   # Use python3 for all commands on Mac M1
   ```

**For Windows:**
1. **Activate virtual environment**
   ```bash
   venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create database and migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

5. **Run development server**

   Choose one of the following options:

   **Option A: Run on localhost (127.0.0.1)**
   
   **Mac (including M1):**
   ```bash
   python3 manage.py runserver
   # or explicitly:
   python3 manage.py runserver 127.0.0.1:8000
   ```
   
   **Windows:**
   ```bash
   python manage.py runserver
   # or explicitly:
   python manage.py runserver 127.0.0.1:8000
   ```
   - Access at: http://127.0.0.1:8000/ or http://localhost:8000/
   - Only accessible from the same machine
   - Best for local development

   **Option B: Run on a specific IP address**
   
   **Mac (including M1):**
   ```bash
   python3 manage.py runserver 10.100.81.190:8000
   ```
   
   **Windows:**
   ```bash
   python manage.py runserver 10.100.81.190:8000
   ```
   - Access at: http://10.100.81.190:8000/
   - Accessible from other devices on the same network
   - Make sure the IP is in `ALLOWED_HOSTS` in `config/settings.py`

   **Option C: Run on all network interfaces (0.0.0.0)**
   
   **Mac (including M1):**
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```
   
   **Windows:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   - Accessible from any device on the network using your machine's IP
   - Access at: http://YOUR_IP_ADDRESS:8000/
   - Make sure your IP is in `ALLOWED_HOSTS` in `config/settings.py`

6. **Access the application**
   - **Localhost**: http://127.0.0.1:8000/ or http://localhost:8000/
   - **Network IP**: http://YOUR_IP:8000/ (replace YOUR_IP with your actual IP address)
   - **Admin Panel**: http://127.0.0.1:8000/admin/ or http://YOUR_IP:8000/admin/

## Configuring ALLOWED_HOSTS

To allow access from other devices on the network, you need to add your IP address to `ALLOWED_HOSTS` in `config/settings.py`:

```python
ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', 'YOUR_IP_ADDRESS']
```

**To find your IP address:**

**Mac (including M1):**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Or for Wi-Fi: ifconfig en0 | grep "inet "
# Or for Ethernet: ifconfig en1 | grep "inet "
```

**Linux:**
```bash
ifconfig
# or
ip addr show
```

**Windows:**
```bash
ipconfig
```

Look for your network interface and find the IPv4 address (e.g., `192.168.1.100`)

**Example:**
If your machine's IP is `192.168.1.100`, add it to `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', '192.168.1.100']
```

**Note:** For production, use a proper web server (like Nginx + Gunicorn) instead of Django's development server.

## Setting Up User Roles

### Creating an Admin User
1. Go to Admin Panel → Users → Add User
2. Fill in username, email, password
3. Set role to "ADMIN"
4. Check "Staff status" and "Superuser status" (optional but recommended)

### Creating a Judge User
1. Go to Admin Panel → Users → Add User
2. Fill in username, email, password
3. Set role to "JUDGE"
4. Save the user
5. Go to Judges → Add Judge
6. Select the user you just created
7. Optionally add a judge_id and specialization

### Creating a Student User
1. Go to Admin Panel → Users → Add User
2. Fill in username, email, password
3. Set role to "STUDENT"
4. Save the user
5. Go to Students → Add Student
6. Select the user you just created
7. Enter a unique student_id
8. Optionally assign to a team (create team first if needed)

## Creating Your First Rubric

1. **Prepare Excel file** with columns:
   - Criterion Name (required)
   - Max Score (required)
   - Description (optional)
   - Weight (optional, defaults to 1.0)

2. **Import Rubric**:
   - Go to Rubrics → Import New Rubric
   - Enter rubric name
   - Upload Excel file
   - Click "Import Rubric"

## Creating a Project

1. Go to Admin Panel → Projects → Add Project
2. Enter project title and description
3. Select a rubric
4. Set status (Draft, Evaluating, Completed)
5. Save the project

## Creating a Team

1. Go to Admin Panel → Teams → Add Team
2. Select a project
3. Optionally enter team name
4. Save the team

5. **Add Students to Team**:
   - Go to Students → Edit each student
   - Select the team from the dropdown
   - Save

## Evaluation Workflow

1. **Judge logs in** and goes to Projects
2. **Judge selects a project** and clicks "Evaluate"
3. **Judge enters scores** for each criterion
4. **Judge adds comments** (optional)
5. **Judge saves as draft** or **submits** the evaluation

6. **System calculates**:
   - Average scores per criterion
   - Weighted scores
   - Total project score
   - Percentage

## Viewing Reports

1. **Go to Project Details**
2. **View evaluation summary** showing:
   - Total score
   - Average scores per criterion
   - Judge evaluations
   - Comments

3. **Export to Excel/PDF** (Admin only):
   - Go to Reports → Project Report
   - Click "Export to Excel" or "Export to PDF"
