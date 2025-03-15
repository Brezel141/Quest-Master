from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .forms import RegistrationForm, LoginForm, TaskForm, ResetPasswordRequestForm, ResetPasswordForm, CategoryForm, TagForm, QuestChainForm
from .models import User, Task, Category, Tag, QuestChain
from .extensions import db, login_manager
from .utility.assing_badges import assign_badges, remove_badges
from flask_mail import Message
from .extensions import mail


main = Blueprint('main', __name__)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated:
        # Get all tasks including sub-quests
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        
        # Organize tasks by type and parent
        main_quests = []
        side_quests = []
        sub_quests = {}
        
        for task in tasks:
            if not task.completed:
                if task.quest_type == 'main_quest':
                    main_quests.append(task)
                elif task.quest_type == 'side_quest':
                    side_quests.append(task)
                elif task.quest_type == 'sub_quest' and task.parent_id:
                    if task.parent_id not in sub_quests:
                        sub_quests[task.parent_id] = []
                    sub_quests[task.parent_id].append(task)
        
        return render_template('index.html', 
                             tasks=tasks,
                             main_quests=main_quests,
                             side_quests=side_quests,
                             sub_quests=sub_quests)
    return render_template('index.html')

# Registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration completed successfully! Welcome to your quest.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by username or email
        user = User.query.filter((User.username == form.login.data) | 
                               (User.email == form.login.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Welcome back, adventurer!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Your quest has been paused. Come back soon!', 'info')
    return redirect(url_for('main.login'))

# Add task route
@main.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    
    # Get available categories and tags
    categories = Category.query.filter_by(user_id=current_user.id).all()
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    
    # Set choices for category and tags
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    form.tags.choices = [(t.id, t.name) for t in tags]
    
    # Get available parent quests for sub-quests
    available_main_quests = Task.query.filter_by(
        user_id=current_user.id,
        completed=False,
        quest_type='main_quest'
    ).all()
    
    if available_main_quests:
        form.parent_quest.choices = [('', 'Select a Main Quest...')] + [
            (str(t.id), t.title) for t in available_main_quests
        ]
    else:
        form.parent_quest.choices = [('', 'No main quests available - create one first!')]

    if form.validate_on_submit():
        if form.quest_type.data == 'sub_quest':
            if not available_main_quests:
                flash('You need to create a main quest before adding sub-quests!', 'warning')
                return redirect(url_for('main.add_task'))
            if form.parent_quest.data is None:
                flash('Please select a parent quest for your sub-quest.', 'warning')
                return render_template('add_task.html', form=form)

        # Set fixed reward points based on quest type
        if form.quest_type.data == 'main_quest':
            reward_points = 100
        elif form.quest_type.data == 'side_quest':
            reward_points = 50
        else:  # sub_quest
            reward_points = 25

        # Apply difficulty multiplier
        difficulty_multipliers = {
            'easy': 1,
            'normal': 1.5,
            'hard': 2,
            'epic': 3
        }
        reward_points = int(reward_points * difficulty_multipliers[form.difficulty.data])

        # Create a new task
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data if form.due_date.data else None,
            user_id=current_user.id,
            quest_type=form.quest_type.data,
            difficulty=form.difficulty.data,
            reward_points=reward_points,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            priority=form.priority.data
        )
        
        # Add selected tags
        if form.tags.data:
            selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            new_task.tags.extend(selected_tags)
        
        # Set parent quest if it's a sub-quest
        if form.quest_type.data == 'sub_quest' and form.parent_quest.data is not None:
            new_task.parent_id = form.parent_quest.data
        
        # Save as template if requested
        if form.is_template.data and form.template_name.data:
            new_task.is_template = True
            new_task.template_name = form.template_name.data
        
        # Save the new task to the database
        db.session.add(new_task)
        db.session.commit()
        
        flash('New quest added successfully! May fortune favor your journey!', 'success')
        return redirect(url_for('main.home'))

    return render_template('add_task.html', form=form)

# Mark task as completed route
@main.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify that the current user is the owner of the task
    if task.user_id != current_user.id:
        abort(403)  # Forbidden

    if not task.completed:
        task.completed = True
        task.date_completed = datetime.utcnow()
        
        # Award the points based on task's reward_points
        current_user.points += task.reward_points
        
        # We no longer automatically update parent quest progress
        db.session.commit()
        assign_badges(current_user)
        db.session.commit()
        
        flash(f'Quest completed! You earned {task.reward_points} points for your valor!', 'success')
    return redirect(url_for('main.home'))

# Uncomplete task route
@main.route('/uncomplete_task/<int:task_id>', methods=['POST'])
@login_required
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Verify that the current user is the owner of the task
    if task.user_id != current_user.id:
        abort(403)  # Forbidden

    if task.completed:
        task.completed = False
        task.date_completed = None
        db.session.commit()

        current_user.points -= 10
        remove_badges(current_user)
        db.session.commit()
        flash('Quest marked as incomplete. You lost 10 points.', 'info')
    return redirect(url_for('main.home'))

# Edit task route
@main.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Verify that the current user is the owner of the task    
    if task.user_id != current_user.id:
        abort(403)  # Forbidden

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash('Quest updated successfully!', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_task.html', form=form, task=task)

# Delete task route
@main.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify that the current user is the owner of the task
    if task.user_id != current_user.id:
        abort(403)  # Forbidden

    db.session.delete(task)
    db.session.commit()
    flash('Quest abandoned!', 'success')
    return redirect(url_for('main.home'))

# Get sub-quests for a task
@main.route('/get_sub_quests/<int:task_id>')
@login_required
def get_sub_quests(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    sub_quests = task.sub_quests.order_by(Task.completed, Task.date_created.desc()).all()
    return render_template('_sub_quests.html', sub_quests=sub_quests, parent=task)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = Message('Reset Your Password',
                  sender='noreply@questmaster.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('main.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@main.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('main.login'))
    return render_template('reset_password_request.html', form=form)

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired reset token', 'warning')
        return redirect(url_for('main.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form)

@main.route('/check_username/<username>')
def check_username(username):
    user = User.query.filter_by(username=username).first()
    return {'available': user is None}

@main.route('/user_stats')
@login_required
def user_stats():
    # Get quest statistics
    stats = {
        'total_main_quests': Task.query.filter_by(user_id=current_user.id, quest_type='main_quest').count(),
        'main_quests_completed': Task.query.filter_by(user_id=current_user.id, quest_type='main_quest', completed=True).count(),
        'total_side_quests': Task.query.filter_by(user_id=current_user.id, quest_type='side_quest').count(),
        'side_quests_completed': Task.query.filter_by(user_id=current_user.id, quest_type='side_quest', completed=True).count(),
        'total_sub_quests': Task.query.filter_by(user_id=current_user.id, quest_type='sub_quest').count(),
        'sub_quests_completed': Task.query.filter_by(user_id=current_user.id, quest_type='sub_quest', completed=True).count()
    }
    
    # Add total completed quests
    stats['total_completed'] = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    
    # Get list of earned badge names
    earned_badges = [badge.name for badge in current_user.badges]
    
    # Get recent completed quests
    recent_completed_quests = Task.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(Task.date_completed.desc()).limit(5).all()
    
    return render_template('user_stats.html',
                         user=current_user,
                         stats=stats,
                         earned_badges=earned_badges,
                         recent_completed_quests=recent_completed_quests)

@main.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            color=form.color.data,
            icon=form.icon.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{form.name.data}" created successfully!', 'success')
        return redirect(url_for('main.manage_categories'))
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_categories.html', form=form, categories=categories)

@main.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)
    
    # Update tasks to remove category
    Task.query.filter_by(category_id=category.id).update({Task.category_id: None})
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.manage_categories'))

@main.route('/tags', methods=['GET', 'POST'])
@login_required
def manage_tags():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(tag)
        db.session.commit()
        flash(f'Tag "{form.name.data}" created successfully!', 'success')
        return redirect(url_for('main.manage_tags'))
    
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_tags.html', form=form, tags=tags)

@main.route('/delete_tag/<int:tag_id>', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.user_id != current_user.id:
        abort(403)
    
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted successfully!', 'success')
    return redirect(url_for('main.manage_tags'))

