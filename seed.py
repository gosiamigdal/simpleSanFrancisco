import model
import csv 
import datetime

def load_categories(session):
    # use u.categories - it has data about all categories 
    with open("seed_data/u.categories", "rb") as csvfile:
        categories = csv.reader(csvfile, delimiter="|")
        for category in categories:
            new_category = model.Category(id=category[0],name=category[1], symbol_url=category[2])
            session.add(new_category)
    session.commit()


def load_activities(session):
    # use u.activities - it has data about all activities 
    with open("seed_data/u.activities") as csvfile:
        activities = csv.reader(csvfile,delimiter="|")
        for activity in activities:
            new_activity = model.Activity(id=activity[0], title=activity[1], photo_url=activity[2], description=activity[3], category=activity[4])
            session.add(new_activity)
    session.commit()



def load_users(session):
    # use u.users - it has data about all users
    with open("seed_data/u.users") as csvfile:
        users = csv.reader(csvfile,delimiter="|")
        for user in users:
            new_user = model.User(id=user[0], email=user[1], password=user[2], salt=user[3])
            session.add(new_user)
    session.commit()


"""
def load_plans(session):
    # u.plans - it has data about all plans 
    with open("seed_data/u.plans") as csvfile:
        plans = csv.reader(csvfile, delimiter="|")
        for plan in plans:
            new_plan = model.Plan(id=plan[0], name=plan[1], start_date=plan[2], end_date=plan[3])
            session.add(new_plan)
    session.commit()


def load_timelines(session):
    # u.timelines - it has data about all plans
    with open("seed_data/u.timelines") as csvfile:
        timelines = csv.reader(csvfile,delimiter="|")
        for timeline in timelines:
            new_timeline = model.Timeline(id=timeline[0], date=timeline[1], timeslot1=timeline[2],timeslot2=timeline[3],timeslot3=timeline[4],
            timeslot4=timeline[5], timeslot5=timeline[6])
            session.add(new_timeline)
    session.commit()

"""

def main(session):
    load_categories(s)
    load_activities(s)
    load_users(s)
    #load_plans(s)
    #load_timelines(s)


if __name__ == "__main__":
#    s = model.connect()
    s = model.session
    main(s)
    