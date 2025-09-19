#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת דפוסי הזיהוי החדשים במתרגם AI
"""

from ai_translator import IFCQueryTranslator

def test_patterns():
    """בדיקת דפוסי זיהוי חדשים"""
    translator = IFCQueryTranslator('guy_mador_shiba.duckdb')
    
    test_questions = [
        "כמה קירות יש בבניין?",
        "מה גובה הבניין?", 
        "כמה קומות יש?",
        "איזה סוגי דלתות יש?",
        "מה החדר הגדול ביותר?",
        "תן לי סיכום כללי",
        "איזה חומרים בשימוש?",
        "מה הנפח הכולל?",
        "How many walls?",
        "What materials are used?",
        "Building summary"
    ]
    
    print("🔍 בדיקת דפוסי זיהוי חדשים:")
    print("=" * 50)
    
    for question in test_questions:
        result = translator._preprocess_common_patterns(question)
        if result:
            print(f"✅ {question}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   SQL Preview: {result['sql_query'][:80]}...")
            print()
        else:
            print(f"❌ {question} - לא זוהה דפוס")
            print()

if __name__ == "__main__":
    test_patterns()