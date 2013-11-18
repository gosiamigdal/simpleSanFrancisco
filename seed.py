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
                new_activity = model.Activity(title=activity[1], photo_url=activity[2], description=activity[3],
                                                                category_id=activity[4],website_url=activity[5])
                print new_activity.title
                print new_activity.category_id
                session.add(new_activity)
    session.commit()

def create_users(session):
    emails = ["gosia@example.com", "doc@example.com"]
    for email in emails:
        user = model.User(email=email)
        user.set_password("password")
        session.add(user)
    session.commit()



if __name__ == "__main__":
    model.Base.metadata.create_all(model.engine)

    load_categories(model.session)
    load_activities(model.session)
    #create_users(model.session)
