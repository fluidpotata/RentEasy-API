from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from api import server1
from server import server2
import os, datetime

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY", "AstrongSEcretKey")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
jwt = JWTManager(app)


CORS(app)


app.register_blueprint(server1)
app.register_blueprint(server2) 

@app.route('/')
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)
