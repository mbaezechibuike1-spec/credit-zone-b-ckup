#!/usr/bin/env python3
"""
CREDIT ZONE Backend - Complete with Referral System
Updated: Tap reward 5%, Full referral tracking
"""

import os
import json
import hashlib
import secrets
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
CORS(app)

# Create data folder
os.makedirs('data', exist_ok=True)

# File paths
USERS_FILE = 'data/users.json'
PENDING_FILE = 'data/pending.json'
REFERRALS_FILE = 'data/referrals.json'  # New file for referral tracking

# Initialize files
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(REFERRALS_FILE):
        with open(REFERRALS_FILE, 'w') as f:
            json.dump([], f)

init_files()

# Helper functions
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_pending():
    with open(PENDING_FILE, 'r') as f:
        return json.load(f)

def save_pending(pending):
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)

def load_referrals():
    with open(REFERRALS_FILE, 'r') as f:
        return json.load(f)

def save_referrals(referrals):
    with open(REFERRALS_FILE, 'w') as f:
        json.dump(referrals, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def generate_ref():
    return 'CZ' + secrets.token_hex(3).upper()

def find_user_by_email(users, email):
    for u in users:
        if u.get('email') == email:
            return u
    return None

def find_user_by_ref(users, ref):
    for u in users:
        if u.get('refCode') == ref:
            return u
    return None

def find_user_by_id(users, user_id):
    for u in users:
        if u.get('id') == user_id:
            return u
    return None

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        users = load_users()
        user = None
        for u in users:
            if u.get('token') == token:
                user = u
                break
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        return f(user, *args, **kwargs)
    return decorated

# ==================== ROUTES ====================

@app.route('/')
def home():
    users = load_users()
    referrals = load_referrals()
    return jsonify({
        'name': 'CREDIT ZONE API',
        'status': 'running',
        'users': len(users),
        'totalReferrals': len(referrals)
    })

# ============================================================
# AUTHENTICATION
# ============================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    ref_code = data.get('refCode', '')

    if not all([email, password, name]):
        return jsonify({'error': 'Missing fields'}), 400

    users = load_users()
    if find_user_by_email(users, email):
        return jsonify({'error': 'Email exists'}), 400

    referrer = None
    if ref_code:
        referrer = find_user_by_ref(users, ref_code.upper())
        if not referrer:
            return jsonify({'error': 'Invalid referral'}), 400

    # Generate unique referral code
    new_ref_code = generate_ref()
    
    new_user = {
        'id': secrets.token_hex(8),
        'name': name,
        'email': email,
        'password': hash_password(password),
        'refCode': new_ref_code,
        'referredBy': ref_code.upper() if ref_code else None,
        'vipLevel': 0,
        'balance': 0,
        'totalDeposits': 0,
        'totalWithdrawals': 0,
        'tapHistory': [],
        'activities': [],
        'deposits': [],
        'withdrawals': [],
        'vipSince': None,
        'createdAt': datetime.now().isoformat(),
        'lastTapTime': None,
        'token': secrets.token_hex(32)
    }

    users.append(new_user)
    save_users(users)

    # Record referral if applicable
    if referrer:
        referrals = load_referrals()
        referrals.append({
            'id': secrets.token_hex(8),
            'referrerId': referrer['id'],
            'referrerName': referrer['name'],
            'referrerCode': referrer['refCode'],
            'referredId': new_user['id'],
            'referredName': new_user['name'],
            'referredEmail': new_user['email'],
            'status': 'pending',  # pending, active, completed
            'createdAt': datetime.now().isoformat(),
            'depositAmount': 0,
            'bonusEarned': 0
        })
        save_referrals(referrals)
        
        # Add activity to referrer
        referrer['activities'] = referrer.get('activities', []) + [f'New referral: {new_user["name"]} signed up']
        users = load_users()
        for i, u in enumerate(users):
            if u['id'] == referrer['id']:
                users[i] = referrer
                break
        save_users(users)

    return jsonify({
        'message': 'Success',
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'refCode': new_user['refCode'],
            'token': new_user['token']
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    users = load_users()
    user = find_user_by_email(users, email)
    
    if not user or user.get('password') != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    user['token'] = secrets.token_hex(32)
    save_users(users)

    return jsonify({
        'message': 'Welcome back',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'refCode': user['refCode'],
            'token': user['token'],
            'balance': user['balance']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(user):
    users = load_users()
    u = find_user_by_id(users, user['id'])
    if u:
        u['token'] = None
        save_users(users)
    return jsonify({'message': 'Logged out'})

# ============================================================
# USER PROFILE
# ============================================================
@app.route('/api/user/profile', methods=['GET'])
@token_required
def profile(user):
    # Get referral stats
    referrals = load_referrals()
    my_referrals = [r for r in referrals if r.get('referrerId') == user['id']]
    total_referrals = len(my_referrals)
    active_referrals = len([r for r in my_referrals if r.get('status') == 'active'])
    
    # Calculate total earned from referrals
    total_earned = sum([r.get('bonusEarned', 0) for r in my_referrals])
    
    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'refCode': user['refCode'],
        'referredBy': user['referredBy'],
        'vipLevel': user['vipLevel'],
        'balance': user['balance'],
        'totalDeposits': user['totalDeposits'],
        'totalWithdrawals': user['totalWithdrawals'],
        'vipSince': user['vipSince'],
        'tapHistory': user.get('tapHistory', []),
        'activities': user.get('activities', []),
        'deposits': user.get('deposits', []),
        'withdrawals': user.get('withdrawals', []),
        'lastTapTime': user.get('lastTapTime'),
        'referralStats': {
            'total': total_referrals,
            'active': active_referrals,
            'totalEarned': total_earned
        }
    })

@app.route('/api/user/update', methods=['PUT'])
@token_required
def update_profile(user):
    data = request.json
    users = load_users()
    u = find_user_by_id(users, user['id'])
    if not u:
        return jsonify({'error': 'User not found'}), 404

    if 'name' in data:
        u['name'] = data['name']
    if 'password' in data:
        u['password'] = hash_password(data['password'])

    save_users(users)
    return jsonify({'message': 'Profile updated'})

# ============================================================
# REFERRAL SYSTEM
# ============================================================
@app.route('/api/referrals', methods=['GET'])
@token_required
def get_referrals(user):
    referrals = load_referrals()
    my_referrals = [r for r in referrals if r.get('referrerId') == user['id']]
    
    # Get full user details for each referral
    users = load_users()
    for r in my_referrals:
        referred_user = find_user_by_id(users, r.get('referredId'))
        if referred_user:
            r['referredBalance'] = referred_user.get('balance', 0)
            r['referredTotalDeposits'] = referred_user.get('totalDeposits', 0)
    
    return jsonify(my_referrals)

@app.route('/api/referrals/stats', methods=['GET'])
@token_required
def get_referral_stats(user):
    referrals = load_referrals()
    my_referrals = [r for r in referrals if r.get('referrerId') == user['id']]
    
    total = len(my_referrals)
    active = len([r for r in my_referrals if r.get('status') == 'active'])
    completed = len([r for r in my_referrals if r.get('status') == 'completed'])
    total_earned = sum([r.get('bonusEarned', 0) for r in my_referrals])
    total_deposits = sum([r.get('depositAmount', 0) for r in my_referrals])
    
    return jsonify({
        'total': total,
        'active': active,
        'completed': completed,
        'totalEarned': total_earned,
        'totalDeposits': total_deposits
    })

# ============================================================
# TAP - 5% Reward
# ============================================================
@app.route('/api/tap', methods=['POST'])
@token_required
def tap(user):
    COOLDOWN = 24 * 60 * 60 * 1000  # 24 hours in milliseconds
    
    now = datetime.now().timestamp() * 1000
    last = user.get('lastTapTime')
    
    if last:
        last_time = datetime.fromisoformat(last).timestamp() * 1000
        if now - last_time < COOLDOWN:
            remaining = (COOLDOWN - (now - last_time)) / 1000
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            return jsonify({
                'error': f'Wait {hours}h {minutes}m',
                'cooldown': True,
                'remaining': remaining
            }), 429

    # 5% reward
    reward = max(user['balance'] * 0.05, 0.01)
    user['balance'] += reward
    user['lastTapTime'] = datetime.now().isoformat()
    user['tapHistory'] = user.get('tapHistory', []) + [datetime.now().isoformat()]
    user['activities'] = user.get('activities', []) + [f'Tapped earned ₦{reward:.2f}']

    users = load_users()
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i] = user
            break
    save_users(users)

    return jsonify({
        'message': f'Earned ₦{reward:.2f}',
        'reward': reward,
        'newBalance': user['balance']
    })

# ============================================================
# VIP UPGRADE
# ============================================================
@app.route('/api/vip/upgrade', methods=['POST'])
@token_required
def upgrade_vip(user):
    data = request.json
    level = data.get('level')
    
    prices = {1: 20000, 2: 50000, 3: 150000, 4: 500000, 5: 1000000}
    
    if level not in prices:
        return jsonify({'error': 'Invalid level'}), 400
    
    price = prices[level]
    if user['balance'] < price:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user['balance'] -= price
    user['vipLevel'] = level
    user['vipSince'] = datetime.now().isoformat()
    user['activities'] = user.get('activities', []) + [f'Upgraded to VIP {level} for ₦{price:.2f}']
    
    users = load_users()
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i] = user
            break
    save_users(users)

    return jsonify({
        'message': f'Upgraded to VIP {level}',
        'newBalance': user['balance'],
        'vipLevel': level
    })

# ============================================================
# DEPOSIT
# ============================================================
@app.route('/api/deposit/start', methods=['POST'])
@token_required
def start_deposit(user):
    data = request.json
    amount = data.get('amount')
    
    if not amount or amount < 100:
        return jsonify({'error': 'Min ₦100'}), 400
    
    pending = load_pending()
    deposit_id = secrets.token_hex(8)
    pending.append({
        'id': deposit_id,
        'userId': user['id'],
        'amount': amount,
        'startTime': datetime.now().isoformat(),
        'confirmed': False
    })
    save_pending(pending)
    
    return jsonify({
        'message': 'Deposit started',
        'depositId': deposit_id
    })

@app.route('/api/deposit/confirm', methods=['POST'])
@token_required
def confirm_deposit(user):
    data = request.json
    deposit_id = data.get('depositId')
    
    pending = load_pending()
    deposit = None
    for d in pending:
        if d.get('id') == deposit_id and d.get('userId') == user['id'] and not d.get('confirmed'):
            deposit = d
            break
    
    if not deposit:
        return jsonify({'error': 'Pending deposit not found'}), 404
    
    amount = deposit['amount']
    deposit['confirmed'] = True
    save_pending(pending)
    
    # Update user balance
    user['balance'] += amount
    user['totalDeposits'] += amount
    user['deposits'] = user.get('deposits', []) + [{
        'amount': amount,
        'status': 'Completed',
        'date': datetime.now().isoformat()
    }]
    user['activities'] = user.get('activities', []) + [f'Deposited ₦{amount:.2f}']
    
    users = load_users()
    
    # ============================================================
    # REFERRAL BONUS - 20% of deposit
    # ============================================================
    if user.get('referredBy'):
        referrer = find_user_by_ref(users, user['referredBy'])
        if referrer:
            bonus = amount * 0.2  # 20% bonus
            referrer['balance'] += bonus
            referrer['activities'] = referrer.get('activities', []) + [
                f'Earned ₦{bonus:.2f} referral bonus from {user["name"]} deposit of ₦{amount:.2f}'
            ]
            
            # Update referral record
            referrals = load_referrals()
            for r in referrals:
                if r.get('referredId') == user['id'] and r.get('referrerId') == referrer['id']:
                    r['status'] = 'active'
                    r['depositAmount'] = amount
                    r['bonusEarned'] = bonus
                    r['updatedAt'] = datetime.now().isoformat()
                    break
            save_referrals(referrals)
            
            # Save referrer updates
            for i, u in enumerate(users):
                if u['id'] == referrer['id']:
                    users[i] = referrer
                    break
    
    # Save user updates
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i] = user
            break
    save_users(users)
    
    return jsonify({
        'message': 'Deposit confirmed',
        'newBalance': user['balance']
    })

# ============================================================
# WITHDRAW
# ============================================================
@app.route('/api/withdraw', methods=['POST'])
@token_required
def withdraw(user):
    # Check if Friday
    if datetime.now().strftime('%A') != 'Friday':
        return jsonify({'error': 'Withdrawals only on Fridays'}), 400
    
    data = request.json
    amount = data.get('amount')
    bank = data.get('bank')
    acct_name = data.get('acctName')
    acct_num = data.get('acctNum')
    
    if not all([amount, bank, acct_name, acct_num]):
        return jsonify({'error': 'Missing fields'}), 400
    
    if user['balance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user['balance'] -= amount
    user['totalWithdrawals'] += amount
    user['withdrawals'] = user.get('withdrawals', []) + [{
        'amount': amount,
        'bank': bank,
        'acctName': acct_name,
        'acctNum': acct_num,
        'status': 'Pending',
        'date': datetime.now().isoformat()
    }]
    user['activities'] = user.get('activities', []) + [f'Withdrawal request of ₦{amount:.2f} to {bank}']
    
    users = load_users()
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i] = user
            break
    save_users(users)
    
    return jsonify({
        'message': 'Withdrawal requested',
        'newBalance': user['balance']
    })

# ============================================================
# LEADERBOARD
# ============================================================
@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    users = load_users()
    sorted_users = sorted(users, key=lambda x: x.get('balance', 0), reverse=True)[:10]
    
    # Add referral counts
    referrals = load_referrals()
    result = []
    for u in sorted_users:
        user_refs = [r for r in referrals if r.get('referrerId') == u['id']]
        result.append({
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'balance': u['balance'],
            'vipLevel': u['vipLevel'],
            'referredBy': u.get('referredBy'),
            'totalDeposits': u.get('totalDeposits', 0),
            'totalReferrals': len(user_refs),
            'refCode': u.get('refCode')
        })
    return jsonify(result)

# ============================================================
# VIP TIERS
# ============================================================
@app.route('/api/vip/tiers', methods=['GET'])
def vip_tiers():
    return jsonify([
        {'level': 0, 'name': 'VIP 0', 'price': 0},
        {'level': 1, 'name': 'VIP 1', 'price': 20000},
        {'level': 2, 'name': 'VIP 2', 'price': 50000},
        {'level': 3, 'name': 'VIP 3', 'price': 150000},
        {'level': 4, 'name': 'VIP 4', 'price': 500000},
        {'level': 5, 'name': 'VIP 5', 'price': 1000000}
    ])

# ============================================================
# ACTIVITY LOG
# ============================================================
@app.route('/api/activity', methods=['GET'])
def get_activity():
    users = load_users()
    all_activities = []
    for u in users:
        for act in u.get('activities', [])[-5:]:
            all_activities.append({
                'user': u['name'],
                'action': act,
                'timestamp': datetime.now().isoformat()
            })
    # Sort by timestamp (newest first) and limit
    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(all_activities[:20])

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    users = load_users()
    referrals = load_referrals()
    pending = load_pending()
    
    print('\n' + '='*50)
    print('🚀 CREDIT ZONE Backend')
    print('='*50)
    print(f'📁 Data folder: data/')
    print(f'👥 Users: {len(users)}')
    print(f'🔗 Total Referrals: {len(referrals)}')
    print(f'💳 Pending deposits: {len(pending)}')
    print('='*50)
    print('🌐 Server: http://localhost:5000')
    print('📱 Frontend: http://localhost:5000/static/index.html')
    print('='*50)
    print('💡 Tap Reward: 5% of balance (24h cooldown)')
    print('🔗 Referral Bonus: 20% of referral\'s deposit')
    print('='*50 + '\n')
    app.run(host='0.0.0.0', port=5000, debug=True)
