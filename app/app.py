import os

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

def result():
    q_result = "Nothing"
    return render_template("result.html", result=q_result)



if __name__ == "__main__":
    app.run(debug=True)
