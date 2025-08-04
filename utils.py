import random
import string
from flask import session
from models import User

def generate_referral_code(length=8):
    """Generate a unique referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        # Check if code already exists
        if not User.query.filter_by(referral_code=code).first():
            return code

def get_user_language():
    """Get user's preferred language from session or default to English"""
    return session.get('language', 'en')

def get_translation(key, lang=None):
    """Get translation for a specific key"""
    if lang is None:
        lang = get_user_language()
    
    from translations import TRANSLATIONS
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def format_currency(amount):
    """Format currency amount"""
    return f"${amount:,.2f}"

def format_phone(phone):
    """Format phone number for display"""
    if phone.startswith('+'):
        return phone
    return f"+{phone}"

def calculate_referral_level(active_referrals):
    """Calculate referral level based on active referrals count"""
    if active_referrals >= 50:
        return 5, 25
    elif active_referrals >= 30:
        return 4, 20
    elif active_referrals >= 15:
        return 3, 12
    elif active_referrals >= 5:
        return 2, 8
    elif active_referrals >= 1:
        return 1, 3
    return 0, 0

def get_next_referral_level(active_referrals):
    """Get next referral level requirements"""
    if active_referrals < 5:
        return 5, 3
    elif active_referrals < 15:
        return 15, 8
    elif active_referrals < 30:
        return 30, 12
    elif active_referrals < 50:
        return 50, 20
    else:
        return None, 25  # Max level reached

def get_referral_link(referral_code):
    """Generate referral link for doublemoney.pro"""
    return f"https://doublemoney.pro/register?ref={referral_code}"

def get_referral_status(user):
    """Get complete referral status information for user"""
    active_referrals = user.get_active_referrals_count()
    current_level, current_percentage = calculate_referral_level(active_referrals)
    next_required, next_percentage = get_next_referral_level(active_referrals)
    
    # Calculate progress to next level
    if next_required is not None:
        if current_level == 0:
            progress_percentage = (active_referrals / next_required) * 100
            remaining = next_required - active_referrals
        else:
            # Calculate progress within current level range
            level_thresholds = [0, 1, 5, 15, 30, 50]
            current_threshold = level_thresholds[current_level]
            progress_in_level = active_referrals - current_threshold
            level_range = next_required - current_threshold
            progress_percentage = (progress_in_level / level_range) * 100
            remaining = next_required - active_referrals
    else:
        progress_percentage = 100  # Max level reached
        remaining = 0
    
    return {
        'active_referrals': active_referrals,
        'current_level': current_level,
        'current_percentage': current_percentage,
        'next_required': next_required,
        'next_percentage': next_percentage,
        'progress_percentage': min(progress_percentage, 100),
        'remaining_referrals': remaining,
        'is_max_level': next_required is None
    }

def get_level_name(level):
    """Get user-friendly level names"""
    level_names = {
        0: "Starter",
        1: "Bronze", 
        2: "Silver",
        3: "Gold",
        4: "Platinum",
        5: "Diamond"
    }
    return level_names.get(level, "Unknown")

def get_level_benefits(level):
    """Get benefits description for each level"""
    benefits = {
        0: "Start referring friends to unlock rewards",
        1: "Earn 3% on all referral investments",
        2: "Earn 8% on all referral investments", 
        3: "Earn 12% on all referral investments",
        4: "Earn 20% on all referral investments",
        5: "Maximum tier: Earn 25% on all referral investments"
    }
    return benefits.get(level, "")
