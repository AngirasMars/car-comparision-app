from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os
import logging
import click

# --------------------
# App Configuration
# --------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')

# PostgreSQL as default; override with DATABASE_URL if set in the environment.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
    climate_control = db.Column(db.Boolean, default=False)  # Add this line


class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    purchase_type = db.Column(db.String(20), nullable=False)  # Lease/Buy
    downpayment = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    trade_in_value = db.Column(db.Float, default=0.0)
    additional_costs = db.Column(db.Float, default=0.0)
    car_price = db.Column(db.Float, nullable=False)  # New field for car price




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

#-------------------
#Seeding the DB for purpose of testing, code to be removed when deployed
#-------------------

'''@app.cli.command("seed-db")
def seed_db():
    """Seed the database with sample data."""
    from werkzeug.security import generate_password_hash

    # Check if 'testuser' already exists
    existing_user = User.query.filter_by(username='testuser').first()
    if not existing_user:
        test_user = User(username='testuser', password=generate_password_hash('password123', method='pbkdf2:sha256'))
        db.session.add(test_user)
        db.session.flush()
    else:
        test_user = existing_user

    # Add cars
    cars = [
        Car(user_id=test_user.id, company='Tesla', dealership='Tesla Motors', horsepower=450, engine_capacity=0.0, cylinders=0),
        Car(user_id=test_user.id, company='Ford', dealership='Ford Dealership', horsepower=300, engine_capacity=2.5, cylinders=4),
        Car(user_id=test_user.id, company='BMW', dealership='BMW Dealership', horsepower=320, engine_capacity=3.0, cylinders=6),
        Car(user_id=test_user.id, company='Toyota', dealership='Toyota Center', horsepower=200, engine_capacity=1.8, cylinders=4),
        Car(user_id=test_user.id, company='Chevrolet', dealership='Chevy Dealer', horsepower=400, engine_capacity=6.2, cylinders=8),
    ]
    db.session.add_all(cars)
    db.session.flush()

    # Add interiors
    interiors = [
        Interior(car_id=cars[0].id, leather_seats=True, ventilated_seats=True, infotainment_size=15.0, heated_steering=True),
        Interior(car_id=cars[1].id, leather_seats=False, ventilated_seats=False, infotainment_size=8.0, heated_steering=False),
        Interior(car_id=cars[2].id, leather_seats=True, ventilated_seats=False, infotainment_size=10.0, heated_steering=True),
        Interior(car_id=cars[3].id, leather_seats=False, ventilated_seats=False, infotainment_size=7.0, heated_steering=False),
        Interior(car_id=cars[4].id, leather_seats=True, ventilated_seats=True, infotainment_size=12.0, heated_steering=True),
    ]
    db.session.add_all(interiors)

    # Add finance details with car_price included
    finances = [
        Finance(car_id=cars[0].id, purchase_type='buy', downpayment=5000, interest_rate=3.5, loan_term=60, trade_in_value=0, additional_costs=0, car_price=50000),
        Finance(car_id=cars[1].id, purchase_type='lease', downpayment=2000, interest_rate=4.0, loan_term=36, trade_in_value=0, additional_costs=0, car_price=30000),
        Finance(car_id=cars[2].id, purchase_type='buy', downpayment=4000, interest_rate=3.0, loan_term=48, trade_in_value=0, additional_costs=0, car_price=45000),
        Finance(car_id=cars[3].id, purchase_type='lease', downpayment=1500, interest_rate=4.5, loan_term=24, trade_in_value=0, additional_costs=0, car_price=25000),
        Finance(car_id=cars[4].id, purchase_type='buy', downpayment=7000, interest_rate=3.8, loan_term=72, trade_in_value=0, additional_costs=0, car_price=60000),
    ]
    db.session.add_all(finances)

    db.session.commit()
    print("Database seeded with multiple cars!")'''





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
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
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
            print("Form Data Received:", request.form)  # Debugging line to check form data

            # Create Car
            new_car = Car(
                user_id=current_user.id,
                company=request.form['company'].strip(),
                dealership=request.form['model'].strip(),  # Assuming 'model' represents the dealership name
                horsepower=int(request.form['horsepower']),
                engine_capacity=float(request.form['engine_displacement']),
                cylinders=int(request.form['cylinders'])
            )
            db.session.add(new_car)
            db.session.flush()  # To get new_car.id before committing

            # Create Interior
            new_interior = Interior(
                car_id=new_car.id,
                leather_seats='premium_upholstery' in request.form,
                ventilated_seats='ventilated_seats' in request.form,
                infotainment_size=float(request.form.get('touchscreen_size', 0)),
                heated_steering='heated_steering' in request.form,
                climate_control=request.form.get('climate_control_type', 'no').lower() == 'yes'
            )
            db.session.add(new_interior)

            # Create Finance
            new_finance = Finance(
                car_id=new_car.id,
                purchase_type=request.form['purchase_type'] if 'purchase_type' in request.form else 'buy',
                downpayment=float(request.form.get('down_payment', 0)),
                interest_rate=float(request.form['interest_rate']),
                loan_term=int(request.form['loan_term']),
                trade_in_value=float(request.form.get('trade_in_value', 0)),
                additional_costs=float(request.form.get('additional_costs', 0)),
                car_price=float(request.form['car_price'])  # Capture car price from form
            )
            db.session.add(new_finance)

            db.session.commit()
            flash('Car added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError as ve:
            db.session.rollback()
            print(f"ValueError: {ve}")
            flash('Invalid input format. Please check your values.', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected Error: {e}")
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
            logging.info(f"Calculating scores for {car.company} with ID {car.id}")

            # Performance Score (0-100)
            perf_score = (
                (car.horsepower / max_hp * 40) +
                (car.engine_capacity / max_engine * 30) +
                (car.cylinders / max_cylinders * 30)
            )

            # Interior Score (0-100)
            if car.interior:
                interior_score = (
                    20 * int(car.interior.leather_seats) +
                    15 * int(car.interior.ventilated_seats) +
                    10 * int(car.interior.heated_steering) +
                    min(car.interior.infotainment_size * 2, 20)
                )
            else:
                logging.warning(f"No interior details found for car ID {car.id}")
                interior_score = 0

            # Financial Calculations
            if car.finance:
                logging.info(f"Finance details for car ID {car.id}: Car Price: {car.finance.car_price}, Downpayment: {car.finance.downpayment}")
                loan_amount = car.finance.car_price - car.finance.downpayment - car.finance.trade_in_value

                if loan_amount < 0:
                    loan_amount = 0  # Prevent negative loan amounts

                monthly_interest = car.finance.interest_rate / 100 / 12

                if monthly_interest > 0:
                    monthly_payment = (loan_amount * monthly_interest) / (1 - (1 + monthly_interest) ** (-car.finance.loan_term))
                else:
                    monthly_payment = loan_amount / car.finance.loan_term

                total_loan_payments = monthly_payment * car.finance.loan_term
                total_cost = car.finance.downpayment + total_loan_payments + car.finance.additional_costs

                # Value Score (points per $1000)
                value_score = ((perf_score + interior_score) / (total_cost / 1000)) if total_cost else 0

                results.append({
                    'car': car,
                    'perf_score': round(perf_score, 1),
                    'interior_score': round(interior_score, 1),
                    'total_cost': round(total_cost, 2),
                    'value_score': round(value_score, 2)
                })
            else:
                logging.error(f"No finance details found for car ID {car.id}")

        best_performance = sorted(results, key=lambda x: x['perf_score'], reverse=True)
        best_value = sorted(results, key=lambda x: x['value_score'], reverse=True)
        cheapest = sorted(results, key=lambda x: x['total_cost'])

        return best_performance[:1], best_value[:1], cheapest[:1]

    except Exception as e:
        logging.error(f"Error calculating scores: {e}")
        flash('Error calculating scores. Please check your car entries.', 'danger')
        return [], [], []



@app.route('/results')
@login_required
def results():
    user_cars = Car.query.filter_by(user_id=current_user.id).all()
    best_perf, best_value, cheapest = calculate_scores(user_cars)

    # Prepare data for the chart
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



# Prevent browser caching (helpful with POST-Redirect-GET)
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

application = app  # This is necessary for Gunicorn to find the app

