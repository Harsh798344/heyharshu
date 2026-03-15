import cohere
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Set a secret key for CSRF protection


class Form(FlaskForm):
    text = StringField('Enter text to search', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = Form()
    co = cohere.Client('sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae')

    if form.validate_on_submit():
        text = form.text.data
        response = co.chat(
            model='command-nightly',
            message=text,
            max_tokens=300,
            temperature=0.9,
            k=0,
            p=0.75,
            stop_sequences=[]
        )
        output = response.text
        return render_template('index.html', form=form, output=output)

    return render_template('index.html', form=form, output=None)


if __name__ == "__main__":
    app.run(debug=True)