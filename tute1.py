from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return "Home Working Fine!"

@app.route('/index')
def index():
    return "Index Working Correctely!"

@app.route('/about')
def about():
    return render_template('about.html',name="Manthan")

app.run(debug=True)