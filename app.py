#!/usr/bin/env python3
"""
🏗️ IFC Database Professional Interface
ממשק מקצועי לשאילתות על מסד נתונים IFC לפי מקצועות בנייה
"""

import streamlit as st
import duckdb
import pandas as pd
import time
import random
from typing import List, Dict, Any
import re
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional for cloud deployment
    pass
import uuid

# Import query logger
try:
    from query_logger import log_user_question, query_logger
    LOGGING_ENABLED = True
except ImportError:
    # Fallback if query_logger not available
    def log_user_question(*args, **kwargs):
        pass
    query_logger = None
    LOGGING_ENABLED = False

# Try to import AI translator (optional)
try:
    from ai_translator import IFCQueryTranslator
    AI_ENABLED = bool(os.getenv('ENABLE_AI_TRANSLATION', 'true').lower() == 'true')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
        AI_ENABLED = False
except ImportError:
    AI_ENABLED = False
    IFCQueryTranslator = None

# Import all queries from the existing file
from collections import namedtuple

Query = namedtuple('Query', ['id', 'category', 'title', 'sql', 'description'])

# Configuration - for cloud deployment, database will be uploaded by user
DATABASE_PATH = "sample_demo.duckdb"  # Default demo database name
APP_TITLE = "🏗️ מערכת ניתוח נתוני IFC"
APP_SUBTITLE = "ממשק מקצועי לאדריכלים, מהנדסים ובעלי פרויקטים"

# Professional question categories organized by profession
PROFESSIONAL_QUESTIONS = {
    "👷‍♀️ אדריכל": {
        "🧱 אלמנטי בנייה": [
            "כמה קירות יש בפרויקט?",
            "מה גובה הקירות הממוצע?",
            "איזה קירות הכי עבים?",
            "כמה דלתות יש בפרויקט?",
            "מה רוחב הדלתות הרגילות?",
            "איזה חלונות הכי גדולים?",
            "מה שטח התקרות הכולל?",
            "איזה רצפות הכי עבות?"
        ],
        "🏠 חללים ומרחבים": [
            "כמה חדרים יש בפרויקט?",
            "מה שטח החדרים הכולל?",
            "איזה החדר הכי גדול?",
            "כמה חדרי שינה יש?",
            "מה נפח האוויר הכולל?",
            "מה שטח המרפסות?"
        ],
        "🎨 תכנון ועיצוב": [
            "איזה חדרים קשורים פונקציונלית?",
            "איזה אזורים פרטיים וציבוריים?",
            "איזה חדרים עם חלונות?",
            "איזה אזורים עם תאורה טבעית?",
            "מה כיוון החדרים הראשיים?",
            "איזה חלקים נגישים לנכים?"
        ]
    },
    "🔧 מהנדס": {
        "🏗️ מבנה וקונסטרוקציה": [
            "כמה קורות יש בפרויקט?",
            "מה מידות הקורות הראשיות?",
            "איזה עמודים הכי עבים?",
            "מה אורך הקורות הכולל?",
            "איזה קורות מברזל?",
            "כמה עמודים בקומה השנייה?",
            "מה משקל הקונסטרוקציה?",
            "מה גובה העמודים הממוצע?"
        ],
        "⚡ מערכות ותשתיות": [
            "כמה יחידות מיזוג יש?",
            "מה הספק המיזוג הכולל?",
            "איזה צנרת למים חמים?",
            "כמה נקודות תאורה יש?",
            "מה צריכת החשמל הצפויה?",
            "איזה מערכות אוטומציה?",
            "כמה שקעי חשמל בכל חדר?",
            "איזה מערכות גילוי אש?"
        ],
        "📊 כמויות וחומרים": [
            "כמה קוב בטון נדרש?",
            "מה משקל הברזל הכולל?",
            "איזה חומרי גמר נצרכים?",
            "כמה מ\"ר אריחים?",
            "מה נפח הבידוד התרמי?",
            "מה כמות הזכוכית?",
            "איזה חומרי חשמל נדרשים?",
            "כמה מטרים של צנרת?"
        ]
    },
    "💼 בעל פרויקט": {
        "📈 התקדמות ביצוע": [
            "מה אחוז השלמה הכולל?",
            "איזה משימות בוצעו השבוע?",
            "כמה ימי עבודה נותרו?",
            "מה התקדמות השלד הגס?",
            "איזה שלבים מאחרים?",
            "כמה אחוז מהחשמל הושלם?",
            "מה מצב עבודות הגמר?",
            "כמה אחוז מהתשתיות הושלמו?"
        ],
        "💰 עלויות ותקציב": [
            "מה העלות הכוללת עד כה?",
            "איזה פריטים חורגים מהתקציב?",
            "כמה עולה מ\"ר בנוי?",
            "מה עלות החומרים השבוע?",
            "איזה עבודות הכי יקרות?",
            "כמה חסכנו בהזמנה קבוצתית?",
            "מה עלות שעות העבודה?",
            "איזה הוצאות לא צפויות?"
        ],
        "⏰ לוחות זמנים": [
            "מתי צפוי סיום הפרויקט?",
            "איזה משימות קריטיות השבוע?",
            "כמה זמן נדרש לגמר?",
            "מה התאריך הצפוי למסירה?",
            "איזה עבודות מקבילות?",
            "כמה ימי גשם עיכבו?",
            "איזה משימות תלויות?",
            "מה תאריך קבלת אישורים?"
        ]
    }
}

