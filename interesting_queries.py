#!/usr/bin/env python3
"""
5 שאילתות מעניינות על מסד נתונים IFC
"""

import duckdb

def run_interesting_query(conn, query, title, description):
    """הרצת שאילתה מעניינת עם הסבר"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"📖 {description}")
    print(f"📝 SQL: {query}")
    print("📊 תוצאות:")
    
    try:
        results = conn.execute(query).fetchall()
        if results:
            for i, row in enumerate(results, 1):
                print(f"   {i}. {row}")
                if i >= 10:  # הגבל ל-10 תוצאות
                    print(f"   ... (עוד {len(results)-10} תוצאות)")
                    break
        else:
            print("   אין תוצאות")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print("🏗️ 5 שאילתות מעניינות על פרויקט ה-IFC")
    print("🏠 פרויקט: Guy Mador - Shiba V.3.0")
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # שאילתה 1: איזה קומות יש בבניין ומה יש בכל קומה?
        run_interesting_query(conn, 
            """SELECT 
                bs.*, 
                COUNT(rel.RelatedObjects) as elements_count
            FROM ifcbuildingstorey bs
            LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
            GROUP BY bs.ifc_id
            ORDER BY bs.Name""",
            "שאילתה 1: קומות הבניין ומספר האלמנטים בכל קומה",
            "מציגה את הקומות השונות בבניין וכמה אלמנטים יש בכל קומה")
        
        # שאילתה 2: איזה סוגי צנרת יש במערכות?
        run_interesting_query(conn, 
            """SELECT 
                pft.Name as pipe_fitting_type,
                COUNT(*) as count
            FROM ifcpipefittingtype pft
            GROUP BY pft.Name
            ORDER BY count DESC""",
            "שאילתה 2: סוגי חיבורי הצנרת במערכות",
            "מראה איזה סוגי חיבורים ואביזרי צנרת יש במערכות המכניות")
        
        # שאילתה 3: איזה Property Sets מכילים מידע על ממדים?
        run_interesting_query(conn, 
            """SELECT 
                pset_name,
                name as property_name,
                COUNT(*) as usage_count
            FROM psets 
            WHERE name LIKE '%Length%' 
               OR name LIKE '%Width%' 
               OR name LIKE '%Height%'
               OR name LIKE '%Area%'
               OR name LIKE '%Volume%'
            GROUP BY pset_name, name
            ORDER BY usage_count DESC""",
            "שאילתה 3: תכונות הקשורות לממדים",
            "מוצאת כל התכונות הקשורות לממדים (אורך, רוחב, גובה, שטח, נפח)")
        
        # שאילתה 4: איזה חומרים הכי נפוצים בפרויקט?
        run_interesting_query(conn, 
            """SELECT 
                m.Name as material_name,
                COUNT(ram.RelatedObjects) as usage_count
            FROM ifcmaterial m
            LEFT JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
            GROUP BY m.ifc_id, m.Name
            ORDER BY usage_count DESC""",
            "שאילתה 4: החומרים הנפוצים ביותר בפרויקט",
            "מציגה איזה חומרים נמצאים בשימוש הרב ביותר")
        
        # שאילתה 5: איזה אלמנטים קשורים לפתחים (דלתות וחלונות)?
        run_interesting_query(conn, 
            """SELECT 
                'דלת' as opening_type,
                d.Name as element_name,
                oe.Name as opening_name
            FROM ifcdoor d
            LEFT JOIN ifcrelvoidselement rve ON d.ifc_id = rve.RelatedBuildingElement
            LEFT JOIN ifcopeningelement oe ON rve.RelatingOpeningElement = oe.ifc_id
            WHERE d.Name IS NOT NULL
            
            UNION ALL
            
            SELECT 
                'חלון' as opening_type,
                w.Name as element_name,
                oe.Name as opening_name
            FROM ifcwindow w
            LEFT JOIN ifcrelvoidselement rve ON w.ifc_id = rve.RelatedBuildingElement
            LEFT JOIN ifcopeningelement oe ON rve.RelatingOpeningElement = oe.ifc_id
            WHERE w.Name IS NOT NULL
            
            ORDER BY opening_type, element_name""",
            "שאילתה 5: דלתות וחלונות והפתחים הקשורים אליהם",
            "מציגה את הקשר בין דלתות/חלונות לפתחים שלהם בקירות")
        
        print(f"\n{'='*60}")
        print("🎓 רעיונות לשאילתות נוספות:")
        print("• חיפוש אלמנטים לפי סוג חומר")
        print("• מציאת אלמנטים בקומה מסוימת")
        print("• חישוב סך השטחים/נפחים")
        print("• ניתוח מערכות MEP (מכניות/חשמליות/אינסטלציה)")
        print("• בדיקת קשרים בין אלמנטים שונים")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()