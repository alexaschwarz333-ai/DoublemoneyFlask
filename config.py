import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:password@localhost/doublemoney'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Application settings
    MIN_INVESTMENT = 100
    MAX_INVESTMENT = 100000
    INVESTMENT_DURATION_DAYS = 7
    REFERRAL_PAYOUT_DAYS = 10
    
    # Referral tiers
    REFERRAL_TIERS = {
        1: {'min_referrals': 5, 'percentage': 3},
        2: {'min_referrals': 15, 'percentage': 8},
        3: {'min_referrals': 30, 'percentage': 12},
        4: {'min_referrals': 50, 'percentage': 20},
        5: {'min_referrals': 50, 'percentage': 25}  # 50+ gets 25%
    }
    
    # Supported currencies and networks
    SUPPORTED_CURRENCIES = {
        'USDC': 'ERC20',
        'USDT': 'TRC20'
    }
    
    # Default social media links
    DEFAULT_SOCIAL_LINKS = {
        'telegram': 'https://t.me/doublemoney',
        'tiktok': 'https://tiktok.com/@doublemoney',
        'youtube': 'https://youtube.com/@doublemoney',
        'instagram': 'https://instagram.com/doublemoney'
    }