# Initialize AI translator
@st.cache_resource
def get_ai_translator():
    """אתחול המתרגם AI (cached)"""
    if AI_ENABLED and IFCQueryTranslator:
        try:
            return IFCQueryTranslator(DATABASE_PATH)
        except Exception as e:
            st.error(f"Failed to initialize AI translator: {e}")
            return None
    return None

# All 50 queries from the original file
QUERIES_50 = [
    # ===== אלמנטים קונסטרוקטיביים =====
    Query(1, "אלמנטים קונסטרוקטיביים", "כמה קירות יש בכל קומה?", 
          """SELECT bs.Name as storey_name, COUNT(w.ifc_id) as wall_count
             FROM ifcbuildingstorey bs
             LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
             LEFT JOIN ifcwall w ON w.ifc_id = ANY(rel.RelatedElements)
             GROUP BY bs.ifc_id, bs.Name
             ORDER BY wall_count DESC""",
          "מראה חלוקה של קירות לפי קומות"),
    
    Query(2, "אלמנטים קונסטרוקטיביים", "מהם הממדים של כל הקורות?",
          """SELECT p.ifc_id, p.name, p.value
             FROM psets p
             WHERE p.pset_name = 'Pset_BeamCommon' 
             AND p.name IN ('Length', 'Width', 'Height')
             ORDER BY p.ifc_id, p.name""",
          "חילוץ ממדי הקורות (אורך, רוחב, גובה)"),
    
    Query(3, "אלמנטים קונסטרוקטיביים", "איזה עמודים הכי גבוהים?",
          """SELECT p.ifc_id, p.value as height
             FROM psets p
             JOIN id_map im ON p.ifc_id = im.ifc_id
             WHERE im.ifc_class = 'IfcColumn' 
             AND p.name = 'Height'
             ORDER BY CAST(p.value AS DOUBLE) DESC
             LIMIT 10""",
          "רשימת 10 העמודים הגבוהים ביותר"),
    
    Query(4, "אלמנטים קונסטרוקטיביים", "מהו השטח הכולל של כל הרצפות?",
          """SELECT SUM(CAST(p.value AS DOUBLE)) as total_area
             FROM psets p
             JOIN id_map im ON p.ifc_id = im.ifc_id
             WHERE im.ifc_class = 'IfcSlab' 
             AND p.name = 'Area'""",
          "חישוב סך השטח של כל הרצפות"),
    
    Query(5, "אלמנטים קונסטרוקטיביים", "איזה קירות הכי עבים?",
          """SELECT p.ifc_id, p.value as thickness
             FROM psets p
             JOIN id_map im ON p.ifc_id = im.ifc_id
             WHERE im.ifc_class IN ('IfcWall', 'IfcWallStandardCase')
             AND p.name = 'Width'
             ORDER BY CAST(p.value AS DOUBLE) DESC""",
          "מיון הקירות לפי עובי"),
    
    # ===== חומרים ומאפיינים =====
    Query(6, "חומרים ומאפיינים", "איזה חומרים נמצאים בשימוש הרב ביותר?",
          """SELECT m.Name as material_name, COUNT(ram.RelatingMaterial) as usage_count
             FROM ifcmaterial m
             LEFT JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
             GROUP BY m.ifc_id, m.Name
             ORDER BY usage_count DESC""",
          "דירוג החומרים לפי שכיחות השימוש"),
    
    Query(7, "חומרים ומאפיינים", "איזה אלמנטים עשויים מפלדה?",
          """SELECT im.ifc_class, COUNT(*) as count
             FROM ifcmaterial m
             JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
             JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
             WHERE m.Name LIKE '%Steel%' OR m.Name LIKE '%steel%'
             GROUP BY im.ifc_class
             ORDER BY count DESC""",
          "אלמנטים המיוצרים מפלדה"),
    
    Query(8, "חומרים ומאפיינים", "מהן השכבות בקירות המרוכבים?",
          """SELECT ml.Name as layer_name, ml.LayerThickness
             FROM ifcmateriallayer ml
             ORDER BY ml.LayerThickness DESC""",
          "פירוט שכבות החומרים בקירות"),
    
    Query(9, "חומרים ומאפיינים", "איזה צבעים יש לחומרים?",
          """SELECT materials
             FROM geometry
             WHERE materials IS NOT NULL
             LIMIT 10""",
          "מידע על צבעי החומרים מנתוני הגיאומטריה"),
    
    Query(10, "חומרים ומאפיינים", "איזה אלמנטים עשויים מבטון?",
          """SELECT im.ifc_class, im.ifc_id
             FROM ifcmaterial m
             JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
             JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
             WHERE m.Name LIKE '%Concrete%' OR m.Name LIKE '%concrete%'""",
          "זיהוי אלמנטי בטון בפרויקט"),
    
    # ===== מערכות MEP =====
    Query(11, "מערכות MEP", "מהו האורך הכולל של כל הצנרת?",
          """SELECT SUM(CAST(p.value AS DOUBLE)) as total_pipe_length
             FROM psets p
             WHERE p.pset_name = 'Pset_FlowSegmentPipeSegment' 
             AND p.name = 'Length'""",
          "חישוב סך האורך של צנרת במערכות"),
    
    Query(12, "מערכות MEP", "איזה סוגי שסתומים יש במערכות?",
          """SELECT Name as valve_type, COUNT(*) as count
             FROM ifcvalvetype
             GROUP BY Name
             ORDER BY count DESC""",
          "סוגי השסתומים ומספרם"),
    
    Query(13, "מערכות MEP", "כמה יציאות יש לכל מערכת?",
          """SELECT COUNT(dp.ifc_id) as port_count
             FROM ifcdistributionport dp""",
          "ספירת יציאות החיבור במערכות"),
    
    Query(14, "מערכות MEP", "מהן מערכות האוורור?",
          """SELECT SUM(CAST(p.value AS DOUBLE)) as total_duct_length
             FROM psets p
             WHERE p.pset_name = 'Pset_FlowSegmentDuctSegment' 
             AND p.name = 'Length'""",
          "חישוב סך האורך של תעלות אוורור"),
    
    Query(15, "מערכות MEP", "איזה מערכות משרתות את הבניין?",
          """SELECT COUNT(*) as system_count
             FROM ifcsystem""",
          "מספר המערכות הטכניות בבניין"),
    
    # ===== גיאומטריה ונפחים =====
    Query(16, "גיאומטריה ונפחים", "כמה אובייקטים יש עם נתוני גיאומטריה?",
          """SELECT COUNT(*) as objects_with_geometry
             FROM geometry""",
          "ספירת אובייקטים עם ייצוג גיאומטרי"),
    
    Query(17, "גיאומטריה ונפחים", "מהן הצורות הגיאומטריות השכיחות?",
          """SELECT COUNT(*) as shape_count
             FROM shape""",
          "ספירת הצורות הגיאומטריות במודל"),
    
    Query(18, "גיאומטריה ונפחים", "מהו הנפח הכולל של האלמנטים?",
          """SELECT SUM(CAST(p.value AS DOUBLE)) as total_volume
             FROM psets p
             WHERE p.name = 'Volume'""",
          "חישוב סך הנפח של כל האלמנטים"),
    
    Query(19, "גיאומטריה ונפחים", "איזה אלמנטים הכי גדולים בשטח?",
          """SELECT p.ifc_id, p.value as area
             FROM psets p
             WHERE p.name = 'Area'
             ORDER BY CAST(p.value AS DOUBLE) DESC
             LIMIT 10""",
          "10 האלמנטים עם השטח הגדול ביותר"),
    
    Query(20, "גיאומטריה ונפחים", "כמה נקודות קרטזיות יש במודל?",
          """SELECT COUNT(*) as cartesian_points
             FROM id_map
             WHERE ifc_class = 'IfcCartesianPoint'""",
          "ספירת נקודות קרטזיות במודל הגיאומטרי"),
    
    # ===== Property Sets ותכונות =====
    Query(21, "Property Sets ותכונות", "איזה Property Sets קשורים לדלתות?",
          """SELECT DISTINCT p.pset_name, COUNT(*) as count
             FROM psets p
             JOIN id_map im ON p.ifc_id = im.ifc_id
             WHERE im.ifc_class = 'IfcDoor'
             GROUP BY p.pset_name
             ORDER BY count DESC""",
          "קבוצות תכונות של דלתות"),
    
    Query(22, "Property Sets ותכונות", "איזה תכונות קשורות לאבטחת אש?",
          """SELECT p.name, p.value, COUNT(*) as count
             FROM psets p
             WHERE p.name LIKE '%Fire%' OR p.pset_name LIKE '%Fire%'
             GROUP BY p.name, p.value
             ORDER BY count DESC""",
          "תכונות הקשורות לאבטחת אש"),
    
    Query(23, "Property Sets ותכונות", "מהן התכונות הנפוצות ביותר?",
          """SELECT p.name as property_name, COUNT(*) as count
             FROM psets p
             GROUP BY p.name
             ORDER BY count DESC
             LIMIT 20""",
          "20 התכונות השכיחות ביותר"),
    
    Query(24, "Property Sets ותכונות", "איזה אלמנטים יש להם תכונת LoadBearing?",
          """SELECT im.ifc_class, p.value as load_bearing, COUNT(*) as count
             FROM psets p
             JOIN id_map im ON p.ifc_id = im.ifc_id
             WHERE p.name = 'LoadBearing'
             GROUP BY im.ifc_class, p.value
             ORDER BY count DESC""",
          "אלמנטים נושאי משקל"),
    
    Query(25, "Property Sets ותכונות", "מהן תכונות הקיימות (Sustainability)?",
          """SELECT p.name, p.value
             FROM psets p
             WHERE p.name LIKE '%Sustainability%' OR p.pset_name LIKE '%Environmental%'""",
          "תכונות קיימות וסביבה"),
    
    # ===== מבנה הבניין =====
    Query(26, "מבנה הבניין", "מהן הקומות בבניין?",
          """SELECT Name as storey_name, Elevation
             FROM ifcbuildingstorey
             ORDER BY Elevation""",
          "רשימת קומות וגובהן"),
    
    Query(27, "מבנה הבניין", "כמה אלמנטים יש בכל קומה?",
          """SELECT bs.Name as storey_name, COUNT(rel.RelatedElements) as element_count
             FROM ifcbuildingstorey bs
             LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
             GROUP BY bs.ifc_id, bs.Name
             ORDER BY element_count DESC""",
          "חלוקת אלמנטים לפי קומות"),
    
    # ===== פתחים (דלתות וחלונות) =====
    Query(28, "פתחים (דלתות וחלונות)", "מהן תכונות הדלתות?",
          """SELECT d.Name, d.OverallHeight, d.OverallWidth
             FROM ifcdoor d
             WHERE d.Name IS NOT NULL""",
          "ממדי הדלתות"),
    
    Query(29, "פתחים (דלתות וחלונות)", "מהן תכונות החלונות?",
          """SELECT w.Name, w.OverallHeight, w.OverallWidth
             FROM ifcwindow w
             WHERE w.Name IS NOT NULL""",
          "ממדי החלונות"),
    
    # ===== מבנה מסד הנתונים =====
    Query(30, "מבנה מסד הנתונים", "איזה טבלאות קיימות במסד הנתונים?",
          "SHOW TABLES",
          "הצגת כל הטבלאות במסד הנתונים"),
    
    Query(31, "מבנה מסד הנתונים", "מבנה טבלת הקירות",
          "DESCRIBE ifcwall",
          "הצגת מבנה טבלת הקירות"),
    
    Query(32, "סטטיסטיקות כלליות", "כמה אלמנטים מכל סוג יש?",
          """SELECT ifc_class, COUNT(*) as count
             FROM id_map
             GROUP BY ifc_class
             ORDER BY count DESC""",
          "ספירת אלמנטים לפי סוג"),
    
    Query(33, "סטטיסטיקות כלליות", "Property Sets הכי נפוצים",
          """SELECT pset_name, COUNT(*) as usage_count
             FROM psets
             GROUP BY pset_name
             ORDER BY usage_count DESC
             LIMIT 10""",
          "10 ה-Property Sets הנפוצים ביותר"),
    
    Query(34, "גיאומטריה ונפחים", "אלמנטים עם נתוני גיאומטריה",
          """SELECT COUNT(*) as elements_with_geometry
             FROM shape s
             WHERE s.geometry IS NOT NULL""",
          "כמה אלמנטים כוללים נתוני גיאומטריה"),
    
    Query(35, "ניתוח איכות ושלמות", "איזה אלמנטים חסרים Property Sets?",
          """SELECT im.ifc_class, COUNT(*) as no_psets_count
             FROM id_map im
             LEFT JOIN psets p ON im.ifc_id = p.ifc_id
             WHERE p.ifc_id IS NULL
             GROUP BY im.ifc_class
             ORDER BY no_psets_count DESC""",
          "אלמנטים ללא תכונות"),
]

