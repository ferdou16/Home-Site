from flask import Flask, flash, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user
from flask_blogging import SQLAStorage, BloggingEngine
import sqlite3 as sql
from form import LoginForm
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True
db = SQLAlchemy(app)
mail = Mail(app)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"] # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = "/news"
app.config["BLOGGING_SITEURL"] = "http://localhost:8000"
app.config["BLOGGING_POSTS_PER_PAGE"] = 5
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mcss_home.db'
pathToDB = ''

app.config['MAIL_SERVER'] = os.environ["MAIL_SERVER"]
app.config['MAIL_PORT'] = int(os.environ["MAIL_PORT"])
app.config['MAIL_USE_SSL'] = bool(os.environ["MAIL_USE_SSL"])
app.config['MAIL_USERNAME'] = os.environ["MAIL_USERNAME"]
app.config['MAIL_PASSWORD'] = os.environ["MAIL_PASSWORD"]
app.config['MAIL_DEFAULT_SENDER'] = os.environ["MAIL_DEFAULT_SENDER"]

# extensions flask-blogging
engine = create_engine('sqlite:///' + pathToDB)
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)
mail = Mail(app)

#flask-bcrypt
bcrypt = Bcrypt(app)


# user class for providing authentication
class Users(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, name, password):
        self.username = name
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<username %r>' % self.username
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_name(self):
        return self.username

class User(UserMixin):

    def __init__(self, user_id):
        self.id = user_id

    def __repr__(self):
        return '<username %r>' % self.name

    def get_name(self):
        return self.name


login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter(Users.id == int(user_id)).first()

@blog_engine.user_loader
def load_user(user_id):
    return User(Users.query.filter(Users.id == 1).first().username)


@app.route("/login/", methods=['GET','POST'])
def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = Users.query.filter_by(username=request.form['username']).first()
            if user is not None and bcrypt.check_password_hash(user.password,request.form['password']):
                login_user(user)
                flash('You were logged in.')
                return render_template("index.html")
        else:
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form, error=error)

@app.route("/logout/")
def logout():
    logout_user()
    return render_template("index.html")


@app.route('/')
def initialize():
    return render_template("index.html")

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/new/')
def new():
    return redirect("/news")

@app.route('/events/')
def events():
    return render_template("events.html")

@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/404/')
def error_404():
    return render_template("404.html")

@app.route('/submit/', methods=['POST'])
def submit():
    #TODO: Lets work this into mailchimp.
    con = sql.connect("maildb.db")
    try:
        email = request.form['email']
        cur = con.cursor()
        cur.execute("INSERT INTO mail (email) VALUES (?)",(email,))
        con.commit()
        con.close()
        flash("You're now on our mailing list!")
        return redirect("/")
    except:
        con.close()
        return render_template("index.html")

@app.route('/feedback/', methods=['POST'])
def feedback():
    #TODO: A nicer layout is ideal, perhaps some captcha
    msg = Message("UTM MCSS has received feedback!")
    msg.add_recipient("contact@utmmcss.com")
    user_message = request.form['feedback']
    msg.html = """Feedback has been received! <br />
    From: """ + request.form['name'] + " &lt " + request.form['email'] + """ &gt <br /><br />
    """ + user_message + """<br /><br />
    Enjoy!"""
    mail.send(msg)
    flash("Your feedback has been sent!")
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
