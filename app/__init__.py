from flask import Flask

# Create a flask instance 
app = Flask(__name__)

from app import routes  