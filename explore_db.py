#!/usr/bin/env python3
"""
Script to explore the created DuckDB database
"""

import duckdb

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print(f"חוקר מסד נתונים: {db_path}")
    print("=" * 50)
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # רשימת טבלאות
        print("\n1. רשימת טבלאות במסד הנתונים:")
        tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # מטאדאטה
        print("\n2. מטאדאטה של הפרויקט:")
        metadata = conn.execute("SELECT * FROM metadata").fetchall()
        for row in metadata:
            print(f"   Preprocessor: {row[0]}")
            print(f"   Schema: {row[1]}")
            print(f"   MVD: {row[2]}")
        
        # סטטיסטיקות כלליות
        print("\n3. סטטיסטיקות כלליות:")
        total_entities = conn.execute("SELECT COUNT(*) FROM id_map").fetchone()[0]
        print(f"   סך הכל entities: {total_entities}")
        
        # רשימת סוגי entities
        print("\n4. סוגי IFC entities בפרויקט:")
        entity_types = conn.execute("SELECT ifc_class, COUNT(*) as count FROM id_map GROUP BY ifc_class ORDER BY count DESC").fetchall()
        for entity_type, count in entity_types:
            print(f"   {entity_type}: {count}")
        
        # בדיקה אם יש נתוני גיאומטריה
        try:
            geometry_count = conn.execute("SELECT COUNT(*) FROM geometry").fetchone()[0]
            print(f"\n5. נתוני גיאומטריה:")
            print(f"   סך הכל אובייקטים עם גיאומטריה: {geometry_count}")
            
            if geometry_count > 0:
                # דוגמאות לאובייקטים עם גיאומטריה
                geometry_samples = conn.execute("SELECT ifc_id, color FROM geometry LIMIT 5").fetchall()
                print("   דוגמאות לאובייקטים עם גיאומטריה:")
                for ifc_id, color in geometry_samples:
                    print(f"     IFC ID: {ifc_id}, צבע: {color}")
        except Exception as e:
            print(f"\n5. נתוני גיאומטריה: לא זמינים ({e})")
        
        # בדיקה אם יש property sets
        try:
            pset_count = conn.execute("SELECT COUNT(*) FROM pset").fetchone()[0]
            print(f"\n6. Property Sets:")
            print(f"   סך הכל property sets: {pset_count}")
            
            if pset_count > 0:
                # דוגמאות לproperty sets
                pset_samples = conn.execute("SELECT DISTINCT pset_name FROM pset LIMIT 10").fetchall()
                print("   שמות Property Sets:")
                for pset_name, in pset_samples:
                    print(f"     - {pset_name}")
        except Exception as e:
            print(f"\n6. Property Sets: לא זמינים ({e})")
        
        # בדיקה אם יש טבלאות ספציפיות
        print("\n7. טבלאות עיקריות (דוגמאות):")
        common_tables = ['ifcwall', 'ifcwindow', 'ifcdoor', 'ifcspace', 'ifcbuilding', 'ifcslab', 'ifcbeam', 'ifccolumn']
        
        for table_name in common_tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                if count > 0:
                    print(f"   {table_name}: {count} אובייקטים")
            except:
                pass  # הטבלה לא קיימת
                
    except Exception as e:
        print(f"שגיאה בחקירת מסד הנתונים: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()