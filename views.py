from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Plan, Activity, Category, Timeline, TimelineActivity
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flaskext.markdown import Markdown
import config
import forms
import model
import datetime


app = Flask(__name__)
app.config.from_object(config)

timeslots = {0:"10am", 1:"12pm", 2:"2pm", 3:"4pm",4:"6pm"}

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
    timelines = plan.timelines
    timeline_activities = TimelineActivity.query.join(Timeline).join(Plan).join(Activity).filter(Plan.id==id)
    activities_by_timeslot = {}
    for activity in timeline_activities:
        t_id = activity.timeline_id
        #existing = activities_by_timeslot.get(t_id,[])
        #existing.append(activity)
        activities_by_timeslot[(t_id, activity.order)] = activity

    return render_template("plan.html", plan=plan, timelines=timelines, timeslots=timeslots, activities_by_timeslot=activities_by_timeslot)

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

    for day in plan.date_range():
        timeline = Timeline(date=day)
        plan.timelines.append(timeline)
    
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


@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>/category/<int:category_id>")
@login_required
def activities_for_timeslot(plan_id, day, order, category_id):
    category = Category.query.get(category_id)
    plan = Plan.query.get(plan_id)
    print category_id
    activities = Activity.query.filter_by(category_id=category_id).all()
    print activities
    return render_template("activities.html", category=category, plan=plan, order=order, day=day, timeslots=timeslots, activities=activities)
 


@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>")
def categories_for_timeslot(plan_id, day, order):
    categories = Category.query.all()
    plan = Plan.query.get(plan_id)
    return render_template("categories.html", categories=categories, plan=plan, order=order, day=day, timeslots=timeslots)


@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>/category/<int:category_id>", methods=["POST"])
@login_required
def select_activity_for_timeslot(plan_id, day, order, category_id):
    activity_id = request.form["activity_id"]
    activity_in_db = TimelineActivity.query.filter_by(timeline_id=day, order=order).first()
    if activity_in_db == None:
        timeline_activity = TimelineActivity(activity_id=activity_id, timeline_id=day, order=order)
        model.session.add(timeline_activity)
    else:
        activity_in_db.activity_id = activity_id
    model.session.commit()  
    return redirect(url_for("view_plan", id=plan_id))


if __name__ == "__main__":
    app.run(debug=True)



