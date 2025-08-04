import os
import logging
from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "mysql://root:password@localhost/doublemoney")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def check_investment_timers():
    """Check for completed investments and update referral earnings"""
    with app.app_context():
        from models import Investment, User, ReferralEarning
        from datetime import datetime
        
        # Find completed investments
        completed_investments = Investment.query.filter(
            Investment.status == 'confirmed',
            Investment.completion_date <= datetime.utcnow(),
            Investment.is_completed == False
        ).all()
        
        for investment in completed_investments:
            # Mark investment as completed
            investment.is_completed = True
            investment.final_amount = investment.amount * 2  # Double the money
            
            # Process referral earnings
            user = User.query.get(investment.user_id)
            if user.referred_by:
                referrer = User.query.get(user.referred_by)
                if referrer:
                    # Calculate referral percentage based on active referrals
                    active_referrals = User.query.filter(
                        User.referred_by == referrer.id,
                        User.has_active_investment == True
                    ).count()
                    
                    percentage = 0
                    if active_referrals >= 50:
                        percentage = 25
                    elif active_referrals >= 30:
                        percentage = 20
                    elif active_referrals >= 15:
                        percentage = 12
                    elif active_referrals >= 5:
                        percentage = 8
                    elif active_referrals >= 1:
                        percentage = 3
                    
                    if percentage > 0:
                        earning_amount = investment.amount * (percentage / 100)
                        earning = ReferralEarning(
                            user_id=referrer.id,
                            from_user_id=user.id,
                            investment_id=investment.id,
                            amount=earning_amount,
                            percentage=percentage,
                            payout_date=datetime.utcnow() + timedelta(days=10),
                            status='pending'
                        )
                        db.session.add(earning)
        
        db.session.commit()

# Schedule the timer check every minute
scheduler.add_job(
    func=check_investment_timers,
    trigger=IntervalTrigger(minutes=1),
    id='investment_timer_check',
    name='Check investment timers',
    replace_existing=True
)

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Create default admin user if doesn't exist
    from models import Admin
    from werkzeug.security import generate_password_hash
    
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@doublemoney.com'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: username=admin, password=admin123")

# Import routes
from routes import *
from admin_routes import *
