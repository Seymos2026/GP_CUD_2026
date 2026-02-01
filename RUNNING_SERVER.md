# Running the Django Server

This guide explains how to run the Django development server on localhost and on a specific IP address.

## Prerequisites

1. Virtual environment is activated
2. Dependencies are installed (`pip install -r requirements.txt`)
3. Migrations are applied (`python manage.py migrate`)

## Mac M1 (Apple Silicon) Notes

If you're using a Mac with M1 chip:
- Use `python3` instead of `python` for commands
- Virtual environment should work normally with `python3 -m venv venv`
- If you encounter package installation issues, try: `arch -arm64 pip install <package>`
- Most packages in requirements.txt are compatible with Apple Silicon

## Running on Localhost

**Localhost** means the server is only accessible from the same machine.

### Command:
```bash
python manage.py runserver
```
or explicitly:
```bash
python manage.py runserver 127.0.0.1:8000
```

### Access URLs:
- Web Interface: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/
- Alternative: http://localhost:8000/

### When to use:
- Local development and testing
- When you only need to access from the same machine
- No network access required

---

## Running on a Specific IP Address

**Specific IP** allows access from other devices on the same network.

### Step 1: Find Your IP Address

**On Mac (including M1):**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# or more detailed:
ifconfig en0  # for Wi-Fi
ifconfig en1  # for Ethernet
# Look for "inet" line, e.g., "inet 192.168.1.100"
```

**On Linux:**
```bash
ifconfig
# or
ip addr show
```

**On Windows:**
```bash
ipconfig
```

Look for your network interface (usually `eth0`, `wlan0`, `Wi-Fi`, or `Ethernet`) and find the IPv4 address.

**Example output:**
```
inet 192.168.1.100  netmask 255.255.255.0
```

### Step 2: Update ALLOWED_HOSTS

Edit `config/settings.py` and add your IP to `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', '192.168.1.100']
```

Replace `192.168.1.100` with your actual IP address.

### Step 3: Run Server with IP

```bash
python manage.py runserver 192.168.1.100:8000
```

Replace `192.168.1.100` with your actual IP address.

### Access URLs:
- From any device on the network: http://192.168.1.100:8000/
- Admin Panel: http://192.168.1.100:8000/admin/

### When to use:
- Testing from mobile devices
- Accessing from other computers on the same network
- Team development and testing

---

## Running on All Network Interfaces (0.0.0.0)

**0.0.0.0** makes the server accessible from any device on the network using your machine's IP.

### Step 1: Update ALLOWED_HOSTS

Edit `config/settings.py`:

```python
ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', '*']
```

Or add your specific IP addresses.

### Step 2: Run Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### Access URLs:
- From any device: http://YOUR_IP_ADDRESS:8000/
- Replace `YOUR_IP_ADDRESS` with your actual IP

### When to use:
- When you want maximum flexibility
- When your IP might change
- For quick network testing

---

## Common IP Addresses

### Pre-configured IP (from settings.py)
- `10.100.81.190` - Already in ALLOWED_HOSTS

### Localhost addresses
- `127.0.0.1` - Localhost (IPv4)
- `localhost` - Localhost (hostname)
- `::1` - Localhost (IPv6)

### Network addresses
- `0.0.0.0` - All interfaces
- `192.168.x.x` - Common local network range
- `10.x.x.x` - Common local network range

---

## Examples

### Example 1: Local Development (Mac M1)
```bash
# Terminal 1: Activate venv and run
source venv/bin/activate
python3 manage.py runserver
# Access at: http://127.0.0.1:8000/
```

**Note:** On Mac M1, use `python3` instead of `python` if `python` command is not available.

### Example 2: Network Access with Specific IP (Mac M1)
```bash
# Terminal 1: Activate venv
source venv/bin/activate

# Terminal 2: Find IP (Mac)
ifconfig | grep "inet " | grep -v 127.0.0.1
# Found: 192.168.1.50

# Edit config/settings.py - Add to ALLOWED_HOSTS:
# ALLOWED_HOSTS = ['10.100.81.190', '127.0.0.1', 'localhost', '192.168.1.50']

# Terminal 1: Run with IP
python3 manage.py runserver 192.168.1.50:8000
# Access from network: http://192.168.1.50:8000/
```

### Example 3: Using Pre-configured IP
```bash
# Terminal 1: Activate venv
source venv/bin/activate

# Terminal 1: Run with pre-configured IP
python manage.py runserver 10.100.81.190:8000
# Access from network: http://10.100.81.190:8000/
```

---

## Troubleshooting

### Issue: "DisallowedHost" error
**Solution:** Add your IP address to `ALLOWED_HOSTS` in `config/settings.py`

### Issue: Cannot access from other devices
**Solutions:**
1. Check firewall settings - port 8000 might be blocked
2. Verify both devices are on the same network
3. Make sure you're using the correct IP address
4. Check that `ALLOWED_HOSTS` includes your IP

### Issue: Port already in use
**Solution:** Use a different port:
```bash
python manage.py runserver 0.0.0.0:8001
```

### Issue: Connection refused
**Solutions:**
1. Make sure the server is running
2. Check the IP address is correct
3. Verify network connectivity
4. Check firewall/antivirus settings

---

## Security Notes

⚠️ **Important:** The Django development server (`runserver`) is **NOT** suitable for production use.

**For production:**
- Use a proper web server (Nginx, Apache)
- Use a WSGI server (Gunicorn, uWSGI)
- Enable HTTPS
- Configure proper security settings
- Set `DEBUG = False` in production

**For development:**
- Only use on trusted networks
- Don't expose to the public internet
- Keep `DEBUG = True` only in development

---

## Quick Reference

| Command | Access From | URL |
|---------|-------------|-----|
| `python3 manage.py runserver` | Same machine only | http://127.0.0.1:8000/ |
| `python3 manage.py runserver 127.0.0.1:8000` | Same machine only | http://127.0.0.1:8000/ |
| `python3 manage.py runserver 10.100.81.190:8000` | Network (if IP in ALLOWED_HOSTS) | http://10.100.81.190:8000/ |
| `python3 manage.py runserver 0.0.0.0:8000` | Network (any device) | http://YOUR_IP:8000/ |

**Mac M1 Note:** Replace `python3` with `python` if your system has `python` pointing to Python 3.
