from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class BookingForm(FlaskForm):
    seat_number = IntegerField('Seat Number', validators=[DataRequired(), NumberRange(min=1, message="Invalid seat number.")])
    submit = SubmitField('Book')

class PaymentForm(FlaskForm):
    card_number = StringField(
        "Card Number",
        validators=[
            DataRequired(),
            Length(min=16, max=16),
            Regexp(r"^\d{16}$", message="Invalid card number"),
        ],
    )
    expiry_date = StringField(
        "Expiry Date",
        validators=[
            DataRequired(),
            Regexp(r"^(0[1-9]|1[0-2])/[0-9]{2}$", message="Invalid expiry date format (MM/YY)"),
        ],
    )
    cvv = StringField(
        "CVV",
        validators=[
            DataRequired(),
            Length(min=3, max=3),
            Regexp(r"^\d{3}$", message="Invalid CVV"),
        ],
    )
