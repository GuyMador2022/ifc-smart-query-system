#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Query Logger Demo & Test
הדגמה ובדיקת מערכת הלוגים
"""

import time
from query_logger import log_user_question, query_logger

def demo_logging():
    """דמו של רישום שאלות"""
    
    print("🔍 מתחיל דמו מערכת לוגים...")
    print("=" * 50)
    
    # Sample questions from different professions
    demo_queries = [
        {
            "user_question": "כמה קירות יש בפרויקט?",
            "profession": "👷‍♀️ אדריכל", 
            "category": "🧱 אלמנטי בנייה",
            "query_type": "predefined",
            "sql_query": "SELECT COUNT(*) FROM wall_table",
            "success": True,
            "result_rows": 1,
            "execution_time_ms": 45.2,
            "ai_translation_used": False
        },
        {
            "user_question": "מה מידות הקורות הראשיות?",
            "profession": "🔧 מהנדס",
            "category": "🏗️ מבנה",
            "query_type": "ai_translation", 
            "sql_query": "SELECT width, height, length FROM beams WHERE type='main'",
            "success": True,
            "result_rows": 12,
            "execution_time_ms": 78.5,
            "ai_translation_used": True
        },
        {
            "user_question": "מה המחיר הכולל של הפרויקט?",
            "profession": "💼 בעל פרויקט",
            "category": "💰 עלויות",
            "query_type": "free_chat",
            "sql_query": "SELECT SUM(cost) FROM project_costs",
            "success": True,
            "result_rows": 1,
            "execution_time_ms": 23.8,
            "ai_translation_used": True
        },
        {
            "user_question": "How many windows are there?",
            "profession": None,
            "category": None,
            "query_type": "free_chat",
            "sql_query": None,
            "success": False,
            "result_rows": None,
            "execution_time_ms": 12.3,
            "error_message": "AI translation failed",
            "ai_translation_used": True
        },
        {
            "user_question": "SELECT * FROM invalid_table",
            "profession": None,
            "category": None, 
            "query_type": "manual_sql",
            "sql_query": "SELECT * FROM invalid_table",
            "success": False,
            "result_rows": None,
            "execution_time_ms": 156.7,
            "error_message": "Table 'invalid_table' doesn't exist",
            "ai_translation_used": False
        }
    ]
    
    # Log sample queries
    for i, query_data in enumerate(demo_queries, 1):
        print(f"📝 רושם שאלה {i}/5: {query_data['user_question'][:40]}...")
        
        log_user_question(**query_data)
        
        # Small delay to show different timestamps
        time.sleep(0.1)
        
    print("\n✅ נרשמו כל השאלות הדמו!")
    print("=" * 50)
    
    # Show analytics
    print("\n📊 הצגת Analytics:")
    report = query_logger.generate_analytics_report(1)
    print(report)
    
    # Show files created
    print("\n📁 קבצים שנוצרו:")
    import os
    log_dir = "logs"
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   📄 {file} ({file_size} bytes)")
    
    print("\n🎯 מערכת הלוגים פועלת בהצלחה!")

if __name__ == "__main__":
    demo_logging()