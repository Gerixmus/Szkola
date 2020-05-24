import os
from flask import request
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

#this finds a path to our database

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "loginnewdatabase.db"))

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#below this line are all the classes we have in our database
#some of them also contain function that allows us to view content of particular tables

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(5))

class physicalResource(db.Model):
    resourceIdP = db.Column(db.Integer, primary_key=True)
    resourceQuantityP = db.Column(db.Integer())
    resourceManufacturer = db.Column(db.String(100))
    resourceModel = db.Column(db.String(100))
    resourceSerialNumber = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return "<ID: {} Quantity: {} Manufacturer: {} Model: {} Serial Number: {}>".format(self.title)

class virtualResource(db.Model):
    resourceIdV = db.Column(db.Integer, primary_key=True)
    resourceQuantityV = db.Column(db.Integer())
    OSManufacturer = db.Column(db.String(100))
    OSVersion = db.Column(db.String(100))

    def __repr__(self):
        return "<ID: {} Quantity: {} Manufacturer: {} Version: {}>".format(self.title)

class Lab(db.Model):
    labId = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    labName = db.Column(db.String(100))
    labType = db.Column(db.String(100))

    def __repr__(self):
        return "<labId:{} labName:{} labType: {}>".format(self.labId)
    
class Booking(db.Model):
    bookingId = db.Column(db.Integer, primary_key=True)
    bookingUserId = db.Column(db.Integer)
    bookingName = db.Column(db.String(100))
    bookingDate =db.Column(db.String(10))
    
    def __repr__(self):
        return "<bookingId: {} bookingUserId: {} bookingName: {} bookingDate: {}>".format(self.title)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

#below this line are all the functions that redirect us to different subpages

@app.errorhandler(404) 
  
#function that shows a message when you type site that doesn't exist

def not_found(e): 
  return render_template("404.html")

@app.route('/')
def index():
    return render_template('index.html')

#next funtion makes sure you are logged in before it redirects us to dashboard

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

#this function is responsible for registering new users and then adding their data to database

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        #return '<h1>New user has been created!</h1>'
        return render_template('new_user.html')

    return render_template('signup.html', form=form)

#dashboard is a place where you are navigated from to different sub pages

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

#this function shows all labs
#admin can manage them

@app.route('/labs', methods=["GET", "POST"])
@login_required
def home_labs():
    labs = None
    lab_role = current_user.role
    if request.form:
        try:
            lab = Lab(labId=request.form.get("labId"), labName=request.form.get("labName"), labType=request.form.get("labType"))
            db.session.add(lab)
            db.session.commit()
        except Exception as e:
            return render_template("error.html", site='/labs')
    if lab_role == "admin":
        labs = Lab.query.all()
        return render_template("labs_admin.html", labs=labs)
    else:
        labs = Lab.query.all()
        return render_template("labs_user.html", labs=labs)

#this functions deletes particular labs and then redirects you back to /labs

@app.route("/labs/delete", methods=["POST"])
@login_required
def delete_labs():
    labId = request.form.get("labId")
    lab = Lab.query.filter_by(labId=labId).first()
    db.session.delete(lab)
    db.session.commit()
    return redirect("/labs")   

#this function shows your current bookings and allows you to add / delete
#admin can manage all bookings

@app.route('/bookings', methods=["GET", "POST"])
@login_required
def home_bookings():
    bookings = None
    id = current_user.id
    booking_role = current_user.role
    if request.form:
        try:
            if booking_role == "admin":
                booking = Booking(bookingUserId=request.form.get("bookingUserId"), bookingName=request.form.get("bookingName"), bookingDate=request.form.get("bookingDate"))
                db.session.add(booking)
                db.session.commit() 
            else:
                booking = Booking(bookingUserId= id, bookingName=request.form.get("bookingName"), bookingDate=request.form.get("bookingDate"))
                db.session.add(booking)
                db.session.commit()
        except Exception as e:
            return render_template("error.html", site='/bookings')
    if booking_role == "admin":
        bookings = Booking.query.all()
        return render_template("bookings_admin.html", bookings=bookings)
    else:
        search = id
        bookingUserId = request.form.get("bookingUserId")
        bookings = Booking.query.filter(Booking.bookingUserId.like(search)).all()
        return render_template("bookings_user.html", bookings=bookings)

@app.route("/bookings/delete", methods=["POST"])
@login_required
def delete_bookings():
    bookingId = request.form.get("bookingId")
    booking = Booking.query.filter_by(bookingId=bookingId).first()
    db.session.delete(booking)
    db.session.commit()
    return redirect("/bookings")

#this function redirects you to a page with a calendar

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

#the next 2 functions are accesible only by admin
#admin can manage physical and virtual resources

@app.route('/physical', methods=["GET", "POST"])
@login_required
def physical():
    physical_resources = None
    physical_role = current_user.role
    if physical_role == "admin":
        if request.form:
            try:
                physical_resource = physicalResource(resourceIdP=request.form.get("resourceIdP"), resourceQuantityP=request.form.get("resourceQuantityP"), resourceManufacturer=request.form.get("resourceManufacturer"), resourceModel=request.form.get("resourceModel"), resourceSerialNumber=request.form.get("resourceSerialNumber"))
                db.session.add(physical_resource)
                db.session.commit()
            except Exception as e:
                return render_template("error.html", site='/physical')
        physical_resources = physicalResource.query.all()
        return render_template("physical.html", physical_resources=physical_resources)
    else:
        return redirect("/dashboard")

@app.route("/physical/delete", methods=["POST"])
@login_required
def delete_physical():
    resourceIdP = request.form.get("resourceIdP")
    physical_resource = physicalResource.query.filter_by(resourceIdP=resourceIdP).first()
    db.session.delete(physical_resource)
    db.session.commit()
    return redirect("/physical")

@app.route('/virtual', methods=["GET", "POST"])
@login_required
def virtual():
    virtual_resources = None
    virtual_role = current_user.role
    if virtual_role == "admin":    
        if request.form:
            try:
                virtual_resource = virtualResource(resourceIdV=request.form.get("resourceIdV"), resourceQuantityV=request.form.get("resourceQuantityV"), OSManufacturer=request.form.get("OSManufacturer"), OSVersion=request.form.get("OSVersion"))
                db.session.add(virtual_resource)
                db.session.commit()
            except Exception as e:
                return render_template("error.html", site='/virtual')
        virtual_resources = virtualResource.query.all()
        return render_template("virtual.html", virtual_resources=virtual_resources)
    #else:
        #return redirect("/dashboard")

@app.route("/virtual/delete", methods=["POST"])
@login_required
def delete_virtual():
    resourceIdV = request.form.get("resourceIdV")
    virtual_resource = virtualResource.query.filter_by(resourceIdV=resourceIdV).first()
    db.session.delete(virtual_resource)
    db.session.commit()
    return redirect("/virtual")

@app.route('/settings')
@login_required
def settings():
    return render_template('dashboard.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)     #this allows us to make changes without reloading app