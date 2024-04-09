from sqlalchemy import desc
from ..main import session
from ..models.user import User, Role


def run_queries():
    # all_users = session.query(User).all()
    # all_users2 = User.query.all()
    # print(all_users2)

    # first_user = User.query.first()
    # johns = User.query.filter_by(first_name="John").all()
    
    # johns = User.query.filter(User.first_name == "John").all()
    # print(f"JOHNS: {johns}")

    # gmail_users = User.query.filter(User.email.like("%@gmail.com")).all()
    # print(f"GMAIL_USERS: {gmail_users}")

    # super_admins = (
    #     User.query
    #     .join(User.roles)
    #     .filter(Role.slug == "super-admin")
    #     .all()
    # )

    users_by_name = (
        User.query
        .order_by(desc(User.first_name))
        .order_by(desc(User.last_name))
        .offset(2)
        .limit(3)
        .all()
    )

    print(users_by_name)





# run_queries()

import sys
print(sys.path)