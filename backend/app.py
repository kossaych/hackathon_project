from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World"


@app.route("/update")
def update():
    os.system("cd ~/your-repo/backend && git reset --hard && git pull origin main")
    os.system("source ~/venv/bin/activate && pip install -r requirements.txt")
    os.system("touch yourapp_wsgi.py")  # reload
    return "Updated!"

if __name__ == "__main__":
    app.run()
