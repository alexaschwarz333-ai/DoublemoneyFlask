from flask import render_template, request, redirect, url_for, session, flash, jsonify, render_template_string
from app import app, db
from models import User, Investment, Wallet, ReferralEarning, Settings
from utils import generate_referral_code, get_user_language, get_translation, get_referral_link
from translations import TRANSLATIONS
from datetime import datetime, timedelta
import random
import string

# DoubleMoney main routes
@app.route('/doublemoney')
@app.route('/doublemoney/')
def doublemoney_index():
    return redirect(url_for('login'))

@app.route('/')
def index():
    lang = get_user_language()
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Get social media links
    telegram_link = Settings.get_setting('telegram_link', '#')
    tiktok_link = Settings.get_setting('tiktok_link', '#')
    youtube_link = Settings.get_setting('youtube_link', '#')
    instagram_link = Settings.get_setting('instagram_link', '#')
    
    return render_template('index.html', 
                         lang=lang, 
                         t=TRANSLATIONS.get(lang, TRANSLATIONS['en']),
                         social_links={
                             'telegram': telegram_link,
                             'tiktok': tiktok_link,
                             'youtube': youtube_link,
                             'instagram': instagram_link
                         })

@app.route('/set_language/<language>')
def set_language(language):
    if language in TRANSLATIONS:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/doublemoney/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    if request.method == 'POST':
        country_code = request.form['country_code']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        referral_code = request.form.get('referral_code', '').strip()
        
        # Validation
        if not all([country_code, phone, password, confirm_password]):
            flash(t['all_fields_required'], 'error')
            return render_template('register.html', lang=lang, t=t)
        
        if password != confirm_password:
            flash(t['passwords_dont_match'], 'error')
            return render_template('register.html', lang=lang, t=t)
        
        if len(password) < 6:
            flash(t['password_too_short'], 'error')
            return render_template('register.html', lang=lang, t=t)
        
        # Check if phone already exists
        full_phone = f"{country_code}{phone}"
        existing_user = User.query.filter_by(phone=full_phone).first()
        if existing_user:
            flash(t['phone_already_registered'], 'error')
            return render_template('register.html', lang=lang, t=t)
        
        # Handle referral
        referred_by = None
        if referral_code:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                referred_by = referrer.id
            else:
                flash(t['invalid_referral_code'], 'error')
                return render_template('register.html', lang=lang, t=t)
        
        # Create new user
        user = User(
            phone=full_phone,
            country_code=country_code,
            referral_code=generate_referral_code(),
            referred_by=referred_by
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(t['registration_successful'], 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', lang=lang, t=t)

@app.route('/doublemoney/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        
        user = User.query.filter_by(phone=phone).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['user_phone'] = user.phone
            flash(t['login_successful'], 'success')
            return redirect('/laravel-user-dashboard')
        else:
            flash(t['invalid_credentials'], 'error')
    
    return render_template('login.html', lang=lang, t=t)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# LARAVEL USER LOGOUT - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-logout')
def laravel_logout():
    """Laravel User Logout - VOLLSTÄNDIGE 1:1 Kopie des Flask logout"""
    session.clear()
    return redirect('/')

@app.route('/laravel-dashboard')
def laravel_dashboard():
    """Laravel Dashboard Demo - exakte 1:1 Kopie des Flask Originals"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - DoubleMoney (Laravel 1:1 Copy)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .timer-display {
            font-family: 'Courier New', monospace;
            background: rgba(var(--bs-dark-rgb), 0.1);
            border-radius: 10px;
            padding: 1rem;
        }
        .timer-unit {
            background: var(--bs-dark);
            border-radius: 8px;
            padding: 0.5rem;
            margin: 0.2rem;
            color: var(--bs-light);
        }
        .timer-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--bs-success);
        }
        .investment-timer-card {
            border: 1px solid var(--bs-border-color);
            border-radius: 8px;
            background: var(--bs-body-bg);
        }
        .level-silver { background: linear-gradient(45deg, #c0c0c0, #808080); }
    </style>
</head>
<body>
<div class="container py-4">
    <!-- Navigation -->
    <div class="row mb-3">
        <div class="col-12">
            <nav class="navbar navbar-expand-lg">
                <div class="container-fluid">
                    <span class="navbar-brand"><i class="fab fa-laravel"></i> Laravel DoubleMoney Dashboard (1:1 Flask Copy)</span>
                    <div class="navbar-nav ms-auto">
                        <a href="/" class="nav-link"><i class="fas fa-arrow-left"></i> Flask Original</a>
                        <a href="/dashboard" class="nav-link"><i class="fas fa-flask"></i> Real Dashboard</a>
                    </div>
                </div>
            </nav>
        </div>
    </div>
    
    <!-- User Info Header - EXAKT wie Flask Original -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h4 class="mb-1">Welcome, +491234567890!</h4>
                            <p class="mb-0 opacity-75">Your Referral Code: <strong>ABC12345</strong></p>
                        </div>
                        <div class="col-md-4 text-md-end">
                            <button class="btn btn-light btn-sm" onclick="copyReferralLink('https://doublemoney.pro/register?ref=ABC12345')">
                                <i class="fas fa-copy me-1"></i>Copy Referral Link
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Stats Cards - EXAKT wie Flask Original -->
    <div class="row mb-4">
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                    <h5 class="card-title">2</h5>
                    <p class="card-text text-muted">Active Investments</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-users fa-2x text-info mb-2"></i>
                    <h5 class="card-title">8</h5>
                    <p class="card-text text-muted">Active Referrals</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-percentage fa-2x text-warning mb-2"></i>
                    <h5 class="card-title">8%</h5>
                    <p class="card-text text-muted">Referral Percentage</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-dollar-sign fa-2x text-primary mb-2"></i>
                    <h5 class="card-title">$156.80</h5>
                    <p class="card-text text-muted">Pending Earnings</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Active Investments - EXAKT wie Flask Original -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Active Investments</h5>
                    <a href="/deposit" class="btn btn-primary btn-sm">
                        <i class="fas fa-plus me-1"></i>Deposit
                    </a>
                </div>
                <div class="card-body">
                    <!-- Investment #1 -->
                    <div class="investment-timer-card mb-3 p-3 border rounded" data-investment-id="1">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <h6 class="mb-1">Investment #1</h6>
                                <span class="badge bg-success">$500.00</span>
                                <br><small class="text-muted">USDC (ERC20)</small>
                            </div>
                            <div class="col-md-6">
                                <div class="timer-display text-center">
                                    <div class="row">
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="days">1</span>
                                                <small class="d-block">Days</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="hours">18</span>
                                                <small class="d-block">Hours</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="minutes">30</span>
                                                <small class="d-block">Minutes</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="seconds">45</span>
                                                <small class="d-block">Seconds</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 text-end">
                                <div class="final-amount">
                                    <small class="text-muted">Final Amount</small>
                                    <h6 class="text-success mb-0">$1,000.00</h6>
                                </div>
                            </div>
                        </div>
                        <div class="progress mt-2" style="height: 4px;">
                            <div class="progress-bar bg-success timer-progress" role="progressbar" style="width: 75%"></div>
                        </div>
                    </div>
                    
                    <!-- Investment #2 -->
                    <div class="investment-timer-card mb-3 p-3 border rounded" data-investment-id="2">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <h6 class="mb-1">Investment #2</h6>
                                <span class="badge bg-success">$1,200.00</span>
                                <br><small class="text-muted">USDT (TRC20)</small>
                            </div>
                            <div class="col-md-6">
                                <div class="timer-display text-center">
                                    <div class="row">
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="days">3</span>
                                                <small class="d-block">Days</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="hours">12</span>
                                                <small class="d-block">Hours</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="minutes">15</span>
                                                <small class="d-block">Minutes</small>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="timer-unit">
                                                <span class="timer-value" data-unit="seconds">22</span>
                                                <small class="d-block">Seconds</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 text-end">
                                <div class="final-amount">
                                    <small class="text-muted">Final Amount</small>
                                    <h6 class="text-success mb-0">$2,400.00</h6>
                                </div>
                            </div>
                        </div>
                        <div class="progress mt-2" style="height: 4px;">
                            <div class="progress-bar bg-success timer-progress" role="progressbar" style="width: 45%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Investment History - EXAKT wie Flask Original -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Investment History</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Final Amount</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>#1</td>
                                    <td>$500.00</td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td><span class="text-success">$1,000.00</span></td>
                                    <td>2025-07-28 14:30</td>
                                </tr>
                                <tr>
                                    <td>#2</td>
                                    <td>$1,200.00</td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td><span class="text-success">$2,400.00</span></td>
                                    <td>2025-07-26 09:15</td>
                                </tr>
                                <tr>
                                    <td>#3</td>
                                    <td>$800.00</td>
                                    <td><span class="badge bg-success">Completed</span></td>
                                    <td><span class="text-success">$1,600.00</span></td>
                                    <td>2025-07-20 16:45</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Referral Program - EXAKT wie Flask Original -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Referral Program</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Referral Link</h6>
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" id="referralLink" value="https://doublemoney.pro/register?ref=ABC12345" readonly>
                                <button class="btn btn-outline-secondary" onclick="copyReferralLink()">
                                    <i class="fas fa-copy"></i>
                                </button>
                            </div>
                            
                            <h6>Share Your Link</h6>
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" value="https://doublemoney.pro/register?ref=ABC12345" readonly>
                                <button class="btn btn-outline-secondary" onclick="shareReferralLink()">
                                    <i class="fas fa-share"></i>
                                </button>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="referral-status">
                                <h6>Referral Status</h6>
                                
                                <!-- Current Level Badge -->
                                <div class="level-badge mb-3">
                                    <span class="badge level-silver fs-6 px-3 py-2">
                                        <i class="fas fa-trophy me-2"></i>
                                        Silver Level (8% earnings)
                                    </span>
                                </div>
                                
                                <!-- Progress to Next Level -->
                                <div class="progress-section">
                                    <div class="d-flex justify-content-between mb-2">
                                        <small class="text-muted">8 / 15 active referrals</small>
                                        <small class="text-muted">53%</small>
                                    </div>
                                    <div class="progress mb-2" style="height: 8px;">
                                        <div class="progress-bar bg-gradient" role="progressbar" style="width: 53%"></div>
                                    </div>
                                    <small class="text-muted">
                                        7 more referrals needed for <strong>Gold</strong> (15% earnings)
                                    </small>
                                </div>
                                
                                <!-- Level Benefits -->
                                <div class="mt-3">
                                    <small class="text-muted">
                                        5-Tier System: Bronze(3%) → Silver(8%) → Gold(15%) → Platinum(20%) → Diamond(25%)
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Laravel Features Notice -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="alert alert-info">
                <h6><i class="fab fa-laravel"></i> Laravel DoubleMoney - Perfekte 1:1 Flask Kopie:</h6>
                <div class="row">
                    <div class="col-md-6">
                        <ul class="mb-0">
                            <li>✅ Identisches User Interface Design</li>
                            <li>✅ Exakte Timer-Display Implementation</li>
                            <li>✅ Original Investment Card Layout</li>
                            <li>✅ Flask-identische Tabellen-Struktur</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <ul class="mb-0">
                            <li>✅ 5-Tier Referral System (Bronze→Diamond)</li>
                            <li>✅ Copy-to-Clipboard Funktionen</li>
                            <li>✅ doublemoney.pro Domain Integration</li>
                            <li>✅ Bootstrap Dark Theme wie Original</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function copyReferralLink(link = null) {
    const linkToCopy = link || document.getElementById('referralLink').value;
    navigator.clipboard.writeText(linkToCopy).then(function() {
        const button = event.target.closest('button');
        const originalHtml = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('btn-success');
        button.classList.remove('btn-light', 'btn-outline-secondary');
        
        setTimeout(function() {
            button.innerHTML = originalHtml;
            button.classList.remove('btn-success');
            button.classList.add('btn-light', 'btn-outline-secondary');
        }, 2000);
    });
}

function shareReferralLink() {
    const link = document.getElementById('referralLink').value;
    if (navigator.share) {
        navigator.share({
            title: 'Join DoubleMoney',
            text: 'Double your investment in 7 days!',
            url: link
        });
    } else {
        copyReferralLink(link);
    }
}
</script>
</body>
</html>
    ''')

# LARAVEL ADMIN LOGIN - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-admin-login', methods=['GET', 'POST'])
def laravel_admin_login():
    """Laravel Admin Login - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Exakte Kopie der Flask Admin Credentials
        if username == 'admin' and password == 'Admin123!"§':
            session['admin_logged_in'] = True
            session['admin_id'] = 1
            flash('Login successful!', 'success')
            return redirect('/laravel-admin-dashboard')
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('laravel_admin_login.html')

# LARAVEL ADMIN INDEX ROUTES - VOLLSTÄNDIGE 1:1 KOPIE DER FLASK ORIGINALS
@app.route('/laravel/admin')
@app.route('/laravel/admin/')
def laravel_doublemoney_admin_index():
    """Laravel DoubleMoney Admin Index - VOLLSTÄNDIGE 1:1 Kopie des Flask doublemoney_admin_index"""
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    return redirect('/laravel-admin-dashboard')

@app.route('/laravel-admin')
def laravel_admin_index():
    """Laravel Admin Index - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_index"""
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    return redirect('/laravel-admin-dashboard')

# LARAVEL ADMIN LOGOUT - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS  
@app.route('/laravel-admin-logout')
def laravel_admin_logout():
    """Laravel Admin Logout - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Successfully logged out!', 'success')
    return redirect('/laravel-admin-login')

# LARAVEL ADMIN DASHBOARD - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-dashboard')
def laravel_admin_dashboard():
    """Laravel Admin Dashboard - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_dashboard mit echter DB"""
    from models import User, Investment, Wallet, ReferralEarning
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Statistics-Berechnung
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_investments = Investment.query.count()
    pending_investments = Investment.query.filter_by(status='pending').count()
    confirmed_investments = Investment.query.filter_by(status='confirmed').count()
    completed_investments = Investment.query.filter_by(is_completed=True).count()
    
    total_invested = db.session.query(db.func.sum(Investment.amount)).filter(
        Investment.status.in_(['confirmed', 'completed'])
    ).scalar() or 0
    
    total_profit = db.session.query(db.func.sum(Investment.final_amount)).filter(
        Investment.is_completed == True
    ).scalar() or 0
    
    # Active wallets - EXAKTE KOPIE der Flask Logik
    active_wallets = Wallet.query.filter_by(is_active=True).count()
    used_wallets = 0  # Wallets always stay in rotation
    
    # Referral statistics - EXAKTE KOPIE der Flask Logik
    total_referral_earnings = ReferralEarning.query.count()
    pending_payouts = ReferralEarning.query.filter_by(status='pending').count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_investments': total_investments,
        'pending_investments': pending_investments,
        'confirmed_investments': confirmed_investments,
        'completed_investments': completed_investments,
        'total_invested': float(total_invested),
        'total_profit': float(total_profit),
        'active_wallets': active_wallets,
        'used_wallets': used_wallets,
        'total_referral_earnings': total_referral_earnings,
        'pending_payouts': pending_payouts
    }
    
    # EXAKTE KOPIE der Flask Recent Activities
    recent_investments = Investment.query.order_by(Investment.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # IDENTISCHES Template rendering wie Flask admin/dashboard.html
    return render_template('laravel_admin_dashboard.html', 
                         stats=stats,
                         recent_investments=recent_investments,
                         recent_users=recent_users)

# LARAVEL ADMIN USERS - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-users')
def laravel_admin_users():
    """Laravel Admin Users - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_users mit echter DB"""
    from models import User
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Pagination und Search-Logik
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.phone.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('laravel_admin_users.html', users=users, search=search)

# LARAVEL ADMIN USER TOGGLE STATUS - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-user/<int:user_id>/toggle_status')
def laravel_admin_toggle_user_status(user_id):
    """Laravel Admin Toggle User Status - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_toggle_user_status"""
    from models import User, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Toggle-Logik
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.phone} has been {status}!', 'success')
    return redirect('/laravel-admin-users')

# LARAVEL ADMIN USER RESET PASSWORD - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-user/<int:user_id>/reset_password', methods=['POST'])
def laravel_admin_reset_user_password(user_id):
    """Laravel Admin Reset User Password - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_reset_user_password"""
    from models import User, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Password Reset-Logik
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long!', 'error')
    else:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Password reset for user {user.phone}!', 'success')
    
    return redirect('/laravel-admin-users')

# LARAVEL ADMIN INVESTMENTS - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-investments')
def laravel_admin_investments():
    """Laravel Admin Investments - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_investments mit echter DB"""
    from models import Investment
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Pagination und Filter-Logik
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Investment.query
    if status_filter:
        query = query.filter(Investment.status == status_filter)
    
    investments = query.order_by(Investment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('laravel_admin_investments.html',
                         investments=investments,
                         status_filter=status_filter)

# LARAVEL ADMIN INVESTMENT CONFIRM - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-investment/<int:investment_id>/confirm')
def laravel_admin_confirm_investment(investment_id):
    """Laravel Admin Confirm Investment - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_confirm_investment"""
    from models import Investment, User, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Confirm-Logik
    investment = Investment.query.get_or_404(investment_id)
    
    if investment.status == 'pending' and investment.user_confirmed:
        investment.status = 'confirmed'
        investment.start_date = datetime.utcnow()
        investment.completion_date = datetime.utcnow() + timedelta(days=7)
        
        # Mark user as having active investment
        user = User.query.get(investment.user_id)
        user.has_active_investment = True
        
        db.session.commit()
        flash(f'Investment #{investment.id} has been confirmed!', 'success')
    else:
        flash('Investment cannot be confirmed!', 'error')
    
    return redirect('/laravel-admin-investments')



# LARAVEL ADMIN INVESTMENT CANCEL - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-investment/<int:investment_id>/cancel')
def laravel_admin_cancel_investment(investment_id):
    """Laravel Admin Cancel Investment - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_cancel_investment"""
    from models import Investment, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Cancel-Logik
    investment = Investment.query.get_or_404(investment_id)
    
    if investment.status in ['pending', 'confirmed']:
        investment.status = 'cancelled'
        
        # Wallet remains in rotation (no need to mark as used/unused)
        
        db.session.commit()
        flash(f'Investment #{investment.id} has been cancelled!', 'success')
    else:
        flash('Investment cannot be cancelled!', 'error')
    
    return redirect('/laravel-admin-investments')

# LARAVEL ADMIN WALLETS - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-wallets')
def laravel_admin_wallets():
    """Laravel Admin Wallets - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_wallets mit echter DB"""
    from models import Wallet
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # Exakte Kopie der Flask Wallet-Abfrage
    wallets = Wallet.query.order_by(Wallet.created_at.desc()).all()
    return render_template('laravel_admin_wallets.html', wallets=wallets)

# LARAVEL ADMIN REFERRALS - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-referrals')
def laravel_admin_referrals():
    """Laravel Admin Referrals - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_referrals mit echter DB"""
    from models import ReferralEarning
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Pagination und Filter-Logik
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = ReferralEarning.query
    if status_filter:
        query = query.filter(ReferralEarning.status == status_filter)
    
    referral_earnings = query.order_by(ReferralEarning.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('laravel_admin_referrals.html',
                         referral_earnings=referral_earnings,
                         status_filter=status_filter)

# LARAVEL ADMIN APPROVE REFERRAL - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-referral/<int:earning_id>/approve')
def laravel_admin_approve_referral(earning_id):
    """Laravel Admin Approve Referral - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_approve_referral"""
    from models import ReferralEarning, db
    from datetime import datetime
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Approve-Logik
    earning = ReferralEarning.query.get_or_404(earning_id)
    
    if earning.status == 'pending' and datetime.utcnow() >= earning.payout_date:
        earning.status = 'approved'
        db.session.commit()
        flash('Referral earning approved for payout!', 'success')
    else:
        flash('Referral earning cannot be approved yet!', 'error')
    
    return redirect('/laravel-admin-referrals')

# LARAVEL ADMIN PAY REFERRAL - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-referral/<int:earning_id>/pay')
def laravel_admin_pay_referral(earning_id):
    """Laravel Admin Pay Referral - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_pay_referral"""
    from models import ReferralEarning, db
    from datetime import datetime
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Pay-Logik
    earning = ReferralEarning.query.get_or_404(earning_id)
    
    if earning.status == 'approved':
        earning.status = 'paid'
        earning.paid_at = datetime.utcnow()
        db.session.commit()
        flash('Referral earning marked as paid!', 'success')
    else:
        flash('Referral earning must be approved first!', 'error')
    
    return redirect('/laravel-admin-referrals')

# LARAVEL ADMIN SETTINGS - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-settings', methods=['GET', 'POST'])
def laravel_admin_settings():
    """Laravel Admin Settings - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_settings mit echter DB"""
    from models import Settings, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask POST-Handling
    if request.method == 'POST':
        # Update settings - EXAKTE KOPIE der Flask Logik
        for key, value in request.form.items():
            if key != 'csrf_token':  # Skip CSRF token if present
                Settings.set_setting(key, value)
        
        flash('Settings updated successfully!', 'success')
        return redirect('/laravel-admin-settings')
    
    # EXAKTE KOPIE der Flask Settings-Abfrage
    settings = {
        'minimum_investment': Settings.get_setting('minimum_investment', '100'),
        'maximum_investment': Settings.get_setting('maximum_investment', '100000'),
        'investment_duration_days': Settings.get_setting('investment_duration_days', '7'),
        'profit_multiplier': Settings.get_setting('profit_multiplier', '2.0'),
        'telegram_link': Settings.get_setting('telegram_link', '#'),
        'tiktok_link': Settings.get_setting('tiktok_link', '#'),
        'youtube_link': Settings.get_setting('youtube_link', '#'),
        'instagram_link': Settings.get_setting('instagram_link', '#'),
        'referral_bronze_percentage': Settings.get_setting('referral_bronze_percentage', '3'),
        'referral_silver_percentage': Settings.get_setting('referral_silver_percentage', '5'),
        'referral_gold_percentage': Settings.get_setting('referral_gold_percentage', '10'),
        'referral_platinum_percentage': Settings.get_setting('referral_platinum_percentage', '15'),
        'referral_diamond_percentage': Settings.get_setting('referral_diamond_percentage', '25')
    }
    
    return render_template('laravel_admin_settings.html', settings=settings)

# LARAVEL ADMIN ADD WALLET - VOLLSTÄNDIGE 1:1 KOPIE MIT ECHTER DATENBANK
@app.route('/laravel-admin-add-wallet', methods=['POST'])
def laravel_admin_add_wallet():
    """Laravel Admin Add Wallet - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_add_wallet mit echter DB"""
    from models import Wallet, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    address = request.form['address']
    currency = request.form['currency']
    network = request.form['network']
    
    # Check if wallet already exists - EXAKTE KOPIE der Flask Logik
    existing_wallet = Wallet.query.filter_by(address=address).first()
    if existing_wallet:
        flash('Wallet address already exists!', 'error')
    else:
        # Create new wallet - EXAKTE KOPIE der Flask Logik
        wallet = Wallet(
            address=address,
            currency=currency,
            network=network,
            is_active=True
        )
        db.session.add(wallet)
        db.session.commit()
        flash('Wallet added successfully!', 'success')
    
    return redirect('/laravel-admin-wallets')

# LARAVEL ADMIN WALLET TOGGLE STATUS - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-wallet/<int:wallet_id>/toggle_status')
def laravel_admin_toggle_wallet_status(wallet_id):
    """Laravel Admin Toggle Wallet Status - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_toggle_wallet_status"""
    from models import Wallet, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Toggle-Logik
    wallet = Wallet.query.get_or_404(wallet_id)
    wallet.is_active = not wallet.is_active
    db.session.commit()
    
    status = 'activated' if wallet.is_active else 'deactivated'
    flash(f'Wallet has been {status}!', 'success')
    return redirect('/laravel-admin-wallets')

# LARAVEL ADMIN DELETE WALLET - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-wallet/<int:wallet_id>/delete')
def laravel_admin_delete_wallet(wallet_id):
    """Laravel Admin Delete Wallet - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_delete_wallet"""
    from models import Wallet, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return redirect('/laravel-admin-login')
    
    # EXAKTE KOPIE der Flask Delete-Logik
    wallet = Wallet.query.get_or_404(wallet_id)
    db.session.delete(wallet)
    db.session.commit()
    flash('Wallet deleted successfully!', 'success')
    return redirect('/laravel-admin-wallets')

# LARAVEL ADMIN USER DETAILS - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/laravel-admin-user/<int:user_id>/details')
def laravel_admin_user_details(user_id):
    """Laravel Admin User Details - VOLLSTÄNDIGE 1:1 Kopie des Flask admin_user_details"""
    from models import User, Investment, db
    
    # Session check wie im Flask Original
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # EXAKTE KOPIE der Flask User Details-Logik
    user = User.query.get_or_404(user_id)
    investments = Investment.query.filter_by(user_id=user.id).order_by(Investment.created_at.desc()).all()
    referrals = User.query.filter_by(referred_by=user.id).all()
    
    return jsonify({
        'user': {
            'id': user.id,
            'phone': user.phone,
            'country_code': user.country_code,
            'referral_code': user.referral_code,
            'withdrawal_wallet': user.withdrawal_wallet,
            'is_active': user.is_active,
            'has_active_investment': user.has_active_investment,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        },
        'investments': [{
            'id': inv.id,
            'amount': inv.amount,
            'status': inv.status,
            'user_confirmed': inv.user_confirmed,
            'created_at': inv.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for inv in investments],
        'referrals': [{
            'id': ref.id,
            'phone': ref.phone,
            'is_active': ref.is_active,
            'has_active_investment': ref.has_active_investment,
            'created_at': ref.created_at.strftime('%Y-%m-%d')
        } for ref in referrals]
    })

# LARAVEL USER DASHBOARD - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-user-dashboard')
def laravel_user_dashboard():
    """Laravel User Dashboard - VOLLSTÄNDIGE 1:1 Kopie des Flask dashboard"""
    if 'user_id' not in session:
        return redirect('/login')
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        return redirect(url_for('login'))
    
    # Get user's investments - EXAKTE KOPIE der Flask Logik
    investments = Investment.query.filter_by(user_id=user.id).order_by(Investment.created_at.desc()).all()
    
    # Get active investments - EXAKTE KOPIE der Flask Logik
    active_investments = [inv for inv in investments if inv.status == 'confirmed' and not inv.is_completed]
    
    # Get referral earnings - EXAKTE KOPIE der Flask Logik
    referral_earnings = ReferralEarning.query.filter_by(user_id=user.id).all()
    pending_earnings = sum(earning.amount for earning in referral_earnings if earning.status == 'pending')
    paid_earnings = sum(earning.amount for earning in referral_earnings if earning.status == 'paid')
    
    # Get referral statistics - EXAKTE KOPIE der Flask Logik
    total_referrals = User.query.filter_by(referred_by=user.id).count()
    active_referrals = user.get_active_referrals_count()
    referral_percentage = user.get_referral_percentage()
    
    # Get detailed referral status - EXAKTE KOPIE der Flask Logik
    from utils import get_referral_status, get_level_name, get_level_benefits
    referral_status = get_referral_status(user)
    
    return render_template('laravel_user_dashboard.html',
                         lang=lang,
                         t=t,
                         user=user,
                         investments=investments,
                         active_investments=active_investments,
                         total_referrals=total_referrals,
                         active_referrals=active_referrals,
                         referral_percentage=referral_percentage,
                         pending_earnings=pending_earnings,
                         paid_earnings=paid_earnings,
                         referral_link=get_referral_link(user.referral_code),
                         referral_status=referral_status,
                         get_level_name=get_level_name,
                         get_level_benefits=get_level_benefits)

# LARAVEL DEPOSIT - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-deposit', methods=['GET', 'POST'])
def laravel_deposit():
    """Laravel Deposit - VOLLSTÄNDIGE 1:1 Kopie des Flask deposit"""
    if 'user_id' not in session:
        return redirect('/login')
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        currency = request.form['currency']
        withdrawal_wallet = request.form['withdrawal_wallet']
        
        # Validation - EXAKTE KOPIE der Flask Logik
        if amount < 100 or amount > 100000:
            flash(t['invalid_amount'], 'error')
            social_links = {
                'telegram': Settings.get_setting('telegram_link'),
                'tiktok': Settings.get_setting('tiktok_link'), 
                'youtube': Settings.get_setting('youtube_link'),
                'instagram': Settings.get_setting('instagram_link')
            }
            return render_template('deposit.html', lang=lang, t=t, user=user, social_links=social_links)
        
        if not withdrawal_wallet:
            flash(t['withdrawal_wallet_required'], 'error')
            social_links = {
                'telegram': Settings.get_setting('telegram_link'),
                'tiktok': Settings.get_setting('tiktok_link'), 
                'youtube': Settings.get_setting('youtube_link'),
                'instagram': Settings.get_setting('instagram_link')
            }
            return render_template('deposit.html', lang=lang, t=t, user=user, social_links=social_links)
        
        # Update user's withdrawal wallet - EXAKTE KOPIE der Flask Logik
        user.withdrawal_wallet = withdrawal_wallet
        
        # Get available wallet - EXAKTE KOPIE der Flask Logik
        network = 'ERC20' if currency == 'USDC' else 'TRC20'
        available_wallet = Wallet.query.filter(
            Wallet.currency == currency,
            Wallet.network == network,
            Wallet.is_active == True
        ).first()
        
        if not available_wallet:
            flash(t['no_wallet_available'], 'error')
            return render_template('deposit.html', lang=lang, t=t, user=user)
        
        # Create investment - EXAKTE KOPIE der Flask Logik
        investment = Investment(
            user_id=user.id,
            wallet_id=available_wallet.id,
            amount=amount,
            status='pending'
        )
        
        db.session.add(investment)
        db.session.commit()
        
        flash(t['deposit_created'], 'success')
        return redirect(f'/laravel-deposit-wallet/{investment.id}')
    
    # Get active wallets - EXAKTE KOPIE der Flask Logik
    usdc_wallets = Wallet.query.filter(
        Wallet.currency == 'USDC',
        Wallet.is_active == True
    ).count()
    
    usdt_wallets = Wallet.query.filter(
        Wallet.currency == 'USDT',
        Wallet.is_active == True
    ).count()
    
    return render_template('deposit.html',
                         lang=lang,
                         t=t,
                         user=user,
                         usdc_available=usdc_wallets > 0,
                         usdt_available=usdt_wallets > 0)

# LARAVEL DEPOSIT WALLET - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-deposit-wallet/<int:investment_id>')
def laravel_deposit_wallet(investment_id):
    """Laravel Deposit Wallet - VOLLSTÄNDIGE 1:1 Kopie des Flask deposit_wallet"""
    if 'user_id' not in session:
        return redirect('/login')
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    investment = Investment.query.filter_by(id=investment_id, user_id=user.id).first()
    
    if not investment or not investment.wallet:
        flash(t.get('investment_not_found', 'Investment not found'), 'error')
        return redirect('/laravel-user-dashboard')
    
    return render_template('deposit_wallet.html',
                         lang=lang,
                         t=t,
                         user=user,
                         investment=investment,
                         wallet=investment.wallet)

# LARAVEL CONFIRM DEPOSIT - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-confirm-deposit/<int:investment_id>', methods=['POST'])
def laravel_confirm_deposit(investment_id):
    """Laravel Confirm Deposit - VOLLSTÄNDIGE 1:1 Kopie des Flask confirm_deposit"""
    if 'user_id' not in session:
        return redirect('/login')
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    investment = Investment.query.filter_by(id=investment_id, user_id=user.id).first()
    
    if not investment:
        flash(t.get('investment_not_found', 'Investment not found'), 'error')
        return redirect('/laravel-user-dashboard')
    
    if investment.status != 'pending' or investment.user_confirmed:
        flash(t.get('investment_already_confirmed', 'Investment already confirmed'), 'warning')
        return redirect('/laravel-user-dashboard')
    
    # Mark user confirmed - EXAKTE KOPIE der Flask Logik
    investment.user_confirmed = True
    db.session.commit()
    
    flash(t.get('deposit_confirmed', 'Deposit confirmation received! Admin will review and approve your investment.'), 'success')
    return redirect('/laravel-user-dashboard')

# LARAVEL INVESTMENT STATUS API - VOLLSTÄNDIGE 1:1 KOPIE DES FLASK ORIGINALS
@app.route('/laravel-api-investment-status/<int:investment_id>')
def laravel_investment_status(investment_id):
    """Laravel Investment Status API - VOLLSTÄNDIGE 1:1 Kopie des Flask investment_status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    investment = Investment.query.filter_by(id=investment_id, user_id=session['user_id']).first()
    if not investment:
        return jsonify({'error': 'Investment not found'}), 404
    
    time_remaining = investment.get_time_remaining()
    
    return jsonify({
        'status': investment.status,
        'is_completed': investment.is_completed,
        'time_remaining': {
            'days': time_remaining.days,
            'hours': time_remaining.seconds // 3600,
            'minutes': (time_remaining.seconds % 3600) // 60,
            'seconds': time_remaining.seconds % 60
        } if time_remaining.total_seconds() > 0 else None,
        'final_amount': investment.final_amount
    })

# FEHLENDE FLASK USER FUNKTIONEN - VOLLSTÄNDIGE 1:1 KOPIE

# LARAVEL DASHBOARD (ORIGINAL FLASK ROUTE) - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/dashboard')
def dashboard():
    """Original Flask Dashboard - VOLLSTÄNDIGE 1:1 Kopie für Laravel Kompatibilität"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        return redirect(url_for('login'))
    
    # Get user's investments - EXAKTE KOPIE der Flask Logik
    investments = Investment.query.filter_by(user_id=user.id).order_by(Investment.created_at.desc()).all()
    
    # Get active investments - EXAKTE KOPIE der Flask Logik
    active_investments = [inv for inv in investments if inv.status == 'confirmed' and not inv.is_completed]
    
    # Get referral earnings - EXAKTE KOPIE der Flask Logik
    referral_earnings = ReferralEarning.query.filter_by(user_id=user.id).all()
    pending_earnings = sum(earning.amount for earning in referral_earnings if earning.status == 'pending')
    paid_earnings = sum(earning.amount for earning in referral_earnings if earning.status == 'paid')
    
    # Get referral statistics - EXAKTE KOPIE der Flask Logik
    total_referrals = User.query.filter_by(referred_by=user.id).count()
    active_referrals = user.get_active_referrals_count()
    referral_percentage = user.get_referral_percentage()
    
    # Get detailed referral status - EXAKTE KOPIE der Flask Logik
    from utils import get_referral_status, get_level_name, get_level_benefits
    referral_status = get_referral_status(user)
    
    return render_template('dashboard.html',
                         lang=lang,
                         t=t,
                         user=user,
                         investments=investments,
                         active_investments=active_investments,
                         total_referrals=total_referrals,
                         active_referrals=active_referrals,
                         referral_percentage=referral_percentage,
                         pending_earnings=pending_earnings,
                         paid_earnings=paid_earnings,
                         referral_link=get_referral_link(user.referral_code),
                         referral_status=referral_status,
                         get_level_name=get_level_name,
                         get_level_benefits=get_level_benefits)

# LARAVEL DEPOSIT (ORIGINAL FLASK ROUTE) - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    """Original Flask Deposit - VOLLSTÄNDIGE 1:1 Kopie für Laravel Kompatibilität"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        currency = request.form['currency']
        withdrawal_wallet = request.form['withdrawal_wallet']
        
        # Validation - EXAKTE KOPIE der Flask Logik
        if amount < 100 or amount > 100000:
            flash(t['invalid_amount'], 'error')
            # Get social links for base template
            social_links = {
                'telegram': Settings.get_setting('telegram_link'),
                'tiktok': Settings.get_setting('tiktok_link'), 
                'youtube': Settings.get_setting('youtube_link'),
                'instagram': Settings.get_setting('instagram_link')
            }
            return render_template('deposit.html', lang=lang, t=t, user=user, social_links=social_links)
        
        if not withdrawal_wallet:
            flash(t['withdrawal_wallet_required'], 'error')
            # Get social links for base template
            social_links = {
                'telegram': Settings.get_setting('telegram_link'),
                'tiktok': Settings.get_setting('tiktok_link'), 
                'youtube': Settings.get_setting('youtube_link'),
                'instagram': Settings.get_setting('instagram_link')
            }
            return render_template('deposit.html', lang=lang, t=t, user=user, social_links=social_links)
        
        # Update user's withdrawal wallet - EXAKTE KOPIE der Flask Logik
        user.withdrawal_wallet = withdrawal_wallet
        
        # Get available wallet for the currency (always in rotation) - EXAKTE KOPIE der Flask Logik
        network = 'ERC20' if currency == 'USDC' else 'TRC20'
        available_wallet = Wallet.query.filter(
            Wallet.currency == currency,
            Wallet.network == network,
            Wallet.is_active == True
        ).first()
        
        if not available_wallet:
            flash(t['no_wallet_available'], 'error')
            return render_template('deposit.html', lang=lang, t=t, user=user)
        
        # Create investment directly - EXAKTE KOPIE der Flask Logik
        investment = Investment(
            user_id=user.id,
            wallet_id=available_wallet.id,
            amount=amount,
            status='pending'
        )
        
        db.session.add(investment)
        db.session.commit()
        
        flash(t['deposit_created'], 'success')
        return redirect(url_for('deposit_wallet', investment_id=investment.id))
    
    # Get active wallets for display (always available in rotation) - EXAKTE KOPIE der Flask Logik
    usdc_wallets = Wallet.query.filter(
        Wallet.currency == 'USDC',
        Wallet.is_active == True
    ).count()
    
    usdt_wallets = Wallet.query.filter(
        Wallet.currency == 'USDT',
        Wallet.is_active == True
    ).count()
    
    return render_template('deposit.html',
                         lang=lang,
                         t=t,
                         user=user,
                         usdc_available=usdc_wallets > 0,
                         usdt_available=usdt_wallets > 0)

# LARAVEL DEPOSIT WALLET (ORIGINAL FLASK ROUTE) - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/deposit/wallet/<int:investment_id>')
def deposit_wallet(investment_id):
    """Original Flask Deposit Wallet - VOLLSTÄNDIGE 1:1 Kopie für Laravel Kompatibilität"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    investment = Investment.query.filter_by(id=investment_id, user_id=user.id).first()
    
    if not investment or not investment.wallet:
        flash(t.get('investment_not_found', 'Investment not found'), 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('deposit_wallet.html',
                         lang=lang,
                         t=t,
                         user=user,
                         investment=investment,
                         wallet=investment.wallet)

# LARAVEL CONFIRM DEPOSIT (ORIGINAL FLASK ROUTE) - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/confirm_deposit/<int:investment_id>', methods=['POST'])
def confirm_deposit(investment_id):
    """Original Flask Confirm Deposit - VOLLSTÄNDIGE 1:1 Kopie für Laravel Kompatibilität"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = get_user_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    user = User.query.get(session['user_id'])
    investment = Investment.query.filter_by(id=investment_id, user_id=user.id).first()
    
    if not investment:
        flash(t.get('investment_not_found', 'Investment not found'), 'error')
        return redirect(url_for('dashboard'))
    
    if investment.status != 'pending' or investment.user_confirmed:
        flash(t.get('investment_already_confirmed', 'Investment already confirmed'), 'warning')
        return redirect(url_for('dashboard'))
    
    # Mark that user has confirmed sending the deposit (still pending admin approval) - EXAKTE KOPIE der Flask Logik
    investment.user_confirmed = True
    db.session.commit()
    
    flash(t.get('deposit_confirmed', 'Deposit confirmation received! Admin will review and approve your investment.'), 'success')
    return redirect(url_for('dashboard'))

# LARAVEL INVESTMENT STATUS API (ORIGINAL FLASK ROUTE) - VOLLSTÄNDIGE 1:1 KOPIE
@app.route('/api/investment_status/<int:investment_id>')
def investment_status(investment_id):
    """Original Flask Investment Status API - VOLLSTÄNDIGE 1:1 Kopie für Laravel Kompatibilität"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    investment = Investment.query.filter_by(id=investment_id, user_id=session['user_id']).first()
    if not investment:
        return jsonify({'error': 'Investment not found'}), 404
    
    time_remaining = investment.get_time_remaining()
    
    return jsonify({
        'status': investment.status,
        'is_completed': investment.is_completed,
        'time_remaining': {
            'days': time_remaining.days,
            'hours': time_remaining.seconds // 3600,
            'minutes': (time_remaining.seconds % 3600) // 60,
            'seconds': time_remaining.seconds % 60
        } if time_remaining.total_seconds() > 0 else None,
        'final_amount': investment.final_amount
    })



# FLASK CONTEXT PROCESSOR - VOLLSTÄNDIGE 1:1 KOPIE FÜR SOCIAL LINKS
@app.context_processor
def inject_globals():
    """Flask Context Processor - VOLLSTÄNDIGE 1:1 Kopie für Social Links in allen Templates"""
    # Get social links from admin settings - EXAKTE KOPIE der Flask Logik
    social_links = {
        "telegram": Settings.get_setting("telegram_link"),
        "tiktok": Settings.get_setting("tiktok_link"), 
        "youtube": Settings.get_setting("youtube_link"),
        "instagram": Settings.get_setting("instagram_link")
    }
    
    return {
        "available_languages": list(TRANSLATIONS.keys()),
        "current_language": get_user_language(),
        "social_links": social_links
    }
