from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from datetime import datetime, timedelta
from time import time
import jwt
from flask import current_app

# Association table for Task-Tag relationship
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    points = db.Column(db.Integer, default=0)
    daily_streak = db.Column(db.Integer, default=0)
    last_completed_quest = db.Column(db.DateTime)
    theme_preference = db.Column(db.String(20), default='dark')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

    def update_streak(self):
        """Update daily streak based on quest completion."""
        now = datetime.utcnow()
        if self.last_completed_quest:
            days_diff = (now - self.last_completed_quest).days
            if days_diff > 1:
                self.daily_streak = 0
            elif days_diff == 1:
                self.daily_streak += 1
        self.last_completed_quest = now

    @property
    def level(self):
        """Calculate user level based on points with increasing XP requirements."""
        points = self.points
        level = 1
        xp_required = 100  # Base XP for level 1
        
        while points >= xp_required:
            points -= xp_required
            level += 1
            # Increase XP required for next level by 50%
            xp_required = int(xp_required * 1.5)
        
        return level

    @property
    def progress_to_next_level(self):
        """Calculate progress to next level as a percentage."""
        points = self.points
        level = 1
        xp_required = 100  # Base XP for level 1
        
        while points >= xp_required:
            points -= xp_required
            level += 1
            xp_required = int(xp_required * 1.5)
        
        return int((points / xp_required) * 100)

    @property
    def xp_for_next_level(self):
        """Get XP required for next level."""
        points = self.points
        xp_required = 100  # Base XP for level 1
        
        while points >= xp_required:
            points -= xp_required
            xp_required = int(xp_required * 1.5)
        
        return xp_required

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#4a90e2')  # Hex color code
    icon = db.Column(db.String(50), default='fa-tasks')  # Font Awesome icon
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='category', lazy=True)
    user = db.relationship('User', backref=db.backref('categories', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('tags', lazy=True))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Quest system fields
    quest_type = db.Column(db.String(20), default='side_quest')  # 'main_quest', 'side_quest', 'sub_quest'
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    difficulty = db.Column(db.String(20), default='normal')  # 'easy', 'normal', 'hard', 'epic'
    reward_points = db.Column(db.Integer, default=10)
    progress = db.Column(db.Integer, default=0)  # 0-100 for progress tracking
    time_spent = db.Column(db.Integer, default=0)  # Time spent in minutes
    priority = db.Column(db.Integer, default=2)  # 1 (high) to 3 (low)
    
    # Template fields
    is_template = db.Column(db.Boolean, default=False)
    template_name = db.Column(db.String(150), nullable=True)
    
    # Quest chain fields
    chain_position = db.Column(db.Integer, default=0)  # Position in quest chain
    chain_id = db.Column(db.Integer, db.ForeignKey('quest_chain.id'), nullable=True)
    prerequisites = db.Column(db.String(200), nullable=True)  # Comma-separated list of task IDs
    
    # Relationships
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    sub_quests = db.relationship('Task', backref=db.backref('parent', remote_side=[id]),
                                lazy='dynamic')
    tags = db.relationship('Tag', secondary=task_tags, lazy='subquery',
                          backref=db.backref('tasks', lazy=True))

    def calculate_progress(self):
        """Calculate progress based on completed sub-quests"""
        if not self.sub_quests.count():
            return 100 if self.completed else 0
        
        completed_sub_quests = sum(1 for q in self.sub_quests if q.completed)
        total_sub_quests = self.sub_quests.count()
        return int((completed_sub_quests / total_sub_quests) * 100)

    def update_progress(self):
        """Update progress and check if quest should be completed"""
        self.progress = self.calculate_progress()
        if self.progress == 100 and not self.completed:
            self.completed = True
            self.date_completed = datetime.utcnow()
            # Update parent quest progress if exists
            if self.parent:
                self.parent.update_progress()

    def get_reward_points(self):
        """Calculate reward points based on difficulty and other factors"""
        difficulty_multipliers = {
            'easy': 1,
            'normal': 1.5,
            'hard': 2,
            'epic': 3
        }
        base_points = {
            'main_quest': 100,
            'side_quest': 50,
            'sub_quest': 25
        }
        points = base_points.get(self.quest_type, 10) * difficulty_multipliers.get(self.difficulty, 1)
        
        # Add time bonus if completed before due date
        if self.completed and self.due_date and self.date_completed.date() < self.due_date:
            points *= 1.2
            
        return int(points)

class QuestChain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='chain', lazy=True)
    user = db.relationship('User', backref=db.backref('quest_chains', lazy=True))

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    icon = db.Column(db.String(50), default='fa-award')
    requirement_type = db.Column(db.String(50), nullable=False)  # 'quest_count', 'streak', 'category', 'difficulty'
    requirement_value = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # For category-specific badges
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_earned = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('badges', lazy=True))
