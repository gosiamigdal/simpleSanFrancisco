from flask import Flask, render_template as flask_render_template, redirect, request, g, session, url_for, flash
from models import User, Plan, Activity, Category, Timeline, TimelineActivity, WeatherCache
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from flaskext.markdown import Markdown
import config
import forms
import requests
from models import db
import datetime
import calendar
import json
import forecastio
from app import app, admin, AuthenticatedModelView
import re
from fb_config import * 
from random import choice
lat = 37.761169
lng = -122.442112

timeslots = {0:"10am", 1:"12pm", 2:"2pm", 3:"4pm",4:"6pm"}

def render_template(template, **kwargs):
    kwargs["FB_APP_ID"] = FB_APP_ID
    kwargs["FB_DOMAIN"] = FB_DOMAIN
    return flask_render_template(template, **kwargs)


def generate_hash():
    items = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M",
    "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    url = []
    i = 0
    while i < 16:
        url.append(choice(items))
        i = i + 1
    url = "".join(url)
    return url


@app.template_filter('datetime')
def format_datetime(date, fmt='%c'):
    # check whether the value is a datetime object
    if not isinstance(date, (datetime.date, datetime.datetime)):
        try:
            date = datetime.datetime.strptime(str(date), '%Y-%m-%d').date()
        except Exception, e:
            return date
    return date.strftime(fmt)



@app.template_filter('quoted')
def quoted(s):
    l = re.findall('\'([^\'\.]*).+\'', str(s))
    if l:
        return l[0]
    return None

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
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/plans")
@login_required
def plans():
    plans = Plan.query.join(User).filter(User.id==current_user.get_id())
    return render_template("plans.html", plans=plans)


def forecast_for_day(day):
    now = datetime.datetime.now()
    day_since_epoch = calendar.timegm(day.utctimetuple()) / 60 / 60 / 24
    weather_cache = WeatherCache.query.get(day_since_epoch)
    if weather_cache == None:
        print "Loading from API", day_since_epoch
        forecast = forecastio.load_forecast(FORECAST_SECRET, lat, lng, units="auto", time=day)
        daily_weather = forecast.daily().data[0]
        cache = WeatherCache(id=day_since_epoch, weather=json.dumps(forecast.json["daily"]["data"][0]), update_time=now)
        db.session.add(cache)
        db.session.commit()
        return daily_weather
    else:
        if weather_cache.update_time + datetime.timedelta(days=1) < now and now <= day:
            print "Updating cache", day_since_epoch
            forecast = forecastio.load_forecast(FORECAST_SECRET, lat, lng, units="auto", time=day)
            daily_weather = forecast.daily().data[0]
            weather_cache.weather = json.dumps(forecast.json["daily"]["data"][0])
            weather_cache.update_time = now
            db.session.commit()
            return daily_weather
        else:
            print "Loading from cache", day_since_epoch
            parsed = json.loads(weather_cache.weather)
            return forecastio.models.ForecastioDataPoint(parsed)


@app.route("/plan/<int:id>")
@login_required
def view_plan(id):
    plan = Plan.query.get(id)
    if str(plan.user_id) != current_user.get_id():
        flash("Don't be evil! Access your plans only!")
        return redirect(url_for("index"))

    timelines = plan.timelines
    timeline_activities = TimelineActivity.query.join(Timeline).join(Plan).join(Activity).filter(Plan.id==id)
    activities_by_timeslot = {}
    for activity in timeline_activities:
        t_id = activity.timeline_id
        activities_by_timeslot[(t_id, activity.order)] = activity
    days = [(t, forecast_for_day(t.date)) for t in timelines]

    return render_template("plan.html", plan=plan, days=days, timeslots=timeslots, activities_by_timeslot=activities_by_timeslot)



@app.route("/plan/new")
def new_plan():
    if not current_user.is_authenticated():
        user = User()
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        login_user(user)
    return render_template("new_plan.html")


@app.route("/plan/new", methods=["POST"])
@login_required
def create_plan():
    form = forms.NewPlanForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_plan.html")

    if form.end_date.data < form.start_date.data:
        flash("Error, end date can't be earlier than start date")
        return render_template("new_plan.html")

    url = generate_hash()
    plan = Plan(name=form.name.data, start_date=form.start_date.data, end_date=form.end_date.data, hashed_url=url)
    if len(plan.date_range()) > 14:
        flash("Error, this trip is too log. You can choose maximum 14 days")
        return render_template("new_plan.html")
        
    current_user.plans.append(plan) 

    for day in plan.date_range():
        timeline = Timeline(date=day)
        plan.timelines.append(timeline)
    
    db.session.commit()
    db.session.refresh(plan)

    return redirect(url_for("view_plan", id=plan.id))



@app.route("/signup_or_login", methods=["POST"])
def signup_or_login():
    fb_id = request.form["fbId"]
    access_token = request.form["fbAccessToken"]
    r = requests.get("https://graph.facebook.com/debug_token", params={
        "input_token": access_token,
        "access_token": "%s|%s" % (FB_APP_ID, FB_SECRET)})
    response = r.json()["data"]
    if (not response["is_valid"]) or (str(response["user_id"]) != fb_id):
        return "Don't cheat!"
    existing_user = User.query.filter_by(fb_id=fb_id).first()
    if current_user.is_authenticated():
        user_id = current_user.get_id()
        if existing_user:
            # User already has account, but ask to connect to FB
            # Merge two accounts. User has been there, merged and now wants to merge again
            login_user(existing_user)
            plans = Plan.query.join(User).filter(User.id==user_id).all()
            for plan in plans:
                plan.user_id = existing_user.id
            db.session.commit()
        else:
            # Connect FB to new account: user first time on site
            user = User.query.get(user_id)
            user.fb_id = fb_id
            db.session.commit()
    else:       
        # User already exists, just log in 
        login_user(existing_user)
        # TODO: What if not exist?
    return "Success"


@app.route("/login")
def login():
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/summary/<int:id>")
@login_required
def see_summary(id):
    plan = Plan.query.get(id)
    if str(plan.user_id) != current_user.get_id():
        flash("Don't be evil! Access your plans only!")
        return redirect(url_for("index"))
    timelines = plan.timelines
    timeline_activities = TimelineActivity.query.join(Timeline).join(Plan).join(Activity).filter(Plan.id==id)
    activities_by_timeslot = {}
    for activity in timeline_activities:
        t_id = activity.timeline_id
        activities_by_timeslot[(t_id, activity.order)] = activity
    days = [(t, forecast_for_day(t.date)) for t in timelines]
    return render_template("summary.html", plan=plan, days=days, timeslots=timeslots, activities_by_timeslot=activities_by_timeslot)



@app.route("/guide/<string:hash>")
def see_guide(hash):
    plan = Plan.query.filter_by(hashed_url=hash).first()
    # TODO: if not exist
    timelines = plan.timelines
    timeline_activities = TimelineActivity.query.join(Timeline).join(Plan).join(Activity).filter(Plan.id==plan.id)
    activities_by_timeslot = {}
    for activity in timeline_activities:
        t_id = activity.timeline_id
        activities_by_timeslot[(t_id, activity.order)] = activity
    days = [(t, forecast_for_day(t.date)) for t in timelines]
    return render_template("guide.html", plan=plan, days=days, timeslots=timeslots, activities_by_timeslot=activities_by_timeslot)



@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>/category/<int:category_id>")
@login_required
def activities_for_timeslot(plan_id, day, order, category_id):
    category = Category.query.get(category_id)
    plan = Plan.query.get(plan_id)
    if str(plan.user_id) != current_user.get_id():
        flash("Don't be evil! Access your plans only!")
        return redirect(url_for("index"))

    activities = Activity.query.filter_by(category_id=category_id).all()
    return render_template("activities.html", category=category, plan=plan, order=order, day=day, timeslots=timeslots, activities=activities)
 


@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>")
@login_required
def categories_for_timeslot(plan_id, day, order):
    categories = Category.query.all()
    plan = Plan.query.get(plan_id)
    if str(plan.user_id) != current_user.get_id():
        flash("Don't be evil! Access your plans only!")
        return redirect(url_for("index"))

    return render_template("categories.html", categories=categories, plan=plan, order=order, day=day, timeslots=timeslots)


@app.route("/plan/<int:plan_id>/time/<int:day>/<int:order>/category/<int:category_id>", methods=["POST"])
@login_required
def select_activity_for_timeslot(plan_id, day, order, category_id):
    timeline = Timeline.query.join(Plan). \
      filter(Plan.user_id == current_user.get_id()). \
      filter(Plan.id == plan_id). \
      filter(Timeline.id == day).first()
    if not timeline:
        flash("Don't try to cheat!")
        return redirect(url_for("index"))
    activity_id = request.form["activity_id"]
    activity_in_db = TimelineActivity.query.filter_by(timeline_id=day, order=order).first()
    if activity_in_db == None:
        timeline_activity = TimelineActivity(activity_id=activity_id, timeline_id=day, order=order)
        db.session.add(timeline_activity)
    else:
        activity_in_db.activity_id = activity_id
    try:
        db.session.commit()  
    except Exception as e:
        print "ERROR while saving activity", e
        db.session.rollback()

    return redirect(url_for("view_plan", id=plan_id))


admin.add_view(AuthenticatedModelView(User, db.session))
admin.add_view(AuthenticatedModelView(Plan, db.session))
admin.add_view(AuthenticatedModelView(Category, db.session))
admin.add_view(AuthenticatedModelView(Activity, db.session))
admin.add_view(AuthenticatedModelView(Timeline, db.session))
admin.add_view(AuthenticatedModelView(TimelineActivity, db.session))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT,debug=True)
