#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Script לבדיקת כל השאלות במערכת IFC-2-DuckDB
מעבר על כל השאלות מכל הקטגוריות והמקצועות
"""

import os
import sys
import glob
import time
from typing import List, Dict, Tuple
from pathlib import Path
import json

# הוספת הנתיב של המודול
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from ai_translator import IFCQueryTranslator
except ImportError as e:
    print(f"❌ שגיאה בטעינת המודול ai_translator: {e}")
    sys.exit(1)

class QuestionTester:
    """כלי לבדיקת שאלות במערכת"""
    
    def __init__(self, db_path: str = "guy_mador_shiba.duckdb"):
        """אתחול הבודק"""
        self.db_path = db_path
        self.translator = None
        self.results = {
            'total_questions': 0,
            'successful_answers': 0,
            'failed_answers': 0,
            'categories': {},
            'details': []
        }
        
    def initialize_translator(self) -> bool:
        """אתחול מתרגם השאלות"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ קובץ מסד הנתונים לא נמצא: {self.db_path}")
                return False
                
            self.translator = IFCQueryTranslator(self.db_path)
            print(f"✅ מתרגם האי מחובר למסד הנתונים: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ שגיאה באתחול המתרגם: {e}")
            return False
    
    def load_questions_from_file(self, file_path: str) -> List[str]:
        """טעינת שאלות מקובץ טקסט"""
        questions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                # התעלמות מהערות ושורות ריקות
                if line and not line.startswith('#') and not line.startswith('//'):
                    questions.append(line)
                    
        except Exception as e:
            print(f"❌ שגיאה בקריאת קובץ {file_path}: {e}")
            
        return questions
    
    def get_all_question_files(self) -> Dict[str, List[str]]:
        """איסוף כל קבצי השאלות"""
        questions_dir = os.path.join(current_dir, "questions")
        if not os.path.exists(questions_dir):
            print(f"❌ תיקיית השאלות לא נמצאה: {questions_dir}")
            return {}
            
        question_files = {}
        
        # חיפוש כל קבצי הטקסט בתיקיות
        for root, dirs, files in os.walk(questions_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, questions_dir)
                    category = relative_path.replace('\\', '/').replace('.txt', '')
                    question_files[category] = file_path
                    
        return question_files
    
    def test_single_question(self, question: str, category: str) -> Tuple[bool, str, str]:
        """בדיקת שאלה בודדת"""
        try:
            print(f"  🔍 בודק: {question}")
            
            # ניסיון לתרגם השאלה
            result = self.translator.translate_query(question)
            sql_query = result.get('sql_query', '') if isinstance(result, dict) else ''
            
            if sql_query and sql_query.strip():
                print(f"    ✅ SQL: {sql_query[:100]}...")
                return True, sql_query, "תורגם בהצלחה"
            else:
                print(f"    ❌ לא הצליח לתרגם")
                return False, "", "תרגום נכשל"
                
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ שגיאה: {error_msg}")
            return False, "", f"שגיאה: {error_msg}"
    
    def test_category(self, category: str, file_path: str) -> Dict:
        """בדיקת קטגוריה שלמה"""
        print(f"\n📂 בודק קטגוריה: {category}")
        print("=" * 60)
        
        questions = self.load_questions_from_file(file_path)
        if not questions:
            print(f"❌ לא נמצאו שאלות בקובץ: {file_path}")
            return {'total': 0, 'success': 0, 'failed': 0, 'details': []}
        
        category_results = {
            'total': len(questions),
            'success': 0, 
            'failed': 0,
            'details': []
        }
        
        for i, question in enumerate(questions, 1):
            success, sql, message = self.test_single_question(question, category)
            
            result_detail = {
                'question': question,
                'success': success,
                'sql': sql,
                'message': message,
                'number': i
            }
            
            category_results['details'].append(result_detail)
            
            if success:
                category_results['success'] += 1
            else:
                category_results['failed'] += 1
                
            # הפסקה קצרה בין שאלות
            time.sleep(0.1)
        
        success_rate = (category_results['success'] / category_results['total'] * 100) if category_results['total'] > 0 else 0
        print(f"\n📊 תוצאות {category}:")
        print(f"   🎯 סה\"כ שאלות: {category_results['total']}")
        print(f"   ✅ הצליחו: {category_results['success']}")
        print(f"   ❌ נכשלו: {category_results['failed']}")
        print(f"   📈 אחוז הצלחה: {success_rate:.1f}%")
        
        return category_results
    
    def run_all_tests(self) -> Dict:
        """הרצת כל הבדיקות"""
        print("🚀 מתחיל בדיקה כוללת של כל השאלות במערכת")
        print("=" * 80)
        
        if not self.initialize_translator():
            return self.results
            
        question_files = self.get_all_question_files()
        if not question_files:
            print("❌ לא נמצאו קבצי שאלות")
            return self.results
            
        print(f"📁 נמצאו {len(question_files)} קטגוריות שאלות")
        
        # בדיקת כל קטגוריה
        for category, file_path in question_files.items():
            category_results = self.test_category(category, file_path)
            self.results['categories'][category] = category_results
            
            # עדכון הסטטיסטיקות הכוללות
            self.results['total_questions'] += category_results['total']
            self.results['successful_answers'] += category_results['success']
            self.results['failed_answers'] += category_results['failed']
            
            # הוספת פרטים לרשימה הכוללת
            for detail in category_results['details']:
                detail['category'] = category
                self.results['details'].append(detail)
        
        return self.results
    
    def print_summary(self):
        """הדפסת סיכום התוצאות"""
        print("\n" + "=" * 80)
        print("📊 סיכום כללי - תוצאות הבדיקה")
        print("=" * 80)
        
        total = self.results['total_questions']
        success = self.results['successful_answers']
        failed = self.results['failed_answers']
        success_rate = (success / total * 100) if total > 0 else 0
        
        print(f"🎯 סה\"כ שאלות נבדקו: {total}")
        print(f"✅ תשובות מוצלחות: {success}")
        print(f"❌ תשובות כושלות: {failed}")
        print(f"📈 אחוז הצלחה כללי: {success_rate:.1f}%")
        
        print(f"\n📂 פירוט לפי קטגוריות:")
        print("-" * 60)
        
        for category, results in self.results['categories'].items():
            cat_success_rate = (results['success'] / results['total'] * 100) if results['total'] > 0 else 0
            status_icon = "✅" if cat_success_rate >= 80 else "⚠️" if cat_success_rate >= 60 else "❌"
            print(f"{status_icon} {category:30} {results['success']:3}/{results['total']:3} ({cat_success_rate:5.1f}%)")
        
        # הצגת השאלות הכושלות
        failed_questions = [d for d in self.results['details'] if not d['success']]
        if failed_questions:
            print(f"\n❌ שאלות שנכשלו ({len(failed_questions)}):")
            print("-" * 60)
            for i, failed in enumerate(failed_questions, 1):
                print(f"{i:2}. [{failed['category']}] {failed['question']}")
                print(f"    📝 {failed['message']}")
        
        # המלצות לשיפור
        print(f"\n💡 המלצות:")
        if success_rate >= 90:
            print("🎉 מעולה! המערכת עובדת בצורה מצוינת")
        elif success_rate >= 80:
            print("👍 טוב! יש מקום לשיפורים קטנים")
        elif success_rate >= 60:
            print("⚠️ בינוני - מומלץ לשפר דפוסי תרגום")
        else:
            print("🚨 נדרש שיפור משמעותי במערכת התרגום")
    
    def save_results(self, output_file: str = "test_results.json"):
        """שמירת התוצאות לקובץ JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"💾 התוצאות נשמרו ב: {output_file}")
        except Exception as e:
            print(f"❌ שגיאה בשמירת התוצאות: {e}")

def main():
    """פונקציה ראשית"""
    print("🏗️ מערכת בדיקת שאלות IFC-2-DuckDB")
    print("מפותח על ידי: AI Assistant")
    print(f"📅 תאריך: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # בדיקת קיום מסד הנתונים
    db_path = "guy_mador_shiba.duckdb"
    if not os.path.exists(db_path):
        print(f"❌ מסד הנתונים לא נמצא: {db_path}")
        print("🔧 אנא וודא שהקובץ קיים בתיקייה הנוכחית")
        sys.exit(1)
    
    # יצירת בודק השאלות
    tester = QuestionTester(db_path)
    
    try:
        # הרצת כל הבדיקות
        results = tester.run_all_tests()
        
        # הצגת סיכום
        tester.print_summary()
        
        # שמירת התוצאות
        tester.save_results()
        
        # קוד יציאה לפי התוצאות
        success_rate = (results['successful_answers'] / results['total_questions'] * 100) if results['total_questions'] > 0 else 0
        
        if success_rate >= 80:
            print(f"\n🎉 הבדיקה הושלמה בהצלחה! אחוז הצלחה: {success_rate:.1f}%")
            sys.exit(0)
        else:
            print(f"\n⚠️ הבדיקה הושלמה עם אזהרות. אחוז הצלחה: {success_rate:.1f}%")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ הבדיקה הופסקה על ידי המשתמש")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()