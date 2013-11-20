from models import db, Category, Activity
import csv

def load_categories(session):
    # use u.categories - it has data about all categories 
    with open("seed_data/u.categories", "rb") as csvfile:
        categories = csv.reader(csvfile, delimiter="|")
        for category in categories:
            new_category = Category(id=category[0],name=category[1], symbol_url=category[2])
            session.add(new_category)
    session.commit()


def load_activities(session):
    # use u.activities - it has data about all activities 
    with open("seed_data/u.activities") as csvfile:
        activities = csv.reader(csvfile,delimiter="|")
        for activity in activities:
                new_activity = Activity(title=activity[1], photo_url=activity[2], description=activity[3],
                                        category_id=activity[4],website_url=activity[5])
                print new_activity.title
                print new_activity.category_id
                session.add(new_activity)
    session.commit()

if __name__ == "__main__":
    db.create_all()
    load_categories(db.session)
    load_activities(db.session)
