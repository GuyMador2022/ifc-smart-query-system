#!/usr/bin/env python3
"""
🤖 AI Query Translator
מתרגם שאלות בשפה טבעית לשאילתות SQL עבור מסד נתונים IFC
"""

import os
import openai
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import duckdb
import logging

# Load environment variables
load_dotenv()

class IFCQueryTranslator:
    """מתרגם שאלות בשפה טבעית לשאילתות SQL עבור IFC database"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 1000))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.1))
        
        # Get database schema for context
        self.schema_info = self._get_database_schema()
        
    def _get_database_schema(self) -> str:
        """מקבל מידע על סכמת מסד הנתונים"""
        try:
            conn = duckdb.connect(self.database_path)
            
            # Get table names and sample columns
            tables = conn.execute("SHOW TABLES").fetchall()
            schema_info = "DATABASE SCHEMA INFORMATION:\\n\\n"
            
            for table in tables[:20]:  # Limit to first 20 tables
                table_name = table[0]
                try:
                    # Get column info
                    columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
                    schema_info += f"Table: {table_name}\\n"
                    schema_info += "Columns: " + ", ".join([f"{col[0]} ({col[1]})" for col in columns[:10]]) + "\\n\\n"
                except:
                    continue
                    
            conn.close()
            return schema_info
            
        except Exception as e:
            logging.error(f"Error getting schema: {e}")
            return "Database schema not available"
    
    def translate_query(self, natural_question: str) -> Dict[str, Any]:
        """
        מתרגם שאלה בשפה טבעית לשאילתת SQL
        
        Args:
            natural_question: השאלה בשפה טבעית
            
        Returns:
            Dict עם sql_query, confidence, explanation
        """
        
        # Pre-process common patterns
        preprocessed = self._preprocess_common_patterns(natural_question)
        if preprocessed:
            return preprocessed
        
        # Create context-aware prompt
        system_prompt = f"""You are an expert SQL translator for IFC (Industry Foundation Classes) building data.
        
CONTEXT:
{self.schema_info}

INSTRUCTIONS:
1. Convert natural language questions about building/construction data to SQL queries
2. Focus on IFC-related entities like walls, doors, windows, spaces, materials, etc.
3. Use proper DuckDB syntax
4. Only use SELECT statements (no INSERT/UPDATE/DELETE)
5. Return only valid, executable SQL
6. Handle both Hebrew and English questions
7. If question is unclear, make reasonable assumptions about IFC data

IMPORTANT IFC CONCEPTS:
- IfcWall, IfcDoor, IfcWindow, IfcSpace, IfcSlab, IfcColumn, IfcBeam
- Properties like height, width, area, volume, material
- Spatial relationships and building hierarchy
- Quantities and measurements

COMMON QUERIES EXAMPLES:
- Floor area / שטח רצפה: "SELECT SUM(CAST(value AS DECIMAL)) FROM psets WHERE name LIKE '%Area%' OR name LIKE '%שטח%'"
- Wall count / ספירת קירות: "SELECT COUNT(*) FROM ifcwall"
- Material list / רשימת חומרים: "SELECT DISTINCT Name FROM ifcmaterial"
- Space areas / שטחי חללים: "SELECT Name, area FROM ifcspace WHERE area IS NOT NULL"

HEBREW TRANSLATIONS:
- שטח רצפה = floor area
- קירות = walls  
- דלתות = doors
- חלונות = windows
- חומרים = materials
- גובה = height
- רוחב = width
- נפח = volume

RESPONSE FORMAT:
Return only the SQL query, no explanations or markdown."""

        user_prompt = f"""Question: {natural_question}

