#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת דפוסי הזיהוי החדשים למהנדסים במתרגם AI
"""

from ai_translator import IFCQueryTranslator

def test_engineer_patterns():
    """בדיקת דפוסי זיהוי חדשים למהנדסים"""
    translator = IFCQueryTranslator('guy_mador_shiba.duckdb')
    
    engineer_questions = [
        # קונסטרוקציה
        "כמה עמודים נושאים יש?",
        "מה מידות הקורות?",
        "מה עובי התקרות?",
        "מה קוטר העמודים?",
        
        # מערכות
        "איזה מערכות HVAC יש?",
        "איזה לוחות חשמל יש?",
        "כמה נקודות מים יש?",
        "איזה מערכות מיזוג יש?",
        
        # חומרים וכמויות
        "כמה טון בטון נדרש?",
        "איזה אלמנטי פלדה יש?",
        "נפח בטון",
        "טון ברזל",
        
        # אנגלית
        "How many structural columns?",
        "What are the beam dimensions?",
        "Show me HVAC systems",
        "Concrete volume",
        "Steel elements"
    ]
    
    print("🔧 בדיקת דפוסי זיהוי חדשים למהנדסים:")
    print("=" * 60)
    
    successful = 0
    total = len(engineer_questions)
    
    for question in engineer_questions:
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
    
    print("=" * 60)
    print(f"📈 סיכום: {successful}/{total} שאלות זוהו בהצלחה ({successful/total*100:.1f}%)")
    
    if successful >= total * 0.8:
        print("🎉 מצוין! רוב השאלות זוהו בהצלחה")
    elif successful >= total * 0.6:
        print("👍 טוב! יש מקום לשיפור")
    else:
        print("⚠️ יש צורך בתיקונים נוספים")

if __name__ == "__main__":
    test_engineer_patterns()