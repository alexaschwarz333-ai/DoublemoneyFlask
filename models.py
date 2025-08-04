from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    country_code = db.Column(db.String(5), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    withdrawal_wallet = db.Column(db.String(100))
    referral_code = db.Column(db.String(10), unique=True, nullable=False)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    has_active_investment = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    investments = db.relationship('Investment', backref='user', lazy=True)
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    referral_earnings = db.relationship('ReferralEarning', foreign_keys='ReferralEarning.user_id', backref='user', lazy=True)
    referred_earnings = db.relationship('ReferralEarning', foreign_keys='ReferralEarning.from_user_id', backref='referred_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_active_referrals_count(self):
        return User.query.filter(
            User.referred_by == self.id,
            User.has_active_investment == True
        ).count()

    def get_referral_percentage(self):
        count = self.get_active_referrals_count()
        if count >= 50:
            return 25
        elif count >= 30:
            return 20
        elif count >= 15:
            return 12
        elif count >= 5:
            return 8
        elif count >= 1:
            return 3
        return 0

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), unique=True, nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # USDC or USDT
    network = db.Column(db.String(10), nullable=False)   # ERC20 or TRC20
    is_active = db.Column(db.Boolean, default=True)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    investments = db.relationship('Investment', backref='wallet', lazy=True)

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_hash = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    user_confirmed = db.Column(db.Boolean, default=False)  # User confirmed they sent deposit
    start_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    final_amount = db.Column(db.Float)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_time_remaining(self):
        if self.completion_date and self.status == 'confirmed':
            remaining = self.completion_date - datetime.utcnow()
            if remaining.total_seconds() > 0:
                return remaining
        return timedelta(0)

    def is_investment_complete(self):
        return self.completion_date and datetime.utcnow() >= self.completion_date

class ReferralEarning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    investment_id = db.Column(db.Integer, db.ForeignKey('investment.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid
    payout_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    # Relationships
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='generated_earnings')
    investment = db.relationship('Investment')

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_setting(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_setting(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = Settings(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
