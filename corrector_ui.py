import flask
from flask import request, redirect, session
import os
import corrector
import pandas as pd


render_template = flask.render_template  # Required to render HTML Pages.
Flask = flask.Flask
app = Flask(__name__)


@app.route('/')
def main ():
    return render_template('index.html')


@app.route('/correct', methods=['POST'])
def correct():
    answers = request.form.getlist('question[]')
    inputfile = request.files.get('file')

    inputfile.save('input/'+inputfile.filename)
    
    answers = [question for question in answers if question]

    corrector.main(inputfile.filename, answers)
   
    df = pd.read_csv('static/output.csv')
    df.index += 1
    return df.to_html()


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.secret_key = os.urandom(12)  # Required for session encryption.
    app.jinja_env.add_extension('jinja2.ext.do')  # Enable do at the jinja level.
    app.run(debug=True)  # Line to comment if needed.
    # Enable this following line and comment the above line if you are running it at the server.
    # app.run(threaded=True, debug=True, host="tvmki271.test.sprint.com", port=7030)
