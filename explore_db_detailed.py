#!/usr/bin/env python3
"""
Script to explore the created DuckDB database with detailed queries
"""

import duckdb

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print(f"חוקר מסד נתונים: {db_path}")
    print("=" * 50)
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # בדיקת מבנה הגיאומטריה
        print("\n1. מבנה טבלת הגיאומטריה:")
        geometry_schema = conn.execute("DESCRIBE geometry").fetchall()
        for col in geometry_schema:
            print(f"   {col[0]}: {col[1]}")
        
        # נתוני גיאומטריה
        print("\n2. דוגמאות לנתוני גיאומטריה:")
        geometry_samples = conn.execute("SELECT id, material_ids FROM geometry LIMIT 5").fetchall()
        for row in geometry_samples:
            print(f"   ID: {row[0]}, חומרים: {row[1]}")
        
        # בדיקת מבנה property sets
        print("\n3. מבנה טבלת ה-Property Sets:")
        psets_schema = conn.execute("DESCRIBE psets").fetchall()
        for col in psets_schema:
            print(f"   {col[0]}: {col[1]}")
        
        # property sets
        print("\n4. דוגמאות ל-Property Sets:")
        psets_samples = conn.execute("SELECT ifc_id, name, properties FROM psets LIMIT 5").fetchall()
        for row in psets_samples:
            print(f"   IFC ID: {row[0]}, שם: {row[1]}")
            # print(f"      תכונות: {row[2][:100]}...")  # רק 100 תווים ראשונים
        
        # בדיקת קירות
        print("\n5. פרטי קירות:")
        walls = conn.execute("SELECT * FROM ifcwall LIMIT 3").fetchall()
        wall_columns = conn.execute("DESCRIBE ifcwall").fetchall()
        print(f"   עמודות בטבלת קירות: {[col[0] for col in wall_columns]}")
        
        # בדיקת קורות
        print("\n6. פרטי קורות:")
        beams = conn.execute("SELECT * FROM ifcbeam LIMIT 3").fetchall()
        beam_columns = conn.execute("DESCRIBE ifcbeam").fetchall()
        print(f"   עמודות בטבלת קורות: {[col[0] for col in beam_columns]}")
        
        # חיפוש אובייקטים עם שמות
        print("\n7. אובייקטים עם שמות:")
        named_objects = conn.execute("""
            SELECT im.ifc_class, COUNT(*) as count
            FROM id_map im
            WHERE im.ifc_class IN ('IfcWall', 'IfcDoor', 'IfcWindow', 'IfcBeam', 'IfcColumn', 'IfcSlab')
            GROUP BY im.ifc_class
            ORDER BY count DESC
        """).fetchall()
        
        for obj_type, count in named_objects:
            print(f"   {obj_type}: {count}")
        
        # סטטיסטיקות על הבניין
        print("\n8. מידע על הבניין:")
        building_info = conn.execute("SELECT * FROM ifcbuilding").fetchall()
        if building_info:
            building_cols = conn.execute("DESCRIBE ifcbuilding").fetchall()
            print(f"   עמודות: {[col[0] for col in building_cols]}")
            print(f"   נתונים: {building_info[0][:5]}...")  # רק 5 עמודות ראשונות
        
        # קומות
        print("\n9. קומות בבניין:")
        storeys = conn.execute("SELECT * FROM ifcbuildingstorey").fetchall()
        print(f"   מספר קומות: {len(storeys)}")
        
        # מידע על חלונות ודלתות
        print("\n10. פתחים:")
        try:
            openings = conn.execute("SELECT COUNT(*) FROM ifcopeningelement").fetchone()[0]
            print(f"   פתחים: {openings}")
        except:
            print("   אין נתונים על פתחים")
            
        # מידע על מערכות
        print("\n11. מערכות בבניין:")
        systems = conn.execute("SELECT COUNT(*) FROM ifcsystem").fetchone()[0]
        print(f"   מספר מערכות: {systems}")
        
    except Exception as e:
        print(f"שגיאה בחקירת מסד הנתונים: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()