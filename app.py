from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sqlalchemy import text
import os
import logging
import click

# --------------------
# App Configuration
# --------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')

# PostgreSQL as default; override with DATABASE_URL if set in the environment.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --------------------
# Request Logging for Debugging
# --------------------
@app.before_request
def log_request_info():
    app.logger.info(f"Request Method: {request.method}, Path: {request.path}")


# Debugging database connection
try:
    with app.app_context():
        db.session.execute(text('SELECT 1'))  # Test simple query
    app.logger.info("Database connection successful!")
except Exception as e:
    app.logger.error(f"Database connection failed: {e}")

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# --------------------
# Models
# --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True, cascade='all, delete-orphan')

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company = db.Column(db.String(50), nullable=False)
    dealership = db.Column(db.String(50))
    horsepower = db.Column(db.Integer, nullable=False)
    engine_capacity = db.Column(db.Float, nullable=False)
    cylinders = db.Column(db.Integer, nullable=False)
    interior = db.relationship('Interior', backref='car', uselist=False, cascade='all, delete-orphan')
    finance = db.relationship('Finance', backref='car', uselist=False, cascade='all, delete-orphan')

class Interior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    leather_seats = db.Column(db.Boolean, default=False)
    ventilated_seats = db.Column(db.Boolean, default=False)
    infotainment_size = db.Column(db.Float)
    heated_steering = db.Column(db.Boolean, default=False)
    climate_control = db.Column(db.Boolean, default=False)

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    purchase_type = db.Column(db.String(20), nullable=False)
    downpayment = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    trade_in_value = db.Column(db.Float, default=0.0)
    additional_costs = db.Column(db.Float, default=0.0)
    car_price = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------
# CLI Command to Initialize Database
# --------------------
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo("Initialized the database.")

# --------------------
# Routes
# --------------------
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        app.logger.info(f"Signup attempt with username: {username}")

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)

        try:
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Signup failed: {e}")
            flash('An error occurred during signup. Please try again.', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_cars = Car.query.filter_by(user_id=current_user.id).order_by(Car.horsepower.desc()).all()
    return render_template('dashboard.html', cars=user_cars)

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        try:
            app.logger.info(f"Form Data Received: {request.form}")

            new_car = Car(
                user_id=current_user.id,
                company=request.form['company'].strip(),
                dealership=request.form['model'].strip(),
                horsepower=int(request.form['horsepower']),
                engine_capacity=float(request.form['engine_displacement']),
                cylinders=int(request.form['cylinders'])
            )
            db.session.add(new_car)
            db.session.flush()

            new_interior = Interior(
                car_id=new_car.id,
                leather_seats='premium_upholstery' in request.form,
                ventilated_seats='ventilated_seats' in request.form,
                infotainment_size=float(request.form.get('touchscreen_size', 0)),
                heated_steering='heated_steering' in request.form,
                climate_control=request.form.get('climate_control_type', 'no').lower() == 'yes'
            )
            db.session.add(new_interior)

            new_finance = Finance(
                car_id=new_car.id,
                purchase_type=request.form.get('purchase_type', 'buy'),
                downpayment=float(request.form.get('down_payment', 0)),
                interest_rate=float(request.form['interest_rate']),
                loan_term=int(request.form['loan_term']),
                trade_in_value=float(request.form.get('trade_in_value', 0)),
                additional_costs=float(request.form.get('additional_costs', 0)),
                car_price=float(request.form['car_price'])
            )
            db.session.add(new_finance)

            db.session.commit()
            flash('Car added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError as ve:
            db.session.rollback()
            app.logger.error(f"ValueError: {ve}")
            flash('Invalid input format. Please check your values.', 'danger')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Unexpected Error: {e}")
            flash('An error occurred while saving the car details.', 'danger')

    return render_template('add_car.html')

def calculate_scores(cars):
    if not cars:
        return [], [], []

    try:
        max_hp = max(car.horsepower for car in cars) or 1
        max_engine = max(car.engine_capacity for car in cars) or 1
        max_cylinders = max(car.cylinders for car in cars) or 1

        results = []
        for car in cars:
            # Performance Score (0-100)
            perf_score = (
                (car.horsepower / max_hp * 40) +
                (car.engine_capacity / max_engine * 30) +
                (car.cylinders / max_cylinders * 30)
            )

            # Interior Score (0-100)
            interior_score = (
                20 * int(car.interior.leather_seats) +
                15 * int(car.interior.ventilated_seats) +
                10 * int(car.interior.heated_steering) +
                min(car.interior.infotainment_size * 2, 20)  # Max 20 points for 10\"+ screens
            )

            # Financial Calculations
            monthly_interest = car.finance.interest_rate / 100 / 12
            total_payments = car.finance.downpayment + sum(
                (car.finance.downpayment * monthly_interest) * 
                (1 + monthly_interest) ** month 
                for month in range(car.finance.loan_term)
            )

            # Value Score (points per $1000)
            value_score = ((perf_score + interior_score) / (total_payments / 1000)) if total_payments else 0

            results.append({
                'car': car,
                'perf_score': round(perf_score, 1),
                'interior_score': round(interior_score, 1),
                'total_cost': round(total_payments, 2),
                'value_score': round(value_score, 2)
            })

        best_performance = sorted(results, key=lambda x: x['perf_score'], reverse=True)
        best_value = sorted(results, key=lambda x: x['value_score'], reverse=True)
        cheapest = sorted(results, key=lambda x: x['total_cost'])

        return best_performance[:3], best_value[:3], cheapest[:3]

    except Exception as e:
        app.logger.error(f'Error calculating scores: {e}')
        return [], [], []


@app.route('/results')
@login_required
def results():
    user_cars = Car.query.filter_by(user_id=current_user.id).all()
    best_perf, best_value, cheapest = calculate_scores(user_cars)

    cars_data = [
        {
            'company': result['car'].company,
            'perf_score': result['perf_score'],
            'value_score': result['value_score']
        }
        for result in best_perf + best_value + cheapest
    ]

    return render_template('results.html',
                           best_perf=best_perf,
                           best_value=best_value,
                           cheapest=cheapest,
                           cars_data=cars_data)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --------------------
# Run the App
# --------------------
application = app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