# Security function to check if query is safe (only SELECT allowed)
def is_safe_query(query: str) -> bool:
    """בדוק אם השאילתה בטוחה (רק SELECT מותר)"""
    query_clean = query.strip().upper()
    
    # Allow only SELECT statements and SHOW/DESCRIBE commands
    allowed_starts = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN']
    if not any(query_clean.startswith(start) for start in allowed_starts):
        return False
    
    # Block dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 
        'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'PRAGMA'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_clean:
            return False
    
    return True

def translate_natural_query(natural_question: str) -> Dict[str, Any]:
    """תרגום שאלה בשפה טבעית לשאילתת SQL"""
    translator = get_ai_translator()
    
    if not translator:
        return {
            'sql_query': None,
            'confidence': 0.0,
            'explanation': 'AI translator not available. Check your OpenAI API key in .env file.',
            'error': 'AI_NOT_ENABLED'
        }
    
    return translator.translate_query(natural_question)

def execute_query(query: str) -> tuple[bool, Any]:
    """הרץ שאילתה על מסד הנתונים"""
    try:
        if not is_safe_query(query):
            return False, "❌ שגיאת בטחון: רק שאילתות SELECT, SHOW ו-DESCRIBE מותרות"
        
        conn = duckdb.connect(DATABASE_PATH)
        result = conn.execute(query).fetchdf()
        conn.close()
        
        return True, result
    
    except Exception as e:
        return False, f"❌ שגיאה: {str(e)}"