Convert this to a SQL query for the IFC database."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # Validate the query
            confidence = self._validate_sql(sql_query)
            
            return {
                'sql_query': sql_query,
                'confidence': confidence,
                'explanation': f"Translated: '{natural_question}' to SQL",
                'model_used': self.model
            }
            
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return {
                'sql_query': None,
                'confidence': 0.0,
                'explanation': f"Translation failed: {str(e)}",
                'error': str(e)
            }
    
    def _preprocess_common_patterns(self, question: str) -> Dict[str, Any]:
        """טיפול בדפוסים נפוצים לפני שליחה ל-AI"""
        question_lower = question.lower()
        
        # Floor area patterns / שטח רצפה
        if any(term in question_lower for term in ['שטח רצפה', 'שטח הרצפה', 'floor area', 'total area']):
            sql_query = """SELECT 
                ROUND(SUM(CAST(JSON_EXTRACT(NominalValue, '$.value') AS DECIMAL)), 2) as total_area_sqm
            FROM IfcPropertySingleValue 
            WHERE Name IN ('TotalArea', 'ProjectedArea', 'Area')
            AND NominalValue IS NOT NULL"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.9,
                'explanation': 'Pre-processed pattern: Floor area calculation from IFC properties',
                'model_used': 'pattern_matching'
            }
        
        # Wall count patterns / ספירת קירות
        if any(term in question_lower for term in ['כמה קירות', 'ספירת קירות', 'how many walls', 'wall count']):
            sql_query = "SELECT COUNT(*) as wall_count FROM IfcWall"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Wall count',
                'model_used': 'pattern_matching'
            }
        
        # Material list patterns / רשימת חומרים
        if any(term in question_lower for term in ['איזה חומרים', 'רשימת חומרים', 'what materials', 'materials used']):
            sql_query = "SELECT DISTINCT Name as material_name FROM IfcMaterial WHERE Name IS NOT NULL ORDER BY Name"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Materials list',
                'model_used': 'pattern_matching'
            }
        
        # Space areas / שטחי חללים
        if any(term in question_lower for term in ['שטח חללים', 'שטחי חללים', 'space areas', 'room areas']):
            sql_query = """SELECT 
                s.Name as space_name,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as area_sqm
            FROM IfcSpace s
            LEFT JOIN IfcPropertySingleValue p ON p.Name = 'Area'
            WHERE s.Name IS NOT NULL
            AND p.NominalValue IS NOT NULL
            ORDER BY area_sqm DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.9,
                'explanation': 'Pre-processed pattern: Space areas',
                'model_used': 'pattern_matching'
            }
        
        # Building height / גובה הבניין
        if any(term in question_lower for term in ['גובה בניין', 'גובה הבניין', 'building height', 'total height']):
            sql_query = """SELECT 
                Name as building_name,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as height_m
            FROM IfcBuilding b
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Height%'
            WHERE b.Name IS NOT NULL
            LIMIT 1"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Building height',
                'model_used': 'pattern_matching'
            }
        
        # Number of floors / מספר קומות
        if any(term in question_lower for term in ['כמה קומות', 'מספר קומות', 'how many floors', 'number of floors', 'storeys']):
            sql_query = "SELECT COUNT(*) as floor_count FROM IfcBuildingStorey WHERE Name IS NOT NULL"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Number of floors',
                'model_used': 'pattern_matching'
            }
        
        # Doors count / מספר דלתות
        if any(term in question_lower for term in ['כמה דלתות', 'מספר דלתות', 'how many doors', 'door count']):
            sql_query = "SELECT COUNT(*) as door_count FROM IfcDoor"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Door count',
                'model_used': 'pattern_matching'
            }
        
        # Windows count / מספר חלונות
        if any(term in question_lower for term in ['כמה חלונות', 'מספר חלונות', 'how many windows', 'window count']):
            sql_query = "SELECT COUNT(*) as window_count FROM IfcWindow"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Window count',
                'model_used': 'pattern_matching'
            }
        
        # Beams count / מספר קורות
        if any(term in question_lower for term in ['כמה קורות', 'מספר קורות', 'how many beams', 'beam count']):
            sql_query = "SELECT COUNT(*) as beam_count FROM IfcBeam"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Beam count',
                'model_used': 'pattern_matching'
            }
        
        # Columns count / מספר עמודים
        if any(term in question_lower for term in ['כמה עמודים', 'מספר עמודים', 'how many columns', 'column count']):
            sql_query = "SELECT COUNT(*) as column_count FROM IfcColumn"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Column count',
                'model_used': 'pattern_matching'
            }
        
        # Slabs count / מספר לוחות
        if any(term in question_lower for term in ['כמה לוחות', 'כמה רצפות', 'מספר לוחות', 'how many slabs', 'slab count']):
            sql_query = "SELECT COUNT(*) as slab_count FROM IfcSlab"
            
            return {
                'sql_query': sql_query,
                'confidence': 0.95,
                'explanation': 'Pre-processed pattern: Slab count',
                'model_used': 'pattern_matching'
            }
        
        # Wall types / סוגי קירות
        if any(term in question_lower for term in ['סוגי קירות', 'טיפוסי קירות', 'wall types', 'types of walls']):
            sql_query = """SELECT 
                wt.Name as wall_type,
                COUNT(w.ifc_id) as count
            FROM IfcWallType wt
            LEFT JOIN IfcWall w ON w.ObjectType LIKE '%' || wt.Name || '%'
            WHERE wt.Name IS NOT NULL
            GROUP BY wt.Name
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Wall types',
                'model_used': 'pattern_matching'
            }
        
        # Volume calculation / חישוב נפח
        if any(term in question_lower for term in ['נפח כולל', 'נפח הכולל', 'הנפח הכולל', 'נפח הבניין', 'total volume', 'building volume']):
            sql_query = """SELECT 
                ROUND(SUM(CAST(JSON_EXTRACT(NominalValue, '$.value') AS DECIMAL)), 2) as total_volume_m3
            FROM IfcPropertySingleValue 
            WHERE Name LIKE '%Volume%'
            AND NominalValue IS NOT NULL"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Building volume',
                'model_used': 'pattern_matching'
            }
        
        # Floor/Storey information / מידע על קומות
        if any(term in question_lower for term in ['קומות', 'שמות קומות', 'floors', 'storeys', 'floor names']):
            sql_query = """SELECT 
                Name as floor_name,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as elevation
            FROM IfcBuildingStorey bs
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Elevation%'
            WHERE bs.Name IS NOT NULL
            ORDER BY elevation"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Floor information',
                'model_used': 'pattern_matching'
            }
        
        # Door types / סוגי דלתות
        if any(term in question_lower for term in ['סוגי דלתות', 'טיפוסי דלתות', 'door types', 'types of doors']):
            sql_query = """SELECT 
                dt.Name as door_type,
                COUNT(d.ifc_id) as count
            FROM IfcDoorType dt
            LEFT JOIN IfcDoor d ON d.ObjectType LIKE '%' || dt.Name || '%'
            WHERE dt.Name IS NOT NULL
            GROUP BY dt.Name
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Door types',
                'model_used': 'pattern_matching'
            }
        
        # Window types / סוגי חלונות
        if any(term in question_lower for term in ['סוגי חלונות', 'טיפוסי חלונות', 'window types', 'types of windows']):
            sql_query = """SELECT 
                wt.Name as window_type,
                COUNT(w.ifc_id) as count
            FROM IfcWindowType wt
            LEFT JOIN IfcWindow w ON w.ObjectType LIKE '%' || wt.Name || '%'
            WHERE wt.Name IS NOT NULL
            GROUP BY wt.Name
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Window types',
                'model_used': 'pattern_matching'
            }
        
        # Spaces by type / חללים לפי סוג
        if any(term in question_lower for term in ['חדרים', 'חללים', 'סוגי חדרים', 'rooms', 'spaces', 'room types']):
            sql_query = """SELECT 
                s.Name as space_name,
                s.ObjectType as space_type,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as area_sqm
            FROM IfcSpace s
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Area%'
            WHERE s.Name IS NOT NULL
            ORDER BY area_sqm DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Spaces by type',
                'model_used': 'pattern_matching'
            }
        
        # Largest room / החדר הגדול ביותר
        if any(term in question_lower for term in ['חדר הגדול', 'החדר הגדול ביותר', 'largest room', 'biggest room']):
            sql_query = """SELECT 
                s.Name as space_name,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as area_sqm
            FROM IfcSpace s
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Area%'
            WHERE s.Name IS NOT NULL
            AND p.NominalValue IS NOT NULL
            ORDER BY CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL) DESC
            LIMIT 1"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.9,
                'explanation': 'Pre-processed pattern: Largest room',
                'model_used': 'pattern_matching'
            }
        
        # Building elements summary / סיכום אלמנטים
        if any(term in question_lower for term in ['סיכום', 'כללי', 'summary', 'overview', 'total elements']):
            sql_query = """SELECT 
                'Walls' as element_type, COUNT(*) as count FROM IfcWall
            UNION ALL
            SELECT 'Doors' as element_type, COUNT(*) as count FROM IfcDoor  
            UNION ALL
            SELECT 'Windows' as element_type, COUNT(*) as count FROM IfcWindow
            UNION ALL
            SELECT 'Beams' as element_type, COUNT(*) as count FROM IfcBeam
            UNION ALL
            SELECT 'Columns' as element_type, COUNT(*) as count FROM IfcColumn
            UNION ALL
            SELECT 'Slabs' as element_type, COUNT(*) as count FROM IfcSlab
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.9,
                'explanation': 'Pre-processed pattern: Building elements summary',
                'model_used': 'pattern_matching'
            }
        
        # Material information / מידע על חומרים
        if any(term in question_lower for term in ['חומרים', 'סוגי חומרים', 'materials', 'material types']):
            sql_query = """SELECT DISTINCT 
                m.Name as material_name,
                m.Description as description
            FROM IfcMaterial m
            WHERE m.Name IS NOT NULL
            ORDER BY m.Name"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Material information',
                'model_used': 'pattern_matching'
            }
        
        # Building orientation / כיוון הבניין
        if any(term in question_lower for term in ['כיוון', 'אוריינטציה', 'orientation', 'direction', 'north']):
            sql_query = """SELECT 
                s.Name as site_name,
                JSON_EXTRACT(p.NominalValue, '$.value') as orientation
            FROM IfcSite s
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Orientation%' OR p.Name LIKE '%Direction%'
            WHERE s.Name IS NOT NULL"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Building orientation',
                'model_used': 'pattern_matching'
            }
        
        # Structural system / מערכת קונסטרוקטיבית
        if any(term in question_lower for term in ['קונסטרוקציה', 'מבנה', 'structural', 'structure', 'construction']):
            sql_query = """SELECT 
                'Columns' as element_type, COUNT(*) as count,
                GROUP_CONCAT(DISTINCT Name) as names
            FROM IfcColumn
            WHERE Name IS NOT NULL
            UNION ALL
            SELECT 
                'Beams' as element_type, COUNT(*) as count,
                GROUP_CONCAT(DISTINCT Name) as names
            FROM IfcBeam
            WHERE Name IS NOT NULL
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Structural system',
                'model_used': 'pattern_matching'
            }
        
        # Energy efficiency / יעילות אנרגטית
        if any(term in question_lower for term in ['אנרגיה', 'יעילות', 'energy', 'efficiency', 'thermal']):
            sql_query = """SELECT 
                p.Name as property_name,
                JSON_EXTRACT(p.NominalValue, '$.value') as value,
                p.Description
            FROM IfcPropertySingleValue p
            WHERE p.Name LIKE '%Energy%' 
            OR p.Name LIKE '%Thermal%'
            OR p.Name LIKE '%Insulation%'
            OR p.Name LIKE '%U-Value%'"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Energy efficiency',
                'model_used': 'pattern_matching'
            }
        
        # Building systems / מערכות הבניין
        if any(term in question_lower for term in ['מערכות', 'חשמל', 'אינסטלציה', 'systems', 'electrical', 'plumbing', 'hvac']):
            sql_query = """SELECT 
                ObjectType as system_type,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT Name) as components
            FROM (
                SELECT ObjectType, Name FROM IfcElectricalElement
                UNION ALL
                SELECT ObjectType, Name FROM IfcFlowTerminal
                UNION ALL
                SELECT ObjectType, Name FROM IfcDistributionElement
            ) systems
            WHERE ObjectType IS NOT NULL
            GROUP BY ObjectType
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Building systems',
                'model_used': 'pattern_matching'
            }
        
        # Fire safety / בטיחות אש
        if any(term in question_lower for term in ['בטיחות', 'כיבוי אש', 'fire', 'safety', 'emergency']):
            sql_query = """SELECT 
                Name as element_name,
                ObjectType as type,
                Description
            FROM (
                SELECT Name, ObjectType, Description FROM IfcFireSuppressionTerminal
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcAlarm
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcProtectiveDevice
            ) safety_elements
            WHERE Name IS NOT NULL"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Fire safety',
                'model_used': 'pattern_matching'
            }
        
        # Structural columns details / פרטי עמודים קונסטרוקטיביים
        if any(term in question_lower for term in ['עמודים נושאים', 'עמודים', 'קוטר עמודים', 'columns', 'structural columns', 'column diameter']):
            sql_query = """SELECT 
                c.Name as column_name,
                c.ObjectType as column_type,
                JSON_EXTRACT(p.NominalValue, '$.value') as diameter_or_dimension,
                p.Name as property_name
            FROM IfcColumn c
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Diameter%' OR p.Name LIKE '%Width%' OR p.Name LIKE '%Dimension%'
            WHERE c.Name IS NOT NULL
            ORDER BY CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL) DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Structural columns details',
                'model_used': 'pattern_matching'
            }
        
        # Beams details / פרטי קורות
        if any(term in question_lower for term in ['קורות ראשיות', 'קורות', 'מידות קורות', 'beams', 'main beams', 'beam dimensions']):
            sql_query = """SELECT 
                b.Name as beam_name,
                b.ObjectType as beam_type,
                JSON_EXTRACT(p.NominalValue, '$.value') as dimension,
                p.Name as property_name
            FROM IfcBeam b
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Height%' OR p.Name LIKE '%Width%' OR p.Name LIKE '%Length%'
            WHERE b.Name IS NOT NULL
            ORDER BY CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL) DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Beams details',
                'model_used': 'pattern_matching'
            }
        
        # Slab thickness / עובי תקרות
        if any(term in question_lower for term in ['עובי תקרות', 'תקרות', 'עובי', 'slab thickness', 'slabs', 'thickness']):
            sql_query = """SELECT 
                s.Name as slab_name,
                s.ObjectType as slab_type,
                ROUND(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL), 2) as thickness_mm
            FROM IfcSlab s
            LEFT JOIN IfcPropertySingleValue p ON p.Name LIKE '%Thickness%'
            WHERE s.Name IS NOT NULL
            AND p.NominalValue IS NOT NULL
            ORDER BY thickness_mm DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Slab thickness',
                'model_used': 'pattern_matching'
            }
        
        # HVAC systems / מערכות מיזוג
        if any(term in question_lower for term in ['מערכות hvac', 'מיזוג אוויר', 'יחידות מיזוג', 'hvac', 'air conditioning', 'ventilation']):
            sql_query = """SELECT 
                Name as equipment_name,
                ObjectType as equipment_type,
                Description
            FROM (
                SELECT Name, ObjectType, Description FROM IfcAirTerminal
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcEvaporator
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcCondenser
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcFan
            ) hvac_equipment
            WHERE Name IS NOT NULL
            ORDER BY equipment_type"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: HVAC systems',
                'model_used': 'pattern_matching'
            }
        
        # Electrical systems / מערכות חשמל
        if any(term in question_lower for term in ['לוחות חשמל', 'מערכות חשמל', 'electrical panels', 'electrical systems', 'power']):
            sql_query = """SELECT 
                Name as equipment_name,
                ObjectType as equipment_type,
                Description
            FROM (
                SELECT Name, ObjectType, Description FROM IfcElectricalElement
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcDistributionBoard
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcSwitchingDevice
            ) electrical_equipment
            WHERE Name IS NOT NULL
            ORDER BY equipment_type"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Electrical systems',
                'model_used': 'pattern_matching'
            }
        
        # Plumbing systems / מערכות אינסטלציה
        if any(term in question_lower for term in ['נקודות מים', 'אינסטלציה', 'צנרת', 'plumbing', 'water points', 'pipes']):
            sql_query = """SELECT 
                Name as equipment_name,
                ObjectType as equipment_type,
                Description
            FROM (
                SELECT Name, ObjectType, Description FROM IfcFlowTerminal
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcSanitaryTerminal
                UNION ALL
                SELECT Name, ObjectType, Description FROM IfcPipeSegment
            ) plumbing_equipment
            WHERE Name IS NOT NULL
            ORDER BY equipment_type"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Plumbing systems',
                'model_used': 'pattern_matching'
            }
        
        # Concrete volume / נפח בטון
        if any(term in question_lower for term in ['טון בטון', 'נפח בטון', 'concrete volume', 'concrete tons']):
            sql_query = """SELECT 
                'Total Concrete Volume' as material_type,
                ROUND(SUM(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL)), 2) as total_volume_m3,
                ROUND(SUM(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL)) * 2.4, 2) as estimated_tons
            FROM IfcPropertySingleValue p
            WHERE p.Name LIKE '%Volume%' 
            AND JSON_EXTRACT(p.NominalValue, '$.value') IS NOT NULL"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Concrete volume calculation',
                'model_used': 'pattern_matching'
            }
        
        # Steel elements / אלמנטי פלדה
        if any(term in question_lower for term in ['טון ברזל', 'פלדה', 'ברזל', 'steel', 'iron', 'steel tons']):
            sql_query = """SELECT 
                ObjectType as steel_element_type,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT Name) as element_names
            FROM (
                SELECT Name, ObjectType FROM IfcBeam WHERE ObjectType LIKE '%Steel%'
                UNION ALL
                SELECT Name, ObjectType FROM IfcColumn WHERE ObjectType LIKE '%Steel%'
                UNION ALL
                SELECT Name, ObjectType FROM IfcPlate WHERE ObjectType LIKE '%Steel%'
            ) steel_elements
            WHERE ObjectType IS NOT NULL
            GROUP BY ObjectType
            ORDER BY count DESC"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.8,
                'explanation': 'Pre-processed pattern: Steel elements',
                'model_used': 'pattern_matching'
            }
        
        # Project completion percentage / אחוז השלמה פרויקט
        if any(term in question_lower for term in ['אחוז השלמה', 'השלמה', 'כמה אחוז', 'completion percentage', 'project progress', 'progress']):
            sql_query = """SELECT 
                'Building Progress' as category,
                ROUND(
                    (SELECT COUNT(*) FROM (
                        SELECT 1 FROM IfcWall WHERE Name IS NOT NULL
                        UNION ALL
                        SELECT 1 FROM IfcDoor WHERE Name IS NOT NULL
                        UNION ALL
                        SELECT 1 FROM IfcWindow WHERE Name IS NOT NULL
                        UNION ALL
                        SELECT 1 FROM IfcSlab WHERE Name IS NOT NULL
                    )) * 100.0 / 
                    GREATEST((SELECT COUNT(*) FROM IfcBuildingStorey) * 50, 1), 1
                ) as estimated_completion_percentage
            FROM dual LIMIT 1"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.7,
                'explanation': 'Pre-processed pattern: Project completion percentage (estimated)',
                'model_used': 'pattern_matching'
            }
        
        # Project cost estimation / הערכת עלות פרויקט
        if any(term in question_lower for term in ['עלות פרויקט', 'כמה עולה', 'עלות בניה', 'project cost', 'total cost', 'cost estimation']):
            sql_query = """SELECT 
                'Cost Estimation' as category,
                ROUND(COUNT(*) * 1500, 0) as estimated_cost_nis,
                'Estimated based on element count' as note
            FROM (
                SELECT 1 FROM IfcWall
                UNION ALL
                SELECT 1 FROM IfcSlab
                UNION ALL
                SELECT 1 FROM IfcColumn
                UNION ALL
                SELECT 1 FROM IfcBeam
            ) all_elements"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.6,
                'explanation': 'Pre-processed pattern: Project cost estimation (rough)',
                'model_used': 'pattern_matching'
            }
        
        # Project size summary / סיכום גודל פרויקט - SPECIFIC FIRST
        if any(term in question_lower for term in ['גודל פרויקט', 'גודל הפרויקט', 'project size']):
            sql_query = """SELECT 
                'Total Floor Area (sqm)' as metric,
                ROUND(SUM(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL)), 1) as value
            FROM IfcPropertySingleValue p
            WHERE p.Name LIKE '%Area%' AND p.NominalValue IS NOT NULL
            UNION ALL
            SELECT 
                'Number of Floors' as metric,
                COUNT(*) as value
            FROM IfcBuildingStorey
            UNION ALL
            SELECT 
                'Total Elements' as metric,
                (SELECT COUNT(*) FROM IfcWall) + 
                (SELECT COUNT(*) FROM IfcDoor) + 
                (SELECT COUNT(*) FROM IfcWindow) as value"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Project size summary',
                'model_used': 'pattern_matching'
            }
            sql_query = """SELECT 
                'Total Floor Area (sqm)' as metric,
                ROUND(SUM(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL)), 1) as value
            FROM IfcPropertySingleValue p
            WHERE p.Name LIKE '%Area%' AND p.NominalValue IS NOT NULL
            UNION ALL
            SELECT 
                'Number of Floors' as metric,
                COUNT(*) as value
            FROM IfcBuildingStorey
            UNION ALL
            SELECT 
                'Total Elements' as metric,
                (SELECT COUNT(*) FROM IfcWall) + 
                (SELECT COUNT(*) FROM IfcDoor) + 
                (SELECT COUNT(*) FROM IfcWindow) as value"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.85,
                'explanation': 'Pre-processed pattern: Project size summary',
                'model_used': 'pattern_matching'
            }
        
        # Building stage / שלב בניה
        if any(term in question_lower for term in ['שלב בניה', 'איזה שלב', 'building stage', 'construction phase', 'current phase']):
            sql_query = """SELECT 
                'Construction Elements Status' as category,
                CASE 
                    WHEN wall_count > 0 AND slab_count > 0 THEN 'Structure Phase'
                    WHEN wall_count > 0 THEN 'Walls Phase'
                    ELSE 'Planning Phase'
                END as estimated_phase,
                wall_count,
                slab_count,
                door_count,
                window_count
            FROM (
                SELECT 
                    (SELECT COUNT(*) FROM IfcWall) as wall_count,
                    (SELECT COUNT(*) FROM IfcSlab) as slab_count,
                    (SELECT COUNT(*) FROM IfcDoor) as door_count,
                    (SELECT COUNT(*) FROM IfcWindow) as window_count
            )"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.7,
                'explanation': 'Pre-processed pattern: Building stage estimation',
                'model_used': 'pattern_matching'
            }
        
        # Quality issues / בעיות איכות
        if any(term in question_lower for term in ['בעיות איכות', 'ליקויים', 'quality issues', 'defects', 'problems']):
            sql_query = """SELECT 
                'Quality Check' as category,
                'No specific quality data in IFC model' as status,
                'Check physical inspections and reports' as recommendation
            FROM dual LIMIT 1"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.5,
                'explanation': 'Pre-processed pattern: Quality issues (limited IFC data)',
                'model_used': 'pattern_matching'
            }
        
        # Project timeline / לוחות זמנים
        if any(term in question_lower for term in ['לוחות זמנים', 'מתי יסתיים', 'timeline', 'schedule', 'completion date']):
            sql_query = """SELECT 
                'Project Timeline' as category,
                'Timeline data not available in IFC model' as status,
                'Check project management system' as recommendation,
                COUNT(*) as total_elements_to_complete
            FROM (
                SELECT 1 FROM IfcWall
                UNION ALL
                SELECT 1 FROM IfcDoor
                UNION ALL
                SELECT 1 FROM IfcWindow
                UNION ALL
                SELECT 1 FROM IfcSlab
            ) all_elements"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.5,
                'explanation': 'Pre-processed pattern: Project timeline (limited IFC data)',
                'model_used': 'pattern_matching'
            }
        
        # Cost per square meter / עלות למטר רבוע
        if any(term in question_lower for term in ['עלות למטר', 'מחיר למטר', 'cost per sqm', 'cost per square meter', 'price per square meter']):
            sql_query = """SELECT 
                'Cost per Square Meter' as metric,
                ROUND(
                    (COUNT(*) * 1500.0) / 
                    GREATEST(
                        (SELECT SUM(CAST(JSON_EXTRACT(p.NominalValue, '$.value') AS DECIMAL)) 
                         FROM IfcPropertySingleValue p 
                         WHERE p.Name LIKE '%Area%' AND p.NominalValue IS NOT NULL), 
                        100
                    ), 0
                ) as estimated_cost_per_sqm_nis
            FROM (
                SELECT 1 FROM IfcWall
                UNION ALL
                SELECT 1 FROM IfcSlab
                UNION ALL
                SELECT 1 FROM IfcColumn
            ) building_elements"""
            
            return {
                'sql_query': sql_query,
                'confidence': 0.6,
                'explanation': 'Pre-processed pattern: Cost per square meter estimation',
                'model_used': 'pattern_matching'
            }
            
        return None
    
    def _validate_sql(self, sql_query: str) -> float:
        """מאמת שאילתה ומחזיר ציון ביטחון"""
        try:
            # Basic SQL validation
            if not sql_query or not sql_query.strip():
                return 0.0
                
            # Check for dangerous operations
            dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
            sql_lower = sql_query.lower()
            
            for keyword in dangerous_keywords:
                if keyword in sql_lower:
                    return 0.0
            
            # Check if it's a SELECT query
            if not sql_lower.strip().startswith('select'):
                return 0.0
                
            # Try to execute the query to validate syntax
            conn = duckdb.connect(self.database_path)
            try:
                conn.execute(f"EXPLAIN {sql_query}")
                conn.close()
                return 0.9  # High confidence if query is valid
            except:
                conn.close()
                return 0.3  # Low confidence if query has syntax errors
                
        except Exception:
            return 0.0

    def interpret_results(self, question: str, sql_query: str, results_df, success: bool) -> str:
        """פרשנות חכמה של תוצאות השאילתה"""
        
        if not success or results_df is None or len(results_df) == 0:
            return "❌ לא הצלחתי למצוא תוצאות לשאלה זו."
        
        try:
            # Convert results to text summary
            num_rows = len(results_df)
            columns = list(results_df.columns)
            
            # Create context for AI interpretation
            results_summary = f"Query returned {num_rows} rows with columns: {', '.join(columns)}\\n"
            
            # Add sample data (first few rows)
            if num_rows > 0:
                results_summary += "Sample data:\\n"
                for i in range(min(5, num_rows)):
                    row_data = []
                    for col in columns:
                        value = results_df.iloc[i][col]
                        row_data.append(f"{col}: {value}")
                    results_summary += f"Row {i+1}: {', '.join(row_data)}\\n"
            
            # Send to AI for interpretation
            system_prompt = """You are an expert building information modeling (BIM) analyst. 
You help interpret IFC database query results in a clear, professional manner.

GUIDELINES:
- Provide clear, actionable insights in Hebrew
- Include relevant numbers and measurements
- Explain what the results mean in practical building/construction context
- Be concise but informative
- Use appropriate building/construction terminology
- Include recommendations or next steps when relevant

RESPONSE LANGUAGE: Hebrew (עברית)
TONE: Professional, helpful, expert"""

            user_prompt = f"""Original question: {question}
SQL query executed: {sql_query}
Results summary: {results_summary}

Please provide a clear interpretation of these results in Hebrew, explaining what they mean in practical terms for someone working with this building project."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,  # Shorter response for interpretation
                temperature=0.3  # Lower temperature for more factual responses
            )
            
            interpretation = response.choices[0].message.content.strip()
            
            # Add data summary
            data_summary = f"\\n\\n📊 **סיכום נתונים:**\\n"
            data_summary += f"• נמצאו {num_rows} תוצאות\\n"
            
            # Add specific insights based on data type
            if num_rows == 1 and len(columns) == 1:
                # Single value result
                value = results_df.iloc[0, 0]
                if isinstance(value, (int, float)):
                    if 'area' in question.lower() or 'שטח' in question:
                        data_summary += f"• שטח: {value:,.2f} מ²\\n"
                    elif 'count' in question.lower() or 'כמה' in question:
                        data_summary += f"• כמות: {value:,} יחידות\\n"
                    elif 'height' in question.lower() or 'גובה' in question:
                        data_summary += f"• גובה: {value:,.2f} מטר\\n"
                    else:
                        data_summary += f"• ערך: {value:,}\\n"
            
            return interpretation + data_summary
            
        except Exception as e:
            logging.error(f"Results interpretation error: {e}")
            
            # Fallback to basic interpretation
            if num_rows == 1 and len(columns) == 1:
                value = results_df.iloc[0, 0]
                return f"✅ התוצאה לשאלה '{question}': **{value:,}**"
            elif num_rows > 0:
                return f"✅ נמצאו {num_rows} תוצאות לשאלה '{question}'. ראה את הטבלה למטה לפרטים מלאים."
            else:
                return "❌ לא נמצאו תוצאות."

    def _validate_sql(self, sql_query: str) -> float:
        """בדיקת תקינות שאילתת SQL"""
        try:
            # Basic syntax checks
            if not sql_query or len(sql_query.strip()) < 5:
                return 0.0
                
            # Check for prohibited operations
            prohibited = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER']
            sql_upper = sql_query.upper()
            
            if any(word in sql_upper for word in prohibited):
                return 0.0
                
            # Test query syntax (without execution)
            conn = duckdb.connect(self.database_path)
            try:
                # Try to prepare the query
                conn.execute(f"EXPLAIN {sql_query}")
                conn.close()
                return 0.9  # High confidence if syntax is valid
            except:
                conn.close()
                return 0.3  # Low confidence if syntax issues
                
        except Exception:
            return 0.1  # Very low confidence on errors

    def get_suggested_questions(self) -> list:
        """רשימת שאלות לדוגמה"""
        return [
            # שטחים ומידות
            "מה שטח הרצפה בפרויקט?",
            "מה השטח הכולל של החללים?",
            "מה גובה הבניין?",
            "מה הנפח הכולל של הבניין?",
            
            # אלמנטים קונסטרוקטיביים
            "כמה קירות יש בבניין?",
            "כמה קומות יש בבניין?",
            "כמה דלתות יש?",
            "כמה חלונות יש?",
            "כמה קורות יש?",
            "כמה עמודים יש?",
            "כמה לוחות יש?",
            
            # חומרים וטיפוסים
            "איזה חומרים משמשים בבניין?",
            "איזה סוגי קירות יש?",
            
            # English versions
            "What is the floor area?",
            "How many walls are in the building?",
            "How many floors are there?",
            "What materials are used?",
            "How many doors and windows?",
            "What is the building height?",
            "Show me all wall types"
        ]

# Example usage functions
def test_translator():
    """בדיקת המתרגם"""
    translator = IFCQueryTranslator("guy_mador_shiba.duckdb")
    
    test_questions = [
        "כמה קירות יש בבניין?",
        "מה השטח הכולל של החללים?",
        "How many doors are there?"
    ]
    
    for question in test_questions:
        result = translator.translate_query(question)
        print(f"Question: {question}")
        print(f"SQL: {result['sql_query']}")
        print(f"Confidence: {result['confidence']}")
        print("-" * 50)

if __name__ == "__main__":
    test_translator()