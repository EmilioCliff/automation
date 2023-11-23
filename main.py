from flask import Flask, render_template, url_for, redirect, flash, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from random import randint, choice
import pandas as pd

# Sample URL
form_url = "https://forms.gle/ihRnBrWwQFcSetV9A"

# Read names file and remove unused columns
data = pd.read_csv('./baby-names.csv')
new_data = data.drop(['year', 'percent'], axis=1)


# FlaskForm to getting number of submission and the form link
class DataForm(FlaskForm):
    number = StringField("Number of entries", validators=[DataRequired()],
                         render_kw={'placeholder': 'Enter number of time to fill. Below 10 please'})
    link = URLField("Link to form", validators=[DataRequired()],
                    render_kw={'placeholder': 'Enter link to the google form to fill'})
    submit = SubmitField("Submit")


# Initialize app and setup people-added db
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuckMyDick'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///people-added.db"
Bootstrap5(app)
db = SQLAlchemy()
db.init_app(app)


# Create the db schema
class FilledForm(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), nullable=False)
    Reg_No = db.Column(db.String(50), nullable=False)
    Phone_No = db.Column(db.Integer, nullable=False)
    Course = db.Column(db.String(150), nullable=False)
    School = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()

# Function to sending the answers and submitting
def find_elements(driver, my_name, my_email, my_reg, my_no, my_course):
    name = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys(my_name)
    email = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys(my_email)
    reg_no = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys(my_reg)
    phone_no = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys(my_no)
    course = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys(my_course)
    school = driver.find_element(By.XPATH,'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/input').send_keys('COETEC')
    # driver.implicitly_wait(3)
    submit = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span').click()
    resubmit = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a').click()


@app.route('/', methods=['GET', 'POST'])
def home():
    form = DataForm()
    if form.validate_on_submit():
        number = form.number.data
        if int(number) > 10:
            flash('Bro just give me below 10 mahn')
            return redirect(url_for('home'))
        link = form.link.data
        if link != form_url:
            flash('Invalid link')
            redirect(url_for('home'))
        return render_template('time.html', number=number, link=link)
    return render_template("index.html", form=form)


@app.route("/sele")
def sele():
    number = int(request.args.get('number'))
    link = request.args.get('link')
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    wait = WebDriverWait(driver, 10)
    reg = {
        1: ['ENE'],
        2: ['221', '220'],
        3: [70, 280],
        4: [2018, 2023]
    }
    # Create random paramaters to fill the form
    for _ in range(number):
        my_no = f"+2547{''.join([str(randint(0, 9)) for _ in range(8)])}"
        course_list = ['TIE', 'MINING', 'GEGEIS', 'EECE']
        my_reg = "-".join([choice(reg[1]), choice(reg[2]), str(randint(a=reg[3][0], b=reg[3][1])),str(randint(a=reg[4][0], b=reg[4][1]))])
        my_name = choice(new_data['name'])
        my_email = f"{my_name.lower()}@gmail.com"
        my_course = choice(course_list)
        added = [my_name, my_email, my_reg, my_no, my_course, "COETEC"]
        # wait = WebDriverWait(driver, 10)
        try:
           find_elements(driver, my_name, my_email, my_reg, my_no, my_course)
        except:
            # wait = WebDriverWait(driver, 15)
            find_elements(driver, my_name, my_email, my_reg, my_no, my_course)
        new_submit = FilledForm(
            Name=my_name,
            Email=my_email,
            Reg_No=my_reg,
            Phone_No=my_no,
            Course=my_course,
            School='COETEC'
        )
        db.session.add(new_submit)
        db.session.commit()
    driver.quit()
    return render_template("close.html", added=added, number=number)


if __name__ == '__main__':
    app.run(debug=True)
