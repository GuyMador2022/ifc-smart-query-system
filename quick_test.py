#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Quick Test - בדיקה מהירה של מערכת השאלות
בדיקה מדגם של שאלות מכל קטגוריה
"""

import os
import sys
from pathlib import Path

# הוספת הנתיב של המודול
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from ai_translator import IFCQueryTranslator
except ImportError as e:
    print(f"❌ שגיאה בטעינת המודול ai_translator: {e}")
    sys.exit(1)

def quick_test():
    """בדיקה מהירה של מדגם שאלות"""
    print("🚀 בדיקה מהירה - מדגם שאלות מכל מקצוע")
    print("=" * 50)
    
    # שאלות לבדיקה מהירה
    sample_questions = [
        ("🏗️ אדריכל", "כמה קירות יש בפרויקט?"),
        ("🔧 מהנדס", "כמה קורות יש בפרויקט?"),
        ("💼 בעל פרויקט", "מה אחוז השלמה הכולל?"),
        ("🚪 אלמנטים", "כמה דלתות יש בפרויקט?"),
        ("🏠 חללים", "כמה חדרים יש בפרויקט?")
    ]
    
    # אתחול המתרגם
    try:
        translator = IFCQueryTranslator("guy_mador_shiba.duckdb")
        print("✅ מחובר למסד הנתונים")
    except Exception as e:
        print(f"❌ שגיאה בחיבור למסד הנתונים: {e}")
        return False
    
    success_count = 0
    total_count = len(sample_questions)
    
    print(f"\n🔍 בודק {total_count} שאלות מדגם:")
    print("-" * 50)
    
    for category, question in sample_questions:
        try:
            result = translator.translate_query(question)
            sql_query = result.get('sql_query', '') if isinstance(result, dict) else ''
            
            if sql_query and sql_query.strip():
                print(f"✅ {category}: {question}")
                print(f"   📝 SQL: {sql_query[:60]}...")
                success_count += 1
            else:
                print(f"❌ {category}: {question}")
                print(f"   📝 תרגום נכשל")
        except Exception as e:
            print(f"❌ {category}: {question}")
            print(f"   📝 שגיאה: {e}")
    
    print("\n" + "=" * 50)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"📊 תוצאות: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 הבדיקה המהירה עברה בהצלחה!")
        print("💡 המערכת מוכנה לשימוש")
    else:
        print("⚠️ יש בעיות במערכת")
        print("🔧 מומלץ להריץ בדיקה מלאה עם: python test_all_questions.py")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)