#!/usr/bin/env python3
"""Quick test of login credentials"""
from app.services.telegram_auth import telegram_auth

print("\n" + "=" * 60)
print("🔐 TELEGRAM BOT LOGIN CREDENTIALS TEST")
print("=" * 60)

print(f"\n✅ Credentials loaded from file")
print(f"\n📝 Login Credentials:")
print(f"   Login ID: {telegram_auth.login_id}")
print(f"   Password: {telegram_auth.login_password}")

# Test login
test_user_id = 123456
result = telegram_auth.verify_login(test_user_id, "apex", "apexbeta")

print(f"\n🧪 Test Result: {'✅ SUCCESS' if result else '❌ FAILED'}")

if result:
    telegram_auth.logout_user(test_user_id)  # Cleanup
    print("\n" + "=" * 60)
    print("✅ LOGIN WORKING CORRECTLY!")
    print("=" * 60)
    print("\n💡 In Telegram bot:")
    print("   1. Send: /start")
    print("   2. Send: /login")
    print("   3. Enter ID: apex")
    print("   4. Enter Password: apexbeta")
    print("\n✅ You should be logged in successfully!\n")
else:
    print("\n❌ Login test failed - credentials not matching")
