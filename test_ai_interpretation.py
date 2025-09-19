#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AI Results Interpretation Test
בדיקת פרשנות תוצאות חכמה
"""

import pandas as pd
from ai_translator import IFCQueryTranslator

def test_ai_interpretation():
    """בדיקת פרשנות AI"""
    
    print("🧠 בודק פרשנות AI לתוצאות...")
    print("=" * 50)
    
    try:
        # Initialize translator
        translator = IFCQueryTranslator('guy_mador_shiba.duckdb')
        print("✅ מתרגם AI מאותחל")
        
        # Test cases - create sample results
        test_cases = [
            {
                "question": "כמה קירות יש בבניין?",
                "sql": "SELECT COUNT(*) as wall_count FROM ifcwall",
                "results": pd.DataFrame({"wall_count": [45]})
            },
            {
                "question": "מה השטח הכולל של החללים?",
                "sql": "SELECT SUM(area) as total_area FROM ifcspace",
                "results": pd.DataFrame({"total_area": [1250.75]})
            },
            {
                "question": "רשימת החומרים בפרויקט",
                "sql": "SELECT name FROM ifcmaterial LIMIT 5",
                "results": pd.DataFrame({
                    "name": ["בטון", "פלדה", "עץ אורן", "זכוכית", "אלומיניום"]
                })
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 בדיקה {i}: {test_case['question']}")
            print("-" * 40)
            
            try:
                interpretation = translator.interpret_results(
                    test_case["question"],
                    test_case["sql"], 
                    test_case["results"],
                    True
                )
                
                print("🤖 פרשנות AI:")
                print(interpretation)
                print("✅ הצלחה!")
                
            except Exception as e:
                print(f"❌ שגיאה בפרשנות: {e}")
        
        print(f"\n{'='*50}")
        print("🎯 בדיקת פרשנות AI הושלמה!")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")

if __name__ == "__main__":
    test_ai_interpretation()