def get_predefined_queries() -> List[Query]:
    """הבא שאילתות מוכנות מראש"""
    return QUERIES_50

def init_session_state():
    """אתחול מצב ה-session"""
    # Initialize session tracking
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """שלום! 👋 אני עוזר הדאטאבייס שלך לפרויקט **Guy Mador Shiba V.3.0**

🔍 **מה אני יכול לעזור לך?**
- לחקור את מסד הנתונים IFC שלך
- להריץ שאילתות SQL מותאמות אישית
- לבחור מתוך **35 שאילתות מוכנות** לפי קטגוריות
- לנתח אלמנטים קונסטרוקטיביים, חומרים, גיאומטריה ועוד

📋 **התחל עכשיו:**
- בחר שאילתה מוכנה מהתפריט בצד שמאל
- או כתוב שאילתת SQL מותאמת אישית
- שאל "עזרה" למידע נוסף

מה תרצה לחקור היום? 🏗️"""
            }
        ]

def display_chat_message(role: str, content: str):
    """הצג הודעת צ'אט"""
    with st.chat_message(role):
        st.markdown(content)

def display_query_result(result_df: pd.DataFrame, query: str, original_question: str = None):
    """הצג תוצאות שאילתה עם פרשנות חכמה"""
    with st.chat_message("assistant"):
        st.markdown("📊 **תוצאות השאילתה:**")
        
        # AI Interpretation if available and original question provided
        if AI_ENABLED and original_question:
            try:
                translator = get_ai_translator()
                if translator:
                    with st.spinner("🤖 מפרש תוצאות..."):
                        interpretation = translator.interpret_results(
                            original_question, query, result_df, True
                        )
                    
                    st.markdown("### 🧠 פרשנות חכמה:")
                    st.markdown(interpretation)
                    st.divider()
            except Exception as e:
                st.warning(f"לא הצלחתי ליצור פרשנות: {str(e)}")
        
        # Show query that was executed
        with st.expander("🔍 השאילתה שהורצה"):
            st.code(query, language="sql")
        
        # Show results
        if len(result_df) == 0:
            st.info("🔍 השאילתה לא החזירה תוצאות")
        else:
            st.markdown("### 📋 נתונים גולמיים:")
            st.dataframe(result_df, width="stretch")
            st.caption(f"📈 נמצאו {len(result_df)} שורות")
            
            # Add download button for results
            csv = result_df.to_csv(index=False, encoding='utf-8-sig')
            import random
            unique_key = f"download_legacy_{random.randint(1000, 9999)}_{int(time.time() * 1000)}"
            st.download_button(
                label="💾 הורד תוצאות כ-CSV",
                data=csv,
                file_name=f"query_results_{int(time.time())}.csv",
                mime="text/csv",
                key=unique_key
            )

def render_chat_messages():
    """רינדור הודעות הצ'אט"""
    for message in st.session_state.messages:
        if message["content"] == "query_result":
            # Enhanced display for query results
            with st.chat_message("assistant"):
                if "query_title" in message:
                    st.markdown(f"📊 **תוצאות עבור:** {message['query_title']}")
                    st.caption(message.get('query_description', ''))
                else:
                    st.markdown("📊 **תוצאות השאילתה:**")
                
                # Show query that was executed
                with st.expander("🔍 השאילתה שהורצה"):
                    st.code(message["query"], language="sql")
                
                # Show AI interpretation if available
                if AI_ENABLED and "query_title" in message:
                    try:
                        translator = get_ai_translator()
                        if translator:
                            with st.spinner("🤖 מפרש תוצאות..."):
                                interpretation = translator.interpret_results(
                                    message["query_title"], 
                                    message["query"], 
                                    message["result_df"], 
                                    True
                                )
                            
                            st.markdown("### 🧠 פרשנות חכמה:")
                            st.markdown(interpretation)
                            st.divider()
                    except Exception as e:
                        st.warning(f"לא הצלחתי ליצור פרשנות: {str(e)}")
                
                # Show results
                result_df = message["result_df"]
                if len(result_df) == 0:
                    st.info("🔍 השאילתה לא החזירה תוצאות")
                else:
                    st.markdown("### 📋 נתונים גולמיים:")
                    st.dataframe(result_df, use_container_width=True)
                    st.caption(f"📈 נמצאו {len(result_df)} שורות")
                    
                    # Add download button
                    csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                    import random
                    unique_key = f"download_{random.randint(1000, 9999)}_{int(time.time() * 1000)}"
                    st.download_button(
                        label="💾 הורד תוצאות כ-CSV",
                        data=csv,
                        file_name=f"query_results_{int(time.time())}.csv",
                        mime="text/csv",
                        key=unique_key
                    )
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def render_chat_input():
    """רינדור תיבת הקלט של הצ'אט"""
    
    # Handle example question from sidebar
    example_question = st.session_state.get('example_question', '')
    if example_question:
        st.session_state.example_question = ''  # Clear it
        user_input = example_question
    else:
        # Chat input
        user_input = st.chat_input(
            "שאל שאלה על הפרויקט... (למשל: 'כמה קירות יש?')" if AI_ENABLED 
            else "הכנס שאילתת SQL..."
        )
    
    if user_input:
        start_time = time.time()
        
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        if AI_ENABLED:
            # Use AI to translate and execute
            translator = get_ai_translator()
            if translator:
                try:
                    with st.spinner("🤖 מעבד שאלה..."):
                        result = translator.translate_query(user_input)
                        
                    if isinstance(result, dict) and result.get('sql_query'):
                        sql_query = result['sql_query']
                        
                        # Show the translated query
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🔄 **תרגמתי את השאלה ל-SQL:**\n```sql\n{sql_query}\n```\n\n⏳ מריץ שאילתה..."
                        })
                        
                        # Execute the query
                        success, query_result = execute_query(sql_query)
                        execution_time = (time.time() - start_time) * 1000
                        
                        if success:
                            result_rows = len(query_result) if hasattr(query_result, '__len__') else None
                            
                            # Log successful query
                            log_user_question(
                                user_question=user_input,
                                query_type="free_chat",
                                sql_query=sql_query,
                                success=True,
                                execution_time_ms=execution_time,
                                result_rows=result_rows,
                                ai_translation_used=True,
                                session_id=st.session_state.session_id
                            )
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "query_result",
                                "result_df": query_result,
                                "query": sql_query,
                                "query_title": user_input,
                                "query_description": f"תרגום של: {user_input}"
                            })
                        else:
                            # Log failed query
                            log_user_question(
                                user_question=user_input,
                                query_type="free_chat",
                                sql_query=sql_query,
                                success=False,
                                execution_time_ms=execution_time,
                                error_message=str(query_result),
                                ai_translation_used=True,
                                session_id=st.session_state.session_id
                            )
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"❌ שגיאה בהרצת השאילתה:\n```\n{query_result}\n```"
                            })
                    else:
                        # Log failed translation
                        log_user_question(
                            user_question=user_input,
                            query_type="free_chat",
                            success=False,
                            execution_time_ms=(time.time() - start_time) * 1000,
                            error_message="Failed to translate question",
                            ai_translation_used=True,
                            session_id=st.session_state.session_id
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ לא הצלחתי לתרגם את השאלה. נסה לנסח אחרת או השתמש ב-SQL ישירות."
                        })
                        
                except Exception as e:
                    # Log exception
                    log_user_question(
                        user_question=user_input,
                        query_type="free_chat",
                        success=False,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        error_message=str(e),
                        ai_translation_used=True,
                        session_id=st.session_state.session_id
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ שגיאה בתרגום: {str(e)}"
                    })
            else:
                # Log AI not available
                log_user_question(
                    user_question=user_input,
                    query_type="free_chat",
                    success=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error_message="AI translator not available",
                    ai_translation_used=False,
                    session_id=st.session_state.session_id
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "❌ מתרגם ה-AI לא זמין"
                })
        else:
            # Manual SQL mode
            if user_input.strip().upper().startswith('SELECT'):
                success, result = execute_query(user_input)
                execution_time = (time.time() - start_time) * 1000
                
                if success:
                    result_rows = len(result) if hasattr(result, '__len__') else None
                    
                    # Log successful manual SQL
                    log_user_question(
                        user_question=user_input,
                        query_type="manual_sql",
                        sql_query=user_input,
                        success=True,
                        execution_time_ms=execution_time,
                        result_rows=result_rows,
                        ai_translation_used=False,
                        session_id=st.session_state.session_id
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "query_result",
                        "result_df": result,
                        "query": user_input,
                        "query_title": "שאילתת SQL ידנית",
                        "query_description": "הקלדה ידנית"
                    })
                else:
                    # Log failed manual SQL
                    log_user_question(
                        user_question=user_input,
                        query_type="manual_sql",
                        sql_query=user_input,
                        success=False,
                        execution_time_ms=execution_time,
                        error_message=str(result),
                        ai_translation_used=False,
                        session_id=st.session_state.session_id
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ שגיאה בהרצת השאילתה:\n```\n{result}\n```"
                    })
            else:
                # Log invalid manual input
                log_user_question(
                    user_question=user_input,
                    query_type="manual_sql",
                    success=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error_message="Invalid SQL - must start with SELECT",
                    ai_translation_used=False,
                    session_id=st.session_state.session_id
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ במצב ידני, אנא הכנס שאילתת SQL תקינה שמתחילה ב-SELECT"
                })
        
        st.rerun()

def main():
    """פונקציה ראשית - ממשק מקצועי מינימליסטי"""
    
    # Page config
    st.set_page_config(
        page_title="מערכת ניתוח נתוני IFC",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Check if database exists for cloud deployment
    if not os.path.exists(DATABASE_PATH):
        st.error(f"⚠️ מסד הנתונים {DATABASE_PATH} לא נמצא")
        st.info("📤 אנא העלה קובץ מסד נתונים DuckDB")
        
        uploaded_db = st.file_uploader("העלה קובץ DuckDB", type=['duckdb', 'db'])
        if uploaded_db is not None:
            with open(DATABASE_PATH, "wb") as f:
                f.write(uploaded_db.getvalue())
            st.success(f"✅ מסד הנתונים הועלה בהצלחה: {DATABASE_PATH}")
            st.rerun()
        return
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS for minimalist design
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .profession-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .category-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    .question-button {
        margin: 0.2rem 0;
        width: 100%;
    }
    .ai-status {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Status indicator (floating)
    ai_status_text = "🤖 AI פעיל" if AI_ENABLED else "🔧 ידני"
    ai_color = "success" if AI_ENABLED else "warning"
    
    # Professional interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 שאלה חופשית",
        "👷‍♀️ אדריכל", 
        "🔧 מהנדס", 
        "💼 בעל פרויקט",
        "📊 Analytics"
    ])
    
    # Free form question tab (default)
    with tab1:
        render_chat_interface()

    # Architect tab
    with tab2:
        render_profession_interface("👷‍♀️ אדריכל")
    
    # Engineer tab  
    with tab3:
        render_profession_interface("🔧 מהנדס")
    
    # Project Owner tab
    with tab4:
        render_profession_interface("💼 בעל פרויקט")
    
    # Analytics tab
    with tab5:
        render_analytics_tab()

def render_profession_interface(profession: str):
    """רינדור ממשק מקצועי מסודר"""
    
    if profession not in PROFESSIONAL_QUESTIONS:
        st.error(f"מקצוע {profession} לא נמצא")
        return
    
    st.markdown(f"### {profession}")
    st.caption("בחר קטגוריה ולחץ על שאלה לקבלת תשובה מיידית")
    
    # Status indicator
    col1, col2 = st.columns([3, 1])
    with col2:
        if AI_ENABLED:
            st.success("🤖 AI פעיל")
        else:
            st.warning("🔧 ידני")
    
    # Categories for this profession
    categories = PROFESSIONAL_QUESTIONS[profession]
    
    # Render categories in columns for better layout
    num_categories = len(categories)
    if num_categories <= 2:
        cols = st.columns(num_categories)
    else:
        # For more categories, use 2 columns
        cols = st.columns(2)
    
    col_index = 0
    for category_name, questions in categories.items():
        with cols[col_index % len(cols)]:
            # Category card
            st.markdown(f"""
            <div class="category-header">
                {category_name}
            </div>
            """, unsafe_allow_html=True)
            
            # Questions as clean buttons
            for i, question in enumerate(questions):
                if st.button(
                    question,
                    key=f"{profession}_{category_name}_{i}",
                    help="לחץ לשאילה על מסד הנתונים",
                    use_container_width=True
                ):
                    handle_question(question, f"{profession} - {category_name}")
        
        col_index += 1

def handle_question(question: str, context: str):
    """טיפול בשאלה שנשאלה"""
    
    # Parse profession and category from context
    context_parts = context.split(" - ")
    profession = context_parts[0] if len(context_parts) > 0 else None
    category = context_parts[1] if len(context_parts) > 1 else None
    
    # Add to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": f"🔍 **{context}:** {question}"
    })
    
    start_time = time.time()
    
    if AI_ENABLED:
        # Use AI translation
        translator = get_ai_translator()
        if translator:
            try:
                with st.spinner("🤖 מתרגם שאלה..."):
                    result = translator.translate_query(question)
                    
                if isinstance(result, dict) and result.get('sql_query'):
                    sql_query = result['sql_query']
                    
                    # Execute the generated SQL
                    success, query_result = execute_query(sql_query)
                    execution_time = (time.time() - start_time) * 1000
                    
                    if success:
                        result_rows = len(query_result) if hasattr(query_result, '__len__') else None
                        
                        # Log successful query
                        log_user_question(
                            user_question=question,
                            profession=profession,
                            category=category,
                            query_type="ai_translation",
                            sql_query=sql_query,
                            success=True,
                            execution_time_ms=execution_time,
                            result_rows=result_rows,
                            ai_translation_used=True,
                            session_id=st.session_state.session_id
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "query_result",
                            "result_df": query_result,
                            "query": sql_query,
                            "query_title": question,
                            "query_description": f"תשובה עבור: {question}"
                        })
                    else:
                        # Log failed query
                        log_user_question(
                            user_question=question,
                            profession=profession,
                            category=category,
                            query_type="ai_translation",
                            sql_query=sql_query,
                            success=False,
                            execution_time_ms=(time.time() - start_time) * 1000,
                            error_message=str(query_result),
                            ai_translation_used=True,
                            session_id=st.session_state.session_id
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ שגיאה בהרצת השאילתה:\n```\n{query_result}\n```"
                        })
                else:
                    # Log failed translation
                    log_user_question(
                        user_question=question,
                        profession=profession,
                        category=category,
                        query_type="ai_translation",
                        success=False,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        error_message="Failed to translate question",
                        ai_translation_used=True,
                        session_id=st.session_state.session_id
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ לא הצלחתי לתרגם את השאלה: {question}"
                    })
                    
            except Exception as e:
                # Log exception
                log_user_question(
                    user_question=question,
                    profession=profession,
                    category=category,
                    query_type="ai_translation",
                    success=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error_message=str(e),
                    ai_translation_used=True,
                    session_id=st.session_state.session_id
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ שגיאה בתרגום: {str(e)}"
                })
        else:
            # Log AI not available
            log_user_question(
                user_question=question,
                profession=profession,
                category=category,
                query_type="ai_translation",
                success=False,
                execution_time_ms=(time.time() - start_time) * 1000,
                error_message="AI translator not available",
                ai_translation_used=False,
                session_id=st.session_state.session_id
            )
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ מתרגם ה-AI לא זמין"
            })
    else:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "⚠️ מתרגם ה-AI לא זמין. אנא השתמש בשאילתות SQL ידניות או הפעל את ה-AI."
        })
    
    st.rerun()

def render_chat_interface():
    """ממשק צ'אט חופשי"""
    
    st.markdown("### 💬 שאלה חופשית")
    st.caption("שאל כל שאלה על הפרויקט - המערכת תנסה לתרגם ולהריץ")
    
    # AI status
    if AI_ENABLED:
        st.success("🤖 **AI פעיל** - תרגום שאלות בשפה טבעית זמין!")
        st.info("💡 **דוגמאות:** 'מה שטח הרצפה?' | 'כמה חלונות יש?' | 'מה עלות הפרויקט?'")
    else:
        st.warning("⚠️ **AI לא זמין** - רק שאילתות SQL ידניות")
        with st.expander("💡 איך להפעיל AI?"):
            st.markdown("""
            **להפעלת תרגום שאלות בשפה טבעית:**
            1. הוסף OpenAI API key לקובץ `.env`
            2. הפעל מחדש את האפליקציה
            3. שאל שאלות כמו: "כמה קירות יש בבניין?"
            """)
    
    # Chat interface
    render_chat_messages()
    render_chat_input()

def render_analytics_tab():
    """רינדור טאב Analytics"""
    
    st.markdown("### 📊 ניתוח שאלות משתמשים")
    
    # Check if logging is available
    if not LOGGING_ENABLED or query_logger is None:
        st.warning("📊 מערכת הלוגים לא זמינה - Analytics מושבת")
        st.info("💡 במצב Cloud, Analytics יהיה זמין רק עם קבצי לוג מקומיים")
        return
    
    # Quick stats for today
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    today_stats = query_logger.get_daily_stats(today)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 שאלות היום",
            today_stats.get("total_queries", 0)
        )
        
    with col2:
        success_count = today_stats.get("successful_queries", 0)
        total_count = today_stats.get("total_queries", 0)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        st.metric(
            "✅ אחוז הצלחה",
            f"{success_rate:.1f}%"
        )
        
    with col3:
        ai_count = today_stats.get("ai_translations", 0)
        ai_rate = (ai_count / total_count * 100) if total_count > 0 else 0
        st.metric(
            "🤖 שימוש ב-AI",
            f"{ai_rate:.1f}%"
        )
        
    with col4:
        avg_time = today_stats.get("avg_execution_time", 0)
        st.metric(
            "⏱️ זמן ממוצע",
            f"{avg_time:.0f}ms" if avg_time > 0 else "N/A"
        )
    
    st.divider()
    
    # Analytics options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 דוח מפורט (7 ימים)", use_container_width=True):
            report = query_logger.generate_analytics_report(7)
            st.text_area("📊 דוח Analytics", report, height=300)
    
    with col2:
        if st.button("💾 ייצוא נתונים", use_container_width=True):
            export_result = query_logger.export_data("json", 30)
            st.success(export_result)
    
    # Recent activity
    if today_stats.get("total_queries", 0) > 0:
        st.subheader("📝 פעילות אחרונה")
        
        recent_queries = query_logger.load_queries_by_date(today)
        recent_queries = sorted(recent_queries, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        
        for i, query in enumerate(recent_queries):
            with st.expander(f"🕐 {query.get('timestamp', '')[:19]} - {query.get('user_question', '')[:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**שאלה:** {query.get('user_question', '')}")
                    st.write(f"**מקצוע:** {query.get('profession', 'לא מוגדר')}")
                    st.write(f"**קטגוריה:** {query.get('category', 'לא מוגדר')}")
                    
                with col2:
                    status = "✅ הצליח" if query.get('success') else "❌ נכשל"
                    st.write(f"**סטטוס:** {status}")
                    st.write(f"**סוג:** {query.get('query_type', 'לא מוגדר')}")
                    st.write(f"**AI:** {'כן' if query.get('ai_translation_used') else 'לא'}")
                    
                    if query.get('execution_time_ms'):
                        st.write(f"**זמן ביצוע:** {query.get('execution_time_ms'):.0f}ms")
                
                if query.get('error_message'):
                    st.error(f"**שגיאה:** {query.get('error_message')}")
    else:
        st.info("📝 אין שאלות היום עדיין")
    
    # Link to full analytics dashboard
    st.divider()
    st.markdown("""
    ### 🚀 דשבורד מפורט
    
    להרצת דשבורד Analytics מפורט עם charts ו-visualizations:
    
    ```bash
    streamlit run analytics_dashboard.py --server.port 8503
    ```
    
    הדשבורד יפעל בכתובת: http://localhost:8503
    """)

if __name__ == "__main__":
    main()