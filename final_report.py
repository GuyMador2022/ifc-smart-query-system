#!/usr/bin/env python3
"""
Final exploration script for the IFC to DuckDB conversion
"""

import duckdb
import json

def main():
    db_path = "guy_mador_shiba.duckdb"
    
    print(f"🏗️  דוח סופי על המרת קובץ IFC למסד נתונים DuckDB")
    print("=" * 60)
    
    # התחברות למסד הנתונים
    conn = duckdb.connect(db_path)
    
    try:
        # 1. מידע כללי על הפרויקט
        print("\n📋 1. מידע כללי על הפרויקט:")
        metadata = conn.execute("SELECT * FROM metadata").fetchall()
        for row in metadata:
            print(f"   🔧 Preprocessor: {row[0]}")
            print(f"   📐 Schema: {row[1]}")
            print(f"   📖 MVD: {row[2]}")
        
        # 2. סטטיסטיקות כלליות
        print("\n📊 2. סטטיסטיקות כלליות:")
        total_entities = conn.execute("SELECT COUNT(*) FROM id_map").fetchone()[0]
        print(f"   📦 סך הכל entities: {total_entities:,}")
        
        total_tables = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'main'").fetchone()[0]
        print(f"   🗂️  סך הכל טבלאות: {total_tables}")
        
        # 3. אלמנטים עיקריים בבניין
        print("\n🏢 3. אלמנטים עיקריים בבניין:")
        building_elements = {
            'IfcWall': 'קירות',
            'IfcWallStandardCase': 'קירות סטנדרטיים', 
            'IfcBeam': 'קורות',
            'IfcColumn': 'עמודים',
            'IfcSlab': 'רצפות/תקרות',
            'IfcDoor': 'דלתות',
            'IfcWindow': 'חלונות',
            'IfcCovering': 'חיפויים',
            'IfcRoof': 'גגות',
            'IfcBuildingElementProxy': 'אלמנטים כלליים'
        }
        
        for ifc_type, hebrew_name in building_elements.items():
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM id_map WHERE ifc_class = '{ifc_type}'").fetchone()[0]
                if count > 0:
                    print(f"   🧱 {hebrew_name}: {count}")
            except:
                pass
        
        # 4. מערכות במבנה
        print("\n⚙️  4. מערכות במבנה:")
        systems_count = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcSystem'").fetchone()[0]
        print(f"   🔧 מערכות: {systems_count}")
        
        mep_elements = {
            'IfcFlowSegment': 'קטעי זרימה',
            'IfcFlowFitting': 'חיבורי זרימה', 
            'IfcFlowController': 'בקרי זרימה',
            'IfcFlowTerminal': 'סופי זרימה',
            'IfcDistributionPort': 'יציאות חלוקה'
        }
        
        for ifc_type, hebrew_name in mep_elements.items():
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM id_map WHERE ifc_class = '{ifc_type}'").fetchone()[0]
                if count > 0:
                    print(f"   🔧 {hebrew_name}: {count}")
            except:
                pass
        
        # 5. נתוני גיאומטריה
        print("\n🎨 5. נתוני גיאומטריה:")
        geometry_count = conn.execute("SELECT COUNT(*) FROM geometry").fetchone()[0]
        print(f"   🎯 אובייקטים עם גיאומטריה: {geometry_count}")
        
        shape_count = conn.execute("SELECT COUNT(*) FROM shape").fetchone()[0]
        print(f"   📐 צורות גיאומטריות: {shape_count}")
        
        # 6. Property Sets
        print("\n📝 6. Property Sets:")
        psets_count = conn.execute("SELECT COUNT(*) FROM psets").fetchone()[0]
        print(f"   📊 סך הכל Property Sets: {psets_count}")
        
        # Property Sets השכיחים ביותר
        common_psets = conn.execute("""
            SELECT pset_name, COUNT(*) as count 
            FROM psets 
            GROUP BY pset_name 
            ORDER BY count DESC 
            LIMIT 5
        """).fetchall()
        
        print("   📋 Property Sets השכיחים:")
        for pset_name, count in common_psets:
            print(f"     - {pset_name}: {count}")
        
        # 7. מבנה המבנה
        print("\n🏗️  7. מבנה המבנה:")
        try:
            building_count = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcBuilding'").fetchone()[0]
            storey_count = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcBuildingStorey'").fetchone()[0]
            site_count = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcSite'").fetchone()[0]
            
            print(f"   🌍 אתרים: {site_count}")
            print(f"   🏢 בניינים: {building_count}")
            print(f"   🏠 קומות: {storey_count}")
        except Exception as e:
            print(f"   ❌ שגיאה בקריאת מבנה המבנה: {e}")
        
        # 8. חומרים
        print("\n🎨 8. חומרים:")
        try:
            materials_count = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcMaterial'").fetchone()[0]
            material_layers = conn.execute("SELECT COUNT(*) FROM id_map WHERE ifc_class = 'IfcMaterialLayer'").fetchone()[0]
            
            print(f"   🎯 חומרים בסיסיים: {materials_count}")
            print(f"   📚 שכבות חומר: {material_layers}")
        except:
            print("   ❌ אין מידע על חומרים")
        
        # 9. דוגמאות לשאילתות שימושיות
        print("\n💡 9. דוגמאות לשאילתות שימושיות:")
        print("   📝 כדי לבצע שאילתות על מסד הנתונים, השתמש ב:")
        print("   🔍 SELECT * FROM ifcwall; -- לראות את כל הקירות")
        print("   🔍 SELECT * FROM psets WHERE pset_name LIKE '%Dimensions%'; -- למצוא ממדים")
        print("   🔍 SELECT ifc_class, COUNT(*) FROM id_map GROUP BY ifc_class; -- סטטיסטיקות")
        
        # 10. סיכום
        print(f"\n✅ 10. סיכום:")
        print(f"   🎯 הקובץ IFC הומר בהצלחה למסד נתונים DuckDB")
        print(f"   📁 שם הקובץ: {db_path}")
        print(f"   📦 {total_entities:,} entities נטענו למסד הנתונים")
        print(f"   🗂️  {total_tables} טבלאות נוצרו")
        print(f"   🎨 {geometry_count} אובייקטים עם נתוני גיאומטריה")
        print(f"   📝 {psets_count} Property Sets")
        
        print(f"\n🚀 מסד הנתונים מוכן לשימוש ולשאילתות!")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()