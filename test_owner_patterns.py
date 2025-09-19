#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת דפוסי הזיהוי החדשים לבעלי פרויקט במתרגם AI
"""

from ai_translator import IFCQueryTranslator

def test_owner_patterns():
    """בדיקת דפוסי זיהוי חדשים לבעלי פרויקט"""
    translator = IFCQueryTranslator('guy_mador_shiba.duckdb')
    
    owner_questions = [
        # עלויות ותקציב
        "כמה עולה הפרויקט?",
        "מה העלות למטר רבוע?",
        "מחיר למטר רבוע",
        
        # התקדמות ולוחות זמנים
        "מה אחוז השלמה?",
        "איזה שלב בניה עכשיו?",
        "מתי הפרויקט יסתיים?",
        
        # סיכומים וניהול
        "מה גודל הפרויקט?",
        "סיכום פרויקט",
        "איזה בעיות איכות יש?",
        
        # אנגלית
        "Project completion percentage",
        "What is the project cost?", 
        "Current construction phase",
        "Project size summary",
        "Cost per square meter",
        "Quality issues",
        "Project timeline"
    ]
    
    print("💼 בדיקת דפוסי זיהוי חדשים לבעלי פרויקט:")
    print("=" * 65)
    
    successful = 0
    total = len(owner_questions)
    
    for question in owner_questions:
        result = translator._preprocess_common_patterns(question)
        if result:
            print(f"✅ {question}")
            print(f"   📊 Confidence: {result['confidence']}")
            print(f"   🔍 SQL Preview: {result['sql_query'][:80]}...")
            print(f"   📝 Explanation: {result['explanation']}")
            print()
            successful += 1
        else:
            print(f"❌ {question} - לא זוהה דפוס")
            print()
    
    print("=" * 65)
    print(f"📈 סיכום: {successful}/{total} שאלות זוהו בהצלחה ({successful/total*100:.1f}%)")
    
    if successful >= total * 0.8:
        print("🎉 מצוין! רוב השאלות זוהו בהצלחה")
    elif successful >= total * 0.6:
        print("👍 טוב! יש מקום לשיפור")
    else:
        print("⚠️ יש צורך בתיקונים נוספים")
    
    print("\n🔍 הערות לבעלי פרויקט:")
    print("• שאלות עלות - הערכות גסות בלבד, יש לוודא עם קבלן")
    print("• אחוז השלמה - מבוסס על מודל IFC, לא על מצב שטח בפועל")
    print("• איכות ולוחות זמנים - דורשים מעקב במערכות ניהול פרויקט")

if __name__ == "__main__":
    test_owner_patterns()