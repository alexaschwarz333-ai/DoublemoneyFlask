from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import Admin, User, Investment, Wallet, ReferralEarning, Settings
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# DoubleMoney Admin Routes
@app.route('/doublemoney/admin')
@app.route('/doublemoney/admin/')
def doublemoney_admin_index():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin')
def admin_index():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_dashboard'))

@app.route('/doublemoney/admin/login', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Statistics
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
    
    # Active wallets
    active_wallets = Wallet.query.filter_by(is_active=True).count()
    used_wallets = 0  # Wallets always stay in rotation
    
    # Referral statistics
    total_referral_earnings = ReferralEarning.query.count()
    pending_payouts = ReferralEarning.query.filter_by(status='pending').count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_investments': total_investments,
        'pending_investments': pending_investments,
        'confirmed_investments': confirmed_investments,
        'completed_investments': completed_investments,
        'total_invested': total_invested,
        'total_profit': total_profit,
        'active_wallets': active_wallets,
        'used_wallets': used_wallets,
        'total_referral_earnings': total_referral_earnings,
        'pending_payouts': pending_payouts
    }
    
    # Recent activities
    recent_investments = Investment.query.order_by(Investment.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_investments=recent_investments,
                         recent_users=recent_users)

@app.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.phone.contains(search))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@app.route('/admin/user/<int:user_id>/toggle_status')
def admin_toggle_user_status(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.phone} has been {status}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/reset_password', methods=['POST'])
def admin_reset_user_password(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long!', 'error')
    else:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Password reset for user {user.phone}!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/investments')
def admin_investments():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Investment.query
    if status_filter:
        query = query.filter(Investment.status == status_filter)
    
    investments = query.order_by(Investment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/investments.html',
                         investments=investments,
                         status_filter=status_filter)

@app.route('/admin/investment/<int:investment_id>/confirm')
def admin_confirm_investment(investment_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
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
    
    return redirect(url_for('admin_investments'))

@app.route('/admin/investment/<int:investment_id>/cancel')
def admin_cancel_investment(investment_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    investment = Investment.query.get_or_404(investment_id)
    
    if investment.status in ['pending', 'confirmed']:
        investment.status = 'cancelled'
        
        # Wallet remains in rotation (no need to mark as used/unused)
        
        db.session.commit()
        flash(f'Investment #{investment.id} has been cancelled!', 'success')
    else:
        flash('Investment cannot be cancelled!', 'error')
    
    return redirect(url_for('admin_investments'))

@app.route('/admin/wallets')
def admin_wallets():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    wallets = Wallet.query.order_by(Wallet.created_at.desc()).all()
    return render_template('admin/wallets.html', wallets=wallets)

@app.route('/admin/wallet/add', methods=['POST'])
def admin_add_wallet():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    address = request.form['address']
    currency = request.form['currency']
    network = request.form['network']
    
    # Check if wallet already exists
    existing_wallet = Wallet.query.filter_by(address=address).first()
    if existing_wallet:
        flash('Wallet address already exists!', 'error')
    else:
        wallet = Wallet(
            address=address,
            currency=currency,
            network=network,
            is_active=True
        )
        db.session.add(wallet)
        db.session.commit()
        flash('Wallet added successfully!', 'success')
    
    return redirect(url_for('admin_wallets'))

@app.route('/admin/wallet/<int:wallet_id>/toggle_status')
def admin_toggle_wallet_status(wallet_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    wallet = Wallet.query.get_or_404(wallet_id)
    wallet.is_active = not wallet.is_active
    db.session.commit()
    
    status = 'activated' if wallet.is_active else 'deactivated'
    flash(f'Wallet has been {status}!', 'success')
    return redirect(url_for('admin_wallets'))

@app.route('/admin/user/<int:user_id>/details')
def admin_user_details(user_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
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

@app.route('/admin/referrals')
def admin_referrals():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = ReferralEarning.query
    if status_filter:
        query = query.filter(ReferralEarning.status == status_filter)
    
    referral_earnings = query.order_by(ReferralEarning.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/referrals.html',
                         referral_earnings=referral_earnings,
                         status_filter=status_filter)

@app.route('/admin/referral/<int:earning_id>/approve')
def admin_approve_referral(earning_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    earning = ReferralEarning.query.get_or_404(earning_id)
    
    if earning.status == 'pending' and datetime.utcnow() >= earning.payout_date:
        earning.status = 'approved'
        db.session.commit()
        flash('Referral earning approved for payout!', 'success')
    else:
        flash('Referral earning cannot be approved yet!', 'error')
    
    return redirect(url_for('admin_referrals'))

@app.route('/admin/referral/<int:earning_id>/pay')
def admin_pay_referral(earning_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    earning = ReferralEarning.query.get_or_404(earning_id)
    
    if earning.status == 'approved':
        earning.status = 'paid'
        earning.paid_at = datetime.utcnow()
        db.session.commit()
        flash('Referral earning marked as paid!', 'success')
    else:
        flash('Referral earning must be approved first!', 'error')
    
    return redirect(url_for('admin_referrals'))

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Update social media links
        Settings.set_setting('telegram_link', request.form.get('telegram_link', ''))
        Settings.set_setting('tiktok_link', request.form.get('tiktok_link', ''))
        Settings.set_setting('youtube_link', request.form.get('youtube_link', ''))
        Settings.set_setting('instagram_link', request.form.get('instagram_link', ''))
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    # Get current settings
    settings = {
        'telegram_link': Settings.get_setting('telegram_link', ''),
        'tiktok_link': Settings.get_setting('tiktok_link', ''),
        'youtube_link': Settings.get_setting('youtube_link', ''),
        'instagram_link': Settings.get_setting('instagram_link', '')
    }
    
    return render_template('admin/settings.html', settings=settings)
