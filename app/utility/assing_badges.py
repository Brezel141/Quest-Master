from app.models import Task, Badge
from flask import flash
from app.extensions import db

def assign_badges(user):
    completed_tasks = Task.query.filter_by(user_id=user.id, completed=True).count()

    # Define the rules for badges in a dictionary
    badge_rules = {
        1: 'Novice',
        5: 'Intermediate',
        10: 'Expert',
        20: 'Master'
    }

    # Get the names of the badges already assigned to the user
    existing_badges = [badge.name for badge in user.badges]

    for required_tasks, badge_name in badge_rules.items():
        if completed_tasks >= required_tasks and badge_name not in existing_badges:
            # Create a new badge and assign it to the user
            new_badge = Badge(name=badge_name, user_id=user.id)
            db.session.add(new_badge)
            flash(f'You have earned the "{badge_name}" badge!', 'info')

    db.session.commit()


def remove_badges(user):
    completed_tasks = Task.query.filter_by(user_id=user.id, completed=True).count()

    # Define the rules for badges in a dictionary
    badge_rules = {
        1: 'Novice',
        5: 'Intermediate',
        10: 'Expert',
        20: 'Master'
    }

    # Get the badges currently owned by the user
    user_badges = user.badges[:]  # Copy of the user's badge list

    for required_tasks, badge_name in badge_rules.items():
        if completed_tasks < required_tasks:
            # Find the badge in the user's badge list
            badge_to_remove = Badge.query.filter_by(name=badge_name, user_id=user.id).first()
            if badge_to_remove:
                db.session.delete(badge_to_remove)
                flash(f'You have lost the "{badge_name}" badge.', 'warning')
