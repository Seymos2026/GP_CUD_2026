# Mac M1 (Apple Silicon) Setup Guide

This guide provides specific instructions for setting up and running the Django project on Mac M1 (Apple Silicon) computers.

## Prerequisites

1. **Python 3.10+** - Mac M1 comes with Python 3, but you may need to install/update it
2. **Homebrew** (recommended) - Makes package management easier

## Installation Steps

### 1. Check Python Version

```bash
python3 --version
```

Should show Python 3.10 or higher. If not, install via Homebrew:

```bash
brew install python@3.11
```

### 2. Create Virtual Environment

```bash
cd "eb-based graduation project evaluation system"
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Upgrade pip (Important for M1)

```bash
pip install --upgrade pip
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

**If you encounter architecture errors**, try:

```bash
arch -arm64 pip install -r requirements.txt
```

**If specific packages fail**, you may need to install them individually:

```bash
# Common packages that might need special handling
pip install Django==4.2.7
pip install pandas==2.1.3
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9
pip install reportlab==4.0.7
pip install Pillow==10.1.0
```

### 6. Run Migrations

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 7. Create Superuser

```bash
python3 manage.py createsuperuser
```

Follow the prompts to create an admin account.

## Running the Server

### On Localhost

```bash
python3 manage.py runserver
```

Access at: http://127.0.0.1:8000/

### On Network IP (Mac M1)

**Step 1: Find your IP address**

```bash
# Quick method - shows all IPs
ifconfig | grep "inet " | grep -v 127.0.0.1

# Or for Wi-Fi specifically
ifconfig en0 | grep "inet "

# Or for Ethernet
ifconfig en1 | grep "inet "
```

Look for output like: `inet 192.168.1.100`

**Step 2: Update ALLOWED_HOSTS**

Edit `config/settings.py`:

```python
ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', '192.168.1.100']
```

Replace `192.168.1.100` with your actual IP.

**Step 3: Run server with IP**

```bash
python3 manage.py runserver 192.168.1.100:8000
```

Access from network: http://192.168.1.100:8000/

### Using Pre-configured IP

If you want to use the pre-configured IP `10.100.81.190`:

```bash
python3 manage.py runserver 10.100.81.190:8000
```

Access at: http://10.100.81.190:8000/

## Common Mac M1 Issues and Solutions

### Issue 1: "python: command not found"

**Solution:** Use `python3` instead of `python`

```bash
python3 manage.py runserver
```

### Issue 2: Architecture errors during package installation

**Solution:** Use `arch -arm64` prefix

```bash
arch -arm64 pip install <package-name>
```

### Issue 3: Pillow installation fails

**Solution:** Install dependencies first

```bash
brew install libjpeg libpng
pip install Pillow
```

### Issue 4: pandas installation issues

**Solution:** Install numpy first, then pandas

```bash
pip install numpy
pip install pandas
```

### Issue 5: "zsh: command not found: python"

**Solution:** 
1. Check if Python is installed: `python3 --version`
2. If not installed, install via Homebrew: `brew install python@3.11`
3. Always use `python3` command

### Issue 6: Virtual environment not activating

**Solution:** Make sure you're in the project directory and use the correct path

```bash
cd "/Users/ahmedseyam/Desktop/eb-based graduation project evaluation system"
source venv/bin/activate
```

## Finding Your IP Address on Mac M1

### Method 1: Using ifconfig (Terminal)

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Method 2: System Preferences

1. Open **System Preferences** (or **System Settings** on macOS Ventura+)
2. Go to **Network**
3. Select your active connection (Wi-Fi or Ethernet)
4. Your IP address is displayed

### Method 3: Network Utility

```bash
# For Wi-Fi
ipconfig getifaddr en0

# For Ethernet
ipconfig getifaddr en1
```

## Quick Reference Commands (Mac M1)

```bash
# Activate virtual environment
source venv/bin/activate

# Run on localhost
python3 manage.py runserver

# Run on specific IP
python3 manage.py runserver 192.168.1.100:8000

# Run on all interfaces
python3 manage.py runserver 0.0.0.0:8000

# Find IP address
ifconfig | grep "inet " | grep -v 127.0.0.1
```

## Terminal Tips for Mac M1

1. **Use iTerm2 or Terminal** - Both work fine
2. **Use zsh or bash** - Both are supported
3. **Always use `python3`** - More reliable than `python` on Mac
4. **Check architecture** - Run `uname -m` to confirm you're on arm64

```bash
uname -m
# Should output: arm64
```

## Testing Network Access

After starting the server on a network IP, test from another device:

1. Make sure both devices are on the same Wi-Fi network
2. On your Mac, run: `python3 manage.py runserver 0.0.0.0:8000`
3. Find your Mac's IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
4. On another device, open browser and go to: `http://YOUR_MAC_IP:8000`

## Security Note

When running on network IPs, make sure:
- You're on a trusted network
- Firewall allows port 8000 (if needed)
- `ALLOWED_HOSTS` includes your IP

## Need Help?

If you encounter issues specific to Mac M1:
1. Check Python version: `python3 --version`
2. Check architecture: `uname -m`
3. Verify virtual environment is activated: `which python3`
4. Check if packages are installed: `pip list`
