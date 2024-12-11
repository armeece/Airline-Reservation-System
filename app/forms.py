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
            DataRequired(message="Card Number is required."),
            Length(min=16, max=16, message="Card Number must be 16 digits."),
            Regexp(r"^\d{16}$", message="Card Number must contain only digits."),
        ],
    )
    expiry_date = StringField(
        "Expiry Date (MM/YY)",
        validators=[
            DataRequired(message="Expiry Date is required."),
            Regexp(r"^(0[1-9]|1[0-2])/[0-9]{2}$", message="Invalid Expiry Date format. Use MM/YY."),
        ],
    )
    cvv = StringField(
        "CVV",
        validators=[
            DataRequired(message="CVV is required."),
            Length(min=3, max=3, message="CVV must be 3 digits."),
            Regexp(r"^\d{3}$", message="CVV must contain only digits."),
        ],
    )
    submit = SubmitField("Submit Payment")
