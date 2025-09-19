#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 IFC Query Logger
מערכת לוגים מתקדמת לתיעוד שאלות משתמשים
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class UserQuery:
    """מבנה נתונים לשאלת משתמש"""
    timestamp: str
    session_id: str
    user_question: str
    profession: Optional[str]  # אדריכל/מהנדס/בעל פרויקט
    category: Optional[str]    # הקטגוריה הספציפית
    query_type: str           # "predefined", "ai_translation", "manual_sql", "free_chat"
    sql_query: Optional[str]
    success: bool
    execution_time_ms: Optional[float]
    result_rows: Optional[int]
    error_message: Optional[str]
    ai_translation_used: bool
    user_agent: Optional[str]
    ip_address: Optional[str]

class IFCQueryLogger:
    """מחלקה לניהול לוגים של שאלות משתמשים"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # קבצי לוג שונים
        self.json_log_file = self.log_dir / "user_queries.jsonl"
        self.csv_log_file = self.log_dir / "user_queries.csv"
        self.daily_log_file = self.log_dir / f"queries_{datetime.now().strftime('%Y%m%d')}.log"
        
        # הגדרת logger רגיל
        self.setup_logging()
        
        # אתחול קובץ CSV אם לא קיים
        self.init_csv_file()
        
    def setup_logging(self):
        """הגדרת מערכת הלוגים הרגילה"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.daily_log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_csv_file(self):
        """אתחול קובץ CSV עם כותרות"""
        if not self.csv_log_file.exists():
            headers = [
                'timestamp', 'session_id', 'user_question', 'profession', 'category',
                'query_type', 'sql_query', 'success', 'execution_time_ms', 
                'result_rows', 'error_message', 'ai_translation_used'
            ]
            
            with open(self.csv_log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    def log_query(self, query: UserQuery):
        """רישום שאלה במערכת הלוגים"""
        try:
            # רישום ב-JSON Lines
            self._log_to_jsonl(query)
            
            # רישום ב-CSV
            self._log_to_csv(query)
            
            # רישום בלוג רגיל
            self._log_to_standard(query)
            
            print(f"✅ נרשם בלוג: {query.user_question[:50]}...")
            
        except Exception as e:
            self.logger.error(f"שגיאה ברישום לוג: {e}")
            
    def _log_to_jsonl(self, query: UserQuery):
        """רישום ב-JSON Lines (קל לעיבוד אוטומטי)"""
        with open(self.json_log_file, 'a', encoding='utf-8') as f:
            json.dump(asdict(query), f, ensure_ascii=False)
            f.write('\n')
            
    def _log_to_csv(self, query: UserQuery):
        """רישום ב-CSV (קל לעיבוד ב-Excel)"""
        with open(self.csv_log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            row = [
                query.timestamp, query.session_id, query.user_question,
                query.profession, query.category, query.query_type,
                query.sql_query, query.success, query.execution_time_ms,
                query.result_rows, query.error_message, query.ai_translation_used
            ]
            writer.writerow(row)
            
    def _log_to_standard(self, query: UserQuery):
        """רישום בלוג רגיל (קריא לבני אדם)"""
        status = "✅" if query.success else "❌"
        profession_info = f" [{query.profession}]" if query.profession else ""
        
        message = (
            f"{status} שאלה{profession_info}: '{query.user_question}' | "
            f"סוג: {query.query_type} | AI: {'כן' if query.ai_translation_used else 'לא'}"
        )
        
        if query.success and query.result_rows is not None:
            message += f" | תוצאות: {query.result_rows}"
        elif query.error_message:
            message += f" | שגיאה: {query.error_message}"
            
        self.logger.info(message)
        
    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """סטטיסטיקות יומיות"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        queries = self.load_queries_by_date(date)
        
        if not queries:
            return {"date": date, "total_queries": 0}
            
        stats = {
            "date": date,
            "total_queries": len(queries),
            "successful_queries": sum(1 for q in queries if q.get('success', False)),
            "ai_translations": sum(1 for q in queries if q.get('ai_translation_used', False)),
            "professions": {},
            "query_types": {},
            "most_common_questions": {},
            "avg_execution_time": 0,
            "total_results": sum(q.get('result_rows', 0) or 0 for q in queries)
        }
        
        # ניתוח לפי מקצועות
        for query in queries:
            prof = query.get('profession', 'לא מוגדר')
            stats["professions"][prof] = stats["professions"].get(prof, 0) + 1
            
        # ניתוח לפי סוגי שאלות
        for query in queries:
            q_type = query.get('query_type', 'לא מוגדר')
            stats["query_types"][q_type] = stats["query_types"].get(q_type, 0) + 1
            
        # שאלות נפוצות
        questions = [q.get('user_question', '') for q in queries]
        for question in questions:
            if len(question) > 10:  # רק שאלות אמיתיות
                stats["most_common_questions"][question] = stats["most_common_questions"].get(question, 0) + 1
                
        # זמן ביצוע ממוצע
        execution_times = [q.get('execution_time_ms') for q in queries if q.get('execution_time_ms')]
        if execution_times:
            stats["avg_execution_time"] = sum(execution_times) / len(execution_times)
            
        return stats
        
    def load_queries_by_date(self, date: str) -> List[Dict]:
        """טעינת שאלות לפי תאריך"""
        queries = []
        
        if not self.json_log_file.exists():
            return queries
            
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        query = json.loads(line)
                        query_date = query.get('timestamp', '')[:10]  # YYYY-MM-DD
                        if query_date == date:
                            queries.append(query)
        except Exception as e:
            self.logger.error(f"שגיאה בטעינת שאלות: {e}")
            
        return queries
        
    def generate_analytics_report(self, days: int = 7) -> str:
        """יצירת דוח ניתוח לתקופה"""
        report = ["🔍 דוח ניתוח שאלות משתמשים", "=" * 50]
        
        from datetime import timedelta
        end_date = datetime.now()
        
        total_queries = 0
        total_successes = 0
        profession_stats = {}
        
        for i in range(days):
            current_date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats = self.get_daily_stats(current_date)
            
            if daily_stats["total_queries"] > 0:
                total_queries += daily_stats["total_queries"]
                total_successes += daily_stats.get("successful_queries", 0)
                
                report.append(f"\n📅 {current_date}:")
                report.append(f"   🎯 סה\"כ שאלות: {daily_stats['total_queries']}")
                report.append(f"   ✅ הצליחו: {daily_stats.get('successful_queries', 0)}")
                report.append(f"   🤖 AI: {daily_stats.get('ai_translations', 0)}")
                
                # צבירת סטטיסטיקות מקצועות
                for prof, count in daily_stats.get("professions", {}).items():
                    profession_stats[prof] = profession_stats.get(prof, 0) + count
                    
        # סיכום כללי
        success_rate = (total_successes / total_queries * 100) if total_queries > 0 else 0
        
        report.extend([
            "\n" + "=" * 50,
            "📊 סיכום כללי:",
            f"🎯 סה\"כ שאלות: {total_queries}",
            f"✅ אחוז הצלחה: {success_rate:.1f}%",
            f"👥 מקצועות פעילים: {len(profession_stats)}",
            "\n📈 פילוח לפי מקצועות:"
        ])
        
        for prof, count in sorted(profession_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_queries * 100) if total_queries > 0 else 0
            report.append(f"   {prof}: {count} ({percentage:.1f}%)")
            
        return "\n".join(report)
        
    def export_data(self, output_format: str = "excel", days: int = 30) -> str:
        """ייצוא נתונים לפורמטים שונים"""
        from datetime import timedelta
        
        # איסוף נתונים
        end_date = datetime.now()
        all_queries = []
        
        for i in range(days):
            current_date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_queries = self.load_queries_by_date(current_date)
            all_queries.extend(daily_queries)
            
        if not all_queries:
            return "❌ לא נמצאו נתונים לייצוא"
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format.lower() == "excel":
            # ייצוא ל-Excel
            try:
                import pandas as pd
                
                df = pd.DataFrame(all_queries)
                output_file = self.log_dir / f"query_analytics_{timestamp}.xlsx"
                df.to_excel(output_file, index=False)
                
                return f"✅ ייצוא ל-Excel: {output_file}"
                
            except ImportError:
                return "❌ pandas לא מותקן - לא ניתן לייצא ל-Excel"
                
        elif output_format.lower() == "json":
            # ייצוא ל-JSON
            output_file = self.log_dir / f"query_analytics_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_queries, f, ensure_ascii=False, indent=2)
                
            return f"✅ ייצוא ל-JSON: {output_file}"
            
        else:
            return f"❌ פורמט לא נתמך: {output_format}"

# Global logger instance
query_logger = IFCQueryLogger()

def log_user_question(
    user_question: str,
    profession: str = None,
    category: str = None,
    query_type: str = "free_chat",
    sql_query: str = None,
    success: bool = True,
    execution_time_ms: float = None,
    result_rows: int = None,
    error_message: str = None,
    ai_translation_used: bool = False,
    session_id: str = None
):
    """פונקציה נוחה לרישום שאלת משתמש"""
    
    if session_id is None:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    query = UserQuery(
        timestamp=datetime.now().isoformat(),
        session_id=session_id,
        user_question=user_question,
        profession=profession,
        category=category,
        query_type=query_type,
        sql_query=sql_query,
        success=success,
        execution_time_ms=execution_time_ms,
        result_rows=result_rows,
        error_message=error_message,
        ai_translation_used=ai_translation_used,
        user_agent=None,  # יכול להיות מוגדר מ-Streamlit
        ip_address=None   # יכול להיות מוגדר מ-Streamlit
    )
    
    query_logger.log_query(query)