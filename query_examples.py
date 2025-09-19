#!/usr/bin/env python3
"""
דוגמאות לשאילתות על מסד נתונים IFC-DuckDB
"""

import duckdb

def run_query(conn, query, description):
    """הרצת שאילתה עם תיאור"""
    print(f"\n🔍 {description}")
    print(f"📝 שאילתה: {query}")
    print("📊 תוצאות:")
    
    try:
        results = conn.execute(query).fetchall()
        if results:
            for row in results:
                print(f"   {row}")
        else:
            print("   אין תוצאות")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print("🏗️ שאילתות על מסד נתונים IFC")
    print("=" * 50)
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # שאילתה 1: כמה קירות יש בפרויקט?
        run_query(conn, 
                 "SELECT COUNT(*) as total_walls FROM ifcwall", 
                 "שאילתה 1: כמה קירות יש בפרויקט?")
        
        # שאילתה 2: מהם סוגי האלמנטים השכיחים ביותר?
        run_query(conn, 
                 """SELECT ifc_class, COUNT(*) as count 
                    FROM id_map 
                    WHERE ifc_class LIKE 'Ifc%' 
                    GROUP BY ifc_class 
                    ORDER BY count DESC 
                    LIMIT 10""", 
                 "שאילתה 2: 10 סוגי האלמנטים השכיחים ביותר")
        
        # שאילתה 3: אילו Property Sets קשורים לקורות?
        run_query(conn, 
                 """SELECT DISTINCT pset_name, COUNT(*) as count
                    FROM psets p
                    JOIN id_map im ON p.ifc_id = im.ifc_id
                    WHERE im.ifc_class = 'IfcBeam'
                    GROUP BY pset_name
                    ORDER BY count DESC""", 
                 "שאילתה 3: Property Sets הקשורים לקורות")
        
        # שאילתה 4: מהן המערכות במבנה?
        run_query(conn, 
                 """SELECT COUNT(*) as system_count
                    FROM ifcsystem""", 
                 "שאילתה 4: כמה מערכות יש במבנה?")
        
        # שאילתה 5: אילו חומרים משמשים בפרויקט?
        run_query(conn, 
                 """SELECT COUNT(*) as material_count
                    FROM ifcmaterial""", 
                 "שאילתה 5: כמה חומרים שונים יש בפרויקט?")
        
        # שאילתה מתקדמת: פירוט האלמנטים הקונסטרוקטיביים
        run_query(conn, 
                 """SELECT 
                        'קירות' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class IN ('IfcWall', 'IfcWallStandardCase')
                    UNION ALL
                    SELECT 
                        'קורות' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class = 'IfcBeam'
                    UNION ALL
                    SELECT 
                        'עמודים' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class = 'IfcColumn'
                    UNION ALL
                    SELECT 
                        'רצפות/תקרות' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class = 'IfcSlab'
                    UNION ALL
                    SELECT 
                        'דלתות' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class = 'IfcDoor'
                    UNION ALL
                    SELECT 
                        'חלונות' as element_type, COUNT(*) as count
                    FROM id_map WHERE ifc_class = 'IfcWindow'
                    ORDER BY count DESC""", 
                 "שאילתה בונוס: סיכום אלמנטים קונסטרוקטיביים")
        
        print("\n" + "="*60)
        print("💡 איך להריץ שאילתות בעצמך:")
        print("1. התחבר למסד הנתונים:")
        print("   import duckdb")
        print("   conn = duckdb.connect('guy_mador_shiba.duckdb')")
        print("   ")
        print("2. הרץ שאילתה:")
        print("   results = conn.execute('SELECT * FROM ifcwall').fetchall()")
        print("   ")
        print("3. סגור את החיבור:")
        print("   conn.close()")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()