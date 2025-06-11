from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- MODELO ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# --- FORMULARIO ---
class RegistrationForm(FlaskForm):
    full_name = StringField('Nombre Completo', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='Debe tener al menos 8 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')

    def validate_password(self, field):
        if (not any(c.isupper() for c in field.data) or
                not any(c.islower() for c in field.data) or
                not any(c.isdigit() for c in field.data)):
            raise ValidationError('La contraseña debe contener una mayúscula, una minúscula y un número.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este correo ya está registrado.')

# --- RUTAS ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. Bienvenido/a!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
def dashboard():
    return "Bienvenido/a al panel de usuario."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
