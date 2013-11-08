from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Plan, Activity
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flaskext.markdown import Markdown
import config
import forms
import model
import datetime

app = Flask(__name__)
app.config.from_object(config)

def format_datetime(date, fmt='%c'):
    # check whether the value is a datetime object
    if not isinstance(date, (datetime.date, datetime.datetime)):
        try:
            date = datetime.datetime.strptime(str(date), '%Y-%m-%d').date()
        except Exception, e:
            return date
    return date.strftime(fmt)

app.jinja_env.filters['datetime'] = format_datetime

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    plans = Plan.query.all()
    return render_template("index.html", plans=plans)

@app.route("/plan/<int:id>")
def view_plan(id):
    plan = Plan.query.get(id)
    return render_template("plan.html", plan=plan)

@app.route("/plan/new")
@login_required
def new_plan():
    return render_template("new_plan.html")

@app.route("/plan/new", methods=["POST"])
@login_required
def create_plan():
    form = forms.NewPlanForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_plan.html")

    plan = Plan(name=form.name.data, start_date=form.start_date.data, end_date=form.end_date.data)
    current_user.plans.append(plan) 
    
    model.session.commit()
    model.session.refresh(plan)

    return redirect(url_for("view_plan", id=plan.id))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def authenticate():
    form = forms.LoginForm(request.form)
    if not form.validate():
        flash("Incorrect username or password") 
        return render_template("login.html")

    email = form.email.data
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("login.html")

    login_user(user)
    return redirect(request.args.get("next", url_for("index")))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/categories_display/<category_id>")
@login_required
def display_activities_for_category(category_id):
    activity = session.query(Activity).filter_by(category_id=5).all()
    # return render_template("categories_display.html",category_name=category_id)
    return activity



if __name__ == "__main__":
    app.run(debug=True)