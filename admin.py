#!/usr/bin/env python3
"""
CREDIT ZONE Admin Dashboard
View all users, deposits, withdrawals, and referrals
"""

import json
import os
from datetime import datetime

def load_data():
    """Load all data from JSON files"""
    with open('data/users.json', 'r') as f:
        users = json.load(f)
    
    with open('data/referrals.json', 'r') as f:
        referrals = json.load(f)
    
    with open('data/pending.json', 'r') as f:
        pending = json.load(f)
    
    return users, referrals, pending

def show_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("🏦 CREDIT ZONE ADMIN")
    print("="*50)
    print("1. View All Users")
    print("2. View All Deposits")
    print("3. View All Withdrawals")
    print("4. View Referral System")
    print("5. View User Details")
    print("6. View Statistics")
    print("7. Check Pending Deposits")
    print("8. Exit")
    print("="*50)

def view_all_users(users, referrals):
    """Display all users with their info"""
    print("\n👥 ALL USERS")
    print("-"*60)
    
    if not users:
        print("No users registered yet.")
        return
    
    for u in users:
        refs = [r for r in referrals if r.get('referrerId') == u['id']]
        print(f"\n📧 {u['email']}")
        print(f"   Name: {u['name']}")
        print(f"   Referral Code: {u['refCode']}")
        print(f"   Balance: ₦{u.get('balance', 0):.2f}")
        print(f"   VIP Level: {u.get('vipLevel', 0)}")
        print(f"   Referrals: {len(refs)}")
        print(f"   Total Deposits: ₦{u.get('totalDeposits', 0):.2f}")
        print(f"   Total Withdrawals: ₦{u.get('totalWithdrawals', 0):.2f}")

def view_all_deposits(users):
    """Display all deposits from all users"""
    print("\n💰 ALL DEPOSITS")
    print("-"*60)
    
    all_deposits = []
    for u in users:
        deposits = u.get('deposits', [])
        for d in deposits:
            all_deposits.append({
                'user': u['name'],
                'email': u['email'],
                'amount': d.get('amount', 0),
                'status': d.get('status', 'N/A'),
                'date': d.get('date', 'N/A')
            })
    
    if not all_deposits:
        print("No deposits yet.")
        return
    
    # Sort by date (newest first)
    all_deposits.sort(key=lambda x: x['date'], reverse=True)
    
    for d in all_deposits[:20]:  # Show last 20
        print(f"\n👤 {d['user']} ({d['email']})")
        print(f"   ₦{d['amount']:.2f} - {d['status']}")
        print(f"   Date: {d['date'][:19] if d['date'] != 'N/A' else 'N/A'}")

def view_all_withdrawals(users):
    """Display all withdrawals from all users"""
    print("\n💳 ALL WITHDRAWALS")
    print("-"*60)
    
    all_withdrawals = []
    for u in users:
        withdrawals = u.get('withdrawals', [])
        for w in withdrawals:
            all_withdrawals.append({
                'user': u['name'],
                'email': u['email'],
                'amount': w.get('amount', 0),
                'status': w.get('status', 'N/A'),
                'bank': w.get('bank', 'N/A'),
                'acctName': w.get('acctName', 'N/A'),
                'date': w.get('date', 'N/A')
            })
    
    if not all_withdrawals:
        print("No withdrawals yet.")
        return
    
    # Sort by date (newest first)
    all_withdrawals.sort(key=lambda x: x['date'], reverse=True)
    
    for w in all_withdrawals[:20]:  # Show last 20
        print(f"\n👤 {w['user']} ({w['email']})")
        print(f"   ₦{w['amount']:.2f} - {w['status']}")
        print(f"   Bank: {w['bank']} - Account: {w['acctName']}")
        print(f"   Date: {w['date'][:19] if w['date'] != 'N/A' else 'N/A'}")

def view_referral_system(referrals, users):
    """Display all referral relationships"""
    print("\n🔗 REFERRAL SYSTEM")
    print("-"*60)
    
    if not referrals:
        print("No referrals yet.")
        return
    
    for r in referrals:
        print(f"\n{r.get('referrerName', 'N/A')} → {r.get('referredName', 'N/A')}")
        print(f"   Status: {r.get('status', 'N/A')}")
        print(f"   Deposit Amount: ₦{r.get('depositAmount', 0):.2f}")
        print(f"   Bonus Earned: ₦{r.get('bonusEarned', 0):.2f}")
        print(f"   Date: {r.get('createdAt', 'N/A')[:19] if r.get('createdAt') else 'N/A'}")

def view_user_details(users, referrals):
    """Show detailed info for a specific user"""
    email = input("\nEnter user email: ")
    user = None
    for u in users:
        if u['email'] == email:
            user = u
            break
    
    if not user:
        print("❌ User not found!")
        return
    
    print(f"\n👤 USER DETAILS: {user['name']}")
    print("-"*60)
    print(f"Email: {user['email']}")
    print(f"Referral Code: {user.get('refCode', 'N/A')}")
    print(f"Referred By: {user.get('referredBy', 'None')}")
    print(f"VIP Level: {user.get('vipLevel', 0)}")
    print(f"Balance: ₦{user.get('balance', 0):.2f}")
    print(f"Total Deposits: ₦{user.get('totalDeposits', 0):.2f}")
    print(f"Total Withdrawals: ₦{user.get('totalWithdrawals', 0):.2f}")
    
    # Get their referrals
    user_refs = [r for r in referrals if r.get('referrerId') == user['id']]
    print(f"\n📋 Their Referrals: {len(user_refs)}")
    for r in user_refs:
        print(f"   → {r.get('referredName', 'N/A')} (Status: {r.get('status', 'N/A')})")
    
    # Show deposit history
    deposits = user.get('deposits', [])
    if deposits:
        print(f"\n📥 Deposit History ({len(deposits)}):")
        for d in deposits[-5:]:  # Last 5
            print(f"   ₦{d['amount']:.2f} - {d.get('status', 'N/A')} - {d.get('date', 'N/A')[:10]}")
    
    # Show withdrawal history
    withdrawals = user.get('withdrawals', [])
    if withdrawals:
        print(f"\n📤 Withdrawal History ({len(withdrawals)}):")
        for w in withdrawals[-5:]:  # Last 5
            print(f"   ₦{w['amount']:.2f} - {w.get('status', 'N/A')} - {w.get('bank', 'N/A')}")

def view_statistics(users, referrals, pending):
    """Display overall statistics"""
    print("\n📊 STATISTICS")
    print("-"*60)
    
    total_balance = sum(u.get('balance', 0) for u in users)
    total_deposits = sum(u.get('totalDeposits', 0) for u in users)
    total_withdrawals = sum(u.get('totalWithdrawals', 0) for u in users)
    total_referrals = len(referrals)
    
    print(f"Total Users: {len(users)}")
    print(f"Total Referrals: {total_referrals}")
    print(f"Total Balance Across All Users: ₦{total_balance:.2f}")
    print(f"Total Deposits: ₦{total_deposits:.2f}")
    print(f"Total Withdrawals: ₦{total_withdrawals:.2f}")
    
    # Pending deposits
    pending_deposits = [p for p in pending if not p.get('confirmed')]
    print(f"Pending Deposits: {len(pending_deposits)}")
    
    # VIP distribution
    vip_counts = {}
    for u in users:
        level = u.get('vipLevel', 0)
        vip_counts[level] = vip_counts.get(level, 0) + 1
    
    print(f"\nVIP Distribution:")
    for level, count in sorted(vip_counts.items()):
        print(f"   VIP {level}: {count} users")
    
    # Active referrals
    active_refs = [r for r in referrals if r.get('status') == 'active']
    total_bonus = sum(r.get('bonusEarned', 0) for r in referrals)
    print(f"\nReferral Bonuses Paid: ₦{total_bonus:.2f}")
    print(f"Active Referrals: {len(active_refs)}")

def check_pending_deposits(users, pending):
    """Show pending deposits that need verification"""
    print("\n⏳ PENDING DEPOSITS")
    print("-"*60)
    
    pending_deposits = [p for p in pending if not p.get('confirmed')]
    
    if not pending_deposits:
        print("No pending deposits to verify.")
        return
    
    for p in pending_deposits:
        # Find the user
        user = None
        for u in users:
            if u['id'] == p.get('userId'):
                user = u
                break
        
        if user:
            print(f"\n👤 User: {user['name']} ({user['email']})")
        else:
            print(f"\n👤 User ID: {p.get('userId')}")
        
        print(f"   Amount: ₦{p.get('amount', 0):.2f}")
        print(f"   Started: {p.get('startTime', 'N/A')}")
        
        # Ask to verify
        verify = input("\n   Has this user sent the money? (y/n/q to quit): ").lower()
        if verify == 'y':
            # Confirm the deposit
            p['confirmed'] = True
            if user:
                user['balance'] += p.get('amount', 0)
                user['totalDeposits'] += p.get('amount', 0)
                user['deposits'] = user.get('deposits', []) + [{
                    'amount': p.get('amount', 0),
                    'status': 'Completed',
                    'date': datetime.now().isoformat()
                }]
                print(f"   ✅ Deposit confirmed! Added ₦{p['amount']:.2f} to {user['name']}")
                
                # Save changes
                with open('data/users.json', 'w') as f:
                    json.dump(users, f, indent=2)
                with open('data/pending.json', 'w') as f:
                    json.dump(pending, f, indent=2)
        elif verify == 'q':
            break
        else:
            print("   ⏳ Deposit still pending")

def main():
    """Main program loop"""
    while True:
        users, referrals, pending = load_data()
        show_menu()
        
        try:
            choice = input("\nSelect option (1-8): ")
            
            if choice == '1':
                view_all_users(users, referrals)
            elif choice == '2':
                view_all_deposits(users)
            elif choice == '3':
                view_all_withdrawals(users)
            elif choice == '4':
                view_referral_system(referrals, users)
            elif choice == '5':
                view_user_details(users, referrals)
            elif choice == '6':
                view_statistics(users, referrals, pending)
            elif choice == '7':
                check_pending_deposits(users, pending)
            elif choice == '8':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 1-8.")
            
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
