import cohere
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


api_key = os.getenv("sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae")

if not api_key:
    api_key = "sEnd1kKmgJzH0URHfJYvXIkwuU1la4gShAhtBSae"  # fallback for local testing

co = cohere.Client(api_key)


class Form(FlaskForm):
    text = StringField('Enter text to search', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = Form()

    if form.validate_on_submit():
        text = form.text.data

        response = co.chat(
            model='command-nightly',
            message=text,
            max_tokens=300,
            temperature=0.9
        )

        output = response.text
        return render_template('index.html', form=form, output=output)

    return render_template('index.html', form=form, output=None)


if __name__ == "__main__":
    app.run(debug=True)