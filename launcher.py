#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 IFC Query System Launcher
מערכת הפעלה מתקדמת עם לוגים
"""

import subprocess
import sys
import time
import os
from datetime import datetime

def check_dependencies():
    """בדיקת תלויות"""
    print("🔍 בודק תלויות...")
    
    required_packages = [
        'streamlit', 'duckdb', 'pandas', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - חסר")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 מתקין חבילות חסרות: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    print("✅ כל התלויות זמינות!\n")

def setup_logging_system():
    """הכנת מערכת לוגים"""
    print("📊 מכין מערכת לוגים...")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Test logging system
    print("🧪 בודק מערכת לוגים...")
    
    try:
        from query_logger import log_user_question, query_logger
        
        # Test log
        log_user_question(
            user_question="בדיקת מערכת לוגים",
            query_type="system_test",
            success=True,
            ai_translation_used=False
        )
        
        print("   ✅ מערכת לוגים פועלת")
        
        # Show today's stats
        today = datetime.now().strftime('%Y-%m-%d')
        stats = query_logger.get_daily_stats(today)
        print(f"   📈 שאלות היום: {stats.get('total_queries', 0)}")
        
    except Exception as e:
        print(f"   ❌ שגיאה במערכת לוגים: {e}")
    
    print("✅ מערכת לוגים מוכנה!\n")

def start_main_app():
    """הפעלת האפליקציה הראשית"""
    print("🚀 מפעיל את האפליקציה הראשית...")
    print("🌐 יפתח בכתובת: http://localhost:8502")
    print("📊 טאב Analytics זמין בממשק!")
    print("\n" + "="*50)
    
    try:
        subprocess.run([
            "streamlit", "run", "app.py", 
            "--server.port", "8502",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 נעצר על ידי המשתמש")
    except Exception as e:
        print(f"❌ שגיאה בהפעלת האפליקציה: {e}")

def start_analytics_dashboard():
    """הפעלת דשבורד Analytics נפרד"""
    print("📊 מפעיל דשבורד Analytics...")
    print("🌐 יפתח בכתובת: http://localhost:8503")
    print("\n" + "="*50)
    
    try:
        subprocess.run([
            "streamlit", "run", "analytics_dashboard.py",
            "--server.port", "8503", 
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 נעצר על ידי המשתמש")
    except Exception as e:
        print(f"❌ שגיאה בהפעלת דשבורד: {e}")

def run_demo():
    """הרצת דמו לוגים"""
    print("🎬 מריץ דמו מערכת לוגים...")
    
    try:
        subprocess.run([sys.executable, "test_logger.py"])
    except Exception as e:
        print(f"❌ שגיאה בהרצת דמו: {e}")

def main():
    """תפריט ראשי"""
    
    print("🏗️ מערכת ניתוח נתוני IFC עם לוגים מתקדמים")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initial setup
    check_dependencies()
    setup_logging_system()
    
    while True:
        print("🎯 מה ברצונך לעשות?")
        print("1. 🚀 הפעל את האפליקציה הראשית (עם Analytics)")
        print("2. 📊 הפעל דשבורד Analytics נפרד")
        print("3. 🎬 הרץ דמו מערכת לוגים") 
        print("4. 🔍 צפה בלוגים")
        print("5. 📈 הצג סטטיסטיקות")
        print("6. 🚪 יציאה")
        print()
        
        choice = input("👆 בחר אפשרות (1-6): ").strip()
        
        if choice == "1":
            start_main_app()
            
        elif choice == "2":
            start_analytics_dashboard()
            
        elif choice == "3":
            run_demo()
            input("\n⏸️  לחץ Enter להמשך...")
            
        elif choice == "4":
            # Show recent logs
            print("\n📋 לוגים אחרונים:")
            print("-" * 40)
            
            try:
                from query_logger import query_logger
                today = datetime.now().strftime('%Y-%m-%d')
                queries = query_logger.load_queries_by_date(today)
                
                if queries:
                    for query in queries[-5:]:  # Last 5
                        timestamp = query.get('timestamp', '')[:19]
                        question = query.get('user_question', '')[:50]
                        status = "✅" if query.get('success') else "❌"
                        print(f"{timestamp} {status} {question}...")
                else:
                    print("📝 אין לוגים להיום")
                    
            except Exception as e:
                print(f"❌ שגיאה בקריאת לוגים: {e}")
                
            input("\n⏸️  לחץ Enter להמשך...")
            
        elif choice == "5":
            # Show stats
            print("\n📊 סטטיסטיקות:")
            print("-" * 40)
            
            try:
                from query_logger import query_logger
                report = query_logger.generate_analytics_report(7)
                print(report)
                
            except Exception as e:
                print(f"❌ שגיאה בהצגת סטטיסטיקות: {e}")
                
            input("\n⏸️  לחץ Enter להמשך...")
            
        elif choice == "6":
            print("👋 להתראות!")
            break
            
        else:
            print("❌ בחירה לא תקינה. נסה שוב.\n")

if __name__ == "__main__":
    main()