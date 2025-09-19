#!/usr/bin/env python3
"""
5 שאילתות פרקטיות ופועלות על מסד נתונים IFC
"""

import duckdb

def run_query_safe(conn, query, title, description):
    """הרצת שאילתה בטוחה עם הסבר"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"📖 {description}")
    print(f"📝 SQL:")
    print(f"    {query}")
    print("📊 תוצאות:")
    
    try:
        results = conn.execute(query).fetchall()
        if results:
            for i, row in enumerate(results, 1):
                print(f"   {i}. {row}")
                if i >= 15:  # הגבל ל-15 תוצאות
                    print(f"   ... (עוד {len(results)-15} תוצאות)")
                    break
        else:
            print("   אין תוצאות")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print("🏗️ 5 שאילתות פרקטיות על פרויקט ה-IFC")
    print("🏠 פרויקט: Guy Mador - Shiba V.3.0")
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # שאילתה 1: מה הם הסוגים השונים של צנרת במערכות?
        run_query_safe(conn, 
            """SELECT 
                Name as pipe_type,
                Description,
                COUNT(*) as count
            FROM ifcpipefittingtype 
            GROUP BY Name, Description
            ORDER BY count DESC""",
            "שאילתה 1: סוגי חיבורי הצנרת במערכות MEP",
            "מציגה את כל סוגי חיבורי הצנרת והכמות של כל סוג")
        
        # שאילתה 2: איזה Property Sets הכי נפוצים?
        run_query_safe(conn, 
            """SELECT 
                pset_name as property_set_name,
                COUNT(*) as properties_count,
                COUNT(DISTINCT ifc_id) as elements_with_this_pset
            FROM psets 
            GROUP BY pset_name
            ORDER BY properties_count DESC
            LIMIT 10""",
            "שאילתה 2: Property Sets הנפוצים ביותר",
            "מראה איזה קבוצות תכונות הכי שכיחות בפרויקט")
        
        # שאילתה 3: איזה סוגי אלמנטים יש לנו ובאיזה כמויות?
        run_query_safe(conn, 
            """SELECT 
                ifc_class as element_type,
                COUNT(*) as quantity
            FROM id_map 
            WHERE ifc_class IN (
                'IfcWall', 'IfcWallStandardCase', 'IfcBeam', 'IfcColumn', 
                'IfcSlab', 'IfcDoor', 'IfcWindow', 'IfcCovering', 'IfcRoof'
            )
            GROUP BY ifc_class
            ORDER BY quantity DESC""",
            "שאילתה 3: אלמנטים קונסטרוקטיביים עיקריים",
            "ספירה של האלמנטים הקונסטרוקטיביים החשובים בפרויקט")
        
        # שאילתה 4: איזה חומרים יש בפרויקט?
        run_query_safe(conn, 
            """SELECT 
                Name as material_name,
                Description as material_description
            FROM ifcmaterial 
            WHERE Name IS NOT NULL
            ORDER BY Name""",
            "שאילתה 4: רשימת החומרים בפרויקט",
            "מציגה את כל החומרים הזמינים בפרויקט")
        
        # שאילתה 5: מידע על מערכות המבנה
        run_query_safe(conn, 
            """SELECT 
                'מערכות במבנה' as category,
                COUNT(*) as count
            FROM ifcsystem
            
            UNION ALL
            
            SELECT 
                'קטעי זרימה' as category,
                COUNT(*) as count
            FROM ifcflowsegment
            
            UNION ALL
            
            SELECT 
                'חיבורי זרימה' as category,
                COUNT(*) as count
            FROM ifcflowfitting
            
            UNION ALL
            
            SELECT 
                'בקרי זרימה' as category,
                COUNT(*) as count
            FROM ifcflowcontroller
            
            ORDER BY count DESC""",
            "שאילתה 5: סיכום מערכות MEP במבנה",
            "מראה את ההרכב של מערכות המכניות במבנה")
        
        print(f"\n{'='*60}")
        print("🔧 איך להריץ שאילתות משלך:")
        print("1. פתח Python:")
        print("   python")
        print("")
        print("2. התחבר למסד הנתונים:")
        print("   import duckdb")
        print("   conn = duckdb.connect('guy_mador_shiba.duckdb')")
        print("")
        print("3. דוגמאות לשאילתות:")
        print("   # כל הקירות")
        print("   conn.execute('SELECT * FROM ifcwall').fetchall()")
        print("")
        print("   # חיפוש Property Set ספציפי")
        print("   conn.execute(\"SELECT * FROM psets WHERE pset_name LIKE '%Beam%'\").fetchall()")
        print("")
        print("   # סך האלמנטים מסוג מסוים")
        print("   conn.execute('SELECT COUNT(*) FROM ifcbeam').fetchall()")
        print("")
        print("4. סגור את החיבור:")
        print("   conn.close()")
        
        print(f"\n💡 טיפים לשאילתות:")
        print("• השתמש ב-LIKE '%חיפוש%' לחיפוש חלקי")
        print("• השתמש ב-JOIN לחבר טבלאות")
        print("• השתמש ב-GROUP BY לסיכומים")
        print("• השתמש ב-ORDER BY למיון")
        print("• השתמש ב-LIMIT להגבלת תוצאות")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()