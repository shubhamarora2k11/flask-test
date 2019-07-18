import time
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ajax/index')
def ajax_index():
    time.sleep(5)
    return '<h1>Done!</h1>'

app.run()