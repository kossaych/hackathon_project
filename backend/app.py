from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World"

@app.route("/update")
def update():
    try:
        backend_path = "/home/hackathonharmonyteam/hackathon_project/backend"
        venv_python = "/home/hackathonharmonyteam/hackathon_project/backend/venv/bin/python3.10"  # adjust to your virtualenv python
        wsgi_file = "/var/www/hackathonharmonyteam_pythonanywhere_com_wsgi.py"

        # Pull latest code
        subprocess.check_call(f"cd {backend_path} && git reset --hard && git pull origin main", shell=True)

        # Install dependencies using virtualenv python
        subprocess.check_call(f"{venv_python} -m pip install -r {backend_path}/requirements.txt", shell=True)

        # Reload app
        subprocess.check_call(f"touch {wsgi_file}", shell=True)

        return "Updated successfully!"
    except subprocess.CalledProcessError as e:
        return f"Update failed: {e}"

if __name__ == "__main__":
    app.run()
