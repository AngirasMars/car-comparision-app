# Car Comparison App

Welcome to the **Car Comparison App**! This web application allows users to compare various cars based on performance, interior features, and financial value. Users can sign up, add cars with detailed specifications, and visualize the best-performing, best-value, and cheapest cars through interactive charts.

---

## 🌟 **Features**

- 🚗 **Add and Compare Cars**: Input car details like horsepower, engine capacity, interior features, and financial data.
- 📊 **Interactive Charts**: Visualize performance vs. value with dynamic charts.
- 🔒 **User Authentication**: Sign up, log in, and manage personal car lists securely.
- 🌌 **Dark Mode**: Switch between light and dark themes for a personalized experience.
- ⏳ **Animated Loaders**: Smooth transitions enhance the user experience.

---

## 💡 **Tech Stack**

- **Frontend**: HTML, CSS, JavaScript, [Chart.js](https://www.chartjs.org/)
- **Backend**: Flask (Python), Flask-Login, SQLAlchemy
- **Database**: PostgreSQL
- **Deployment**: AWS Elastic Beanstalk

---

## 🚀 **Live Demo**

Check out the live app here: [**Car Comparison App**](http://your-aws-app-link.com)

---

## 📁 **Setup Instructions**

### 1. **Clone the Repository**
```bash
git clone https://github.com/AngirasMars/car-comparision-app.git
cd car-comparision-app
```

### 2. **Set Up Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure Environment Variables**
Create a `.env` file in the project root:
```
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://your_username:your_password@localhost/car_db
```

### 5. **Initialize the Database**
```bash
flask init-db
```

### 6. **Run the App Locally**
```bash
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🌐 **Deployment on AWS**

1. **Install Elastic Beanstalk CLI:**
```bash
pip install awsebcli
```

2. **Initialize Elastic Beanstalk:**
```bash
eb init
```
- Choose **Python** as the platform.

3. **Create an Environment and Deploy:**
```bash
eb create car-comparison-env
eb deploy
```

4. **Open the Live App:**
```bash
eb open
```

---

## 📊 **Database Setup with AWS RDS (Optional)**

To host the PostgreSQL database in the cloud:
1. Create a PostgreSQL instance in **AWS RDS**.
2. Update the `.env` file with the RDS endpoint.
3. Deploy the updated app to Elastic Beanstalk.

---

## 👍 **Contributing**

Feel free to fork this repo, submit issues, or make pull requests. Let’s improve the app together!

---

## 📅 **License**

This project is licensed under the **MIT License**.

---

## 🎉 **Author**

Made with passion by [**Angiras Bulusu**](https://www.linkedin.com/in/angiras-bulusu-333481218/). 🚀
