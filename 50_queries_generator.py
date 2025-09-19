#!/usr/bin/env python3
"""
50 שאילתות מעניינות ושימושיות על מסד נתונים IFC
מאת: GitHub Copilot
פרויקט: Guy Mador - Shiba V.3.0
"""

# רשימת 50 שאילתות SQL לחקירת מסד נתונים IFC

QUERIES_50 = [
    # ===== קטגוריה: אלמנטים קונסטרוקטיביים =====
    {
        "id": 1,
        "category": "אלמנטים קונסטרוקטיביים",
        "title": "כמה קירות יש בכל קומה?",
        "sql": """
        SELECT bs.Name as storey_name, COUNT(w.ifc_id) as wall_count
        FROM ifcbuildingstorey bs
        LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
        LEFT JOIN ifcwall w ON w.ifc_id = ANY(rel.RelatedElements)
        GROUP BY bs.ifc_id, bs.Name
        ORDER BY wall_count DESC
        """,
        "description": "מראה חלוקה של קירות לפי קומות"
    },
    
    {
        "id": 2,
        "category": "אלמנטים קונסטרוקטיביים",
        "title": "מהם הממדים של כל הקורות?",
        "sql": """
        SELECT p.ifc_id, p.name, p.value
        FROM psets p
        WHERE p.pset_name = 'Pset_BeamCommon' 
        AND p.name IN ('Length', 'Width', 'Height')
        ORDER BY p.ifc_id, p.name
        """,
        "description": "חילוץ ממדי הקורות (אורך, רוחב, גובה)"
    },
    
    {
        "id": 3,
        "category": "אלמנטים קונסטרוקטיביים",
        "title": "איזה עמודים הכי גבוהים?",
        "sql": """
        SELECT p.ifc_id, p.value as height
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcColumn' 
        AND p.name = 'Height'
        ORDER BY CAST(p.value AS DOUBLE) DESC
        LIMIT 10
        """,
        "description": "רשימת 10 העמודים הגבוהים ביותר"
    },
    
    {
        "id": 4,
        "category": "אלמנטים קונסטרוקטיביים",
        "title": "מהו השטח הכולל של כל הרצפות?",
        "sql": """
        SELECT SUM(CAST(p.value AS DOUBLE)) as total_area
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcSlab' 
        AND p.name = 'Area'
        """,
        "description": "חישוב סך השטח של כל הרצפות"
    },
    
    {
        "id": 5,
        "category": "אלמנטים קונסטרוקטיביים",
        "title": "איזה קירות הכי עבים?",
        "sql": """
        SELECT p.ifc_id, p.value as thickness
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcWallStandardCase')
        AND p.name = 'Width'
        ORDER BY CAST(p.value AS DOUBLE) DESC
        """,
        "description": "מיון הקירות לפי עובי"
    },
    
    # ===== קטגוריה: חומרים ומאפיינים =====
    {
        "id": 6,
        "category": "חומרים ומאפיינים",
        "title": "איזה חומרים נמצאים בשימוש הרב ביותר?",
        "sql": """
        SELECT m.Name as material_name, COUNT(ram.RelatingMaterial) as usage_count
        FROM ifcmaterial m
        LEFT JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        GROUP BY m.ifc_id, m.Name
        ORDER BY usage_count DESC
        """,
        "description": "דירוג החומרים לפי שכיחות השימוש"
    },
    
    {
        "id": 7,
        "category": "חומרים ומאפיינים",
        "title": "איזה אלמנטים עשויים מפלדה?",
        "sql": """
        SELECT im.ifc_class, COUNT(*) as count
        FROM ifcmaterial m
        JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE m.Name LIKE '%Steel%' OR m.Name LIKE '%steel%'
        GROUP BY im.ifc_class
        ORDER BY count DESC
        """,
        "description": "אלמנטים המיוצרים מפלדה"
    },
    
    {
        "id": 8,
        "category": "חומרים ומאפיינים",
        "title": "מהן השכבות בקירות המרוכבים?",
        "sql": """
        SELECT ml.Name as layer_name, ml.LayerThickness
        FROM ifcmateriallayer ml
        ORDER BY ml.LayerThickness DESC
        """,
        "description": "פירוט שכבות החומרים בקירות"
    },
    
    {
        "id": 9,
        "category": "חומרים ומאפיינים",
        "title": "איזה צבעים יש לחומרים?",
        "sql": """
        SELECT materials
        FROM geometry
        WHERE materials IS NOT NULL
        LIMIT 10
        """,
        "description": "מידע על צבעי החומרים מנתוני הגיאומטריה"
    },
    
    {
        "id": 10,
        "category": "חומרים ומאפיינים",
        "title": "איזה אלמנטים עשויים מבטון?",
        "sql": """
        SELECT im.ifc_class, im.ifc_id
        FROM ifcmaterial m
        JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE m.Name LIKE '%Concrete%' OR m.Name LIKE '%concrete%'
        """,
        "description": "זיהוי אלמנטי בטון בפרויקט"
    },
    
    # ===== קטגוריה: מערכות MEP =====
    {
        "id": 11,
        "category": "מערכות MEP",
        "title": "מהו האורך הכולל של כל הצנרת?",
        "sql": """
        SELECT SUM(CAST(p.value AS DOUBLE)) as total_pipe_length
        FROM psets p
        WHERE p.pset_name = 'Pset_FlowSegmentPipeSegment' 
        AND p.name = 'Length'
        """,
        "description": "חישוב סך האורך של צנרת במערכות"
    },
    
    {
        "id": 12,
        "category": "מערכות MEP",
        "title": "איזה סוגי שסתומים יש במערכות?",
        "sql": """
        SELECT Name as valve_type, COUNT(*) as count
        FROM ifcvalvetype
        GROUP BY Name
        ORDER BY count DESC
        """,
        "description": "סוגי השסתומים ומספרם"
    },
    
    {
        "id": 13,
        "category": "מערכות MEP",
        "title": "כמה יציאות יש לכל מערכת?",
        "sql": """
        SELECT COUNT(dp.ifc_id) as port_count
        FROM ifcdistributionport dp
        """,
        "description": "ספירת יציאות החיבור במערכות"
    },
    
    {
        "id": 14,
        "category": "מערכות MEP",
        "title": "מהן מערכות האוורור?",
        "sql": """
        SELECT SUM(CAST(p.value AS DOUBLE)) as total_duct_length
        FROM psets p
        WHERE p.pset_name = 'Pset_FlowSegmentDuctSegment' 
        AND p.name = 'Length'
        """,
        "description": "חישוב סך האורך של תעלות אוורור"
    },
    
    {
        "id": 15,
        "category": "מערכות MEP",
        "title": "איזה מערכות משרתות את הבניין?",
        "sql": """
        SELECT COUNT(*) as system_count
        FROM ifcsystem
        """,
        "description": "מספר המערכות הטכניות בבניין"
    },
    
    # ===== קטגוריה: גיאומטריה ונפחים =====
    {
        "id": 16,
        "category": "גיאומטריה ונפחים",
        "title": "כמה אובייקטים יש עם נתוני גיאומטריה?",
        "sql": """
        SELECT COUNT(*) as objects_with_geometry
        FROM geometry
        """,
        "description": "ספירת אובייקטים עם ייצוג גיאומטרי"
    },
    
    {
        "id": 17,
        "category": "גיאומטריה ונפחים",
        "title": "מהן הצורות הגיאומטריות השכיחות?",
        "sql": """
        SELECT COUNT(*) as shape_count
        FROM shape
        """,
        "description": "ספירת הצורות הגיאומטריות במודל"
    },
    
    {
        "id": 18,
        "category": "גיאומטריה ונפחים",
        "title": "מהו הנפח הכולל של האלמנטים?",
        "sql": """
        SELECT SUM(CAST(p.value AS DOUBLE)) as total_volume
        FROM psets p
        WHERE p.name = 'Volume'
        """,
        "description": "חישוב סך הנפח של כל האלמנטים"
    },
    
    {
        "id": 19,
        "category": "גיאומטריה ונפחים",
        "title": "איזה אלמנטים הכי גדולים בשטח?",
        "sql": """
        SELECT p.ifc_id, p.value as area
        FROM psets p
        WHERE p.name = 'Area'
        ORDER BY CAST(p.value AS DOUBLE) DESC
        LIMIT 10
        """,
        "description": "10 האלמנטים עם השטח הגדול ביותר"
    },
    
    {
        "id": 20,
        "category": "גיאומטריה ונפחים",
        "title": "כמה נקודות קרטזיות יש במודל?",
        "sql": """
        SELECT COUNT(*) as cartesian_points
        FROM id_map
        WHERE ifc_class = 'IfcCartesianPoint'
        """,
        "description": "ספירת נקודות קרטזיות במודל הגיאומטרי"
    },
    
    # ===== קטגוריה: Property Sets ותכונות =====
    {
        "id": 21,
        "category": "Property Sets ותכונות",
        "title": "איזה Property Sets קשורים לדלתות?",
        "sql": """
        SELECT DISTINCT p.pset_name, COUNT(*) as count
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcDoor'
        GROUP BY p.pset_name
        ORDER BY count DESC
        """,
        "description": "קבוצות תכונות של דלתות"
    },
    
    {
        "id": 22,
        "category": "Property Sets ותכונות",
        "title": "איזה תכונות קשורות לאבטחת אש?",
        "sql": """
        SELECT p.name, p.value, COUNT(*) as count
        FROM psets p
        WHERE p.name LIKE '%Fire%' OR p.pset_name LIKE '%Fire%'
        GROUP BY p.name, p.value
        ORDER BY count DESC
        """,
        "description": "תכונות הקשורות לאבטחת אש"
    },
    
    {
        "id": 23,
        "category": "Property Sets ותכונות",
        "title": "מהן התכונות הנפוצות ביותר?",
        "sql": """
        SELECT p.name as property_name, COUNT(*) as count
        FROM psets p
        GROUP BY p.name
        ORDER BY count DESC
        LIMIT 20
        """,
        "description": "20 התכונות השכיחות ביותר"
    },
    
    {
        "id": 24,
        "category": "Property Sets ותכונות",
        "title": "איזה אלמנטים יש להם תכונת LoadBearing?",
        "sql": """
        SELECT im.ifc_class, p.value as load_bearing, COUNT(*) as count
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE p.name = 'LoadBearing'
        GROUP BY im.ifc_class, p.value
        ORDER BY count DESC
        """,
        "description": "אלמנטים נושאי משקל"
    },
    
    {
        "id": 25,
        "category": "Property Sets ותכונות",
        "title": "מהן תכונות הקיימות (Sustainability)?",
        "sql": """
        SELECT p.name, p.value
        FROM psets p
        WHERE p.name LIKE '%Sustainability%' OR p.pset_name LIKE '%Environmental%'
        """,
        "description": "תכונות קיימות וסביבה"
    },
    
    # ===== קטגוריה: מבנה הבניין =====
    {
        "id": 26,
        "category": "מבנה הבניין",
        "title": "מהם פרטי הפרויקט?",
        "sql": """
        SELECT *
        FROM ifcproject
        """,
        "description": "מידע כללי על הפרויקט"
    },
    
    {
        "id": 27,
        "category": "מבנה הבניין",
        "title": "מהם פרטי האתר?",
        "sql": """
        SELECT *
        FROM ifcsite
        """,
        "description": "מידע על האתר"
    },
    
    {
        "id": 28,
        "category": "מבנה הבניין",
        "title": "מהן הקומות בבניין?",
        "sql": """
        SELECT Name as storey_name, Elevation
        FROM ifcbuildingstorey
        ORDER BY Elevation
        """,
        "description": "רשימת קומות וגובהן"
    },
    
    {
        "id": 29,
        "category": "מבנה הבניין",
        "title": "כמה אלמנטים יש בכל קומה?",
        "sql": """
        SELECT bs.Name as storey_name, COUNT(rel.RelatedElements) as element_count
        FROM ifcbuildingstorey bs
        LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
        GROUP BY bs.ifc_id, bs.Name
        ORDER BY element_count DESC
        """,
        "description": "חלוקת אלמנטים לפי קומות"
    },
    
    {
        "id": 30,
        "category": "מבנה הבניין",
        "title": "מהן המחלקות (Classifications) של האלמנטים?",
        "sql": """
        SELECT cr.Name as classification, COUNT(*) as count
        FROM ifcclassificationreference cr
        GROUP BY cr.Name
        ORDER BY count DESC
        """,
        "description": "מחלקות האלמנטים לפי תקנים"
    },
    
    # ===== קטגוריה: פתחים (דלתות וחלונות) =====
    {
        "id": 31,
        "category": "פתחים (דלתות וחלונות)",
        "title": "מהן תכונות הדלתות?",
        "sql": """
        SELECT d.Name, d.OverallHeight, d.OverallWidth
        FROM ifcdoor d
        WHERE d.Name IS NOT NULL
        """,
        "description": "ממדי הדלתות"
    },
    
    {
        "id": 32,
        "category": "פתחים (דלתות וחלונות)",
        "title": "מהן תכונות החלונות?",
        "sql": """
        SELECT w.Name, w.OverallHeight, w.OverallWidth
        FROM ifcwindow w
        WHERE w.Name IS NOT NULL
        """,
        "description": "ממדי החלונות"
    },
    
    {
        "id": 33,
        "category": "פתחים (דלתות וחלונות)",
        "title": "כמה פתחים יש בקירות?",
        "sql": """
        SELECT COUNT(*) as opening_count
        FROM ifcopeningelement
        """,
        "description": "מספר הפתחים בקירות"
    },
    
    {
        "id": 34,
        "category": "פתחים (דלתות וחלונות)",
        "title": "איזה סגנונות דלתות יש?",
        "sql": """
        SELECT ds.Name as door_style, COUNT(*) as count
        FROM ifcdoorstyle ds
        GROUP BY ds.Name
        """,
        "description": "סגנונות הדלתות בפרויקט"
    },
    
    {
        "id": 35,
        "category": "פתחים (דלתות וחלונות)",
        "title": "איזה סגנונות חלונות יש?",
        "sql": """
        SELECT ws.Name as window_style, COUNT(*) as count
        FROM ifcwindowstyle ws
        GROUP BY ws.Name
        """,
        "description": "סגנונות החלונות בפרויקט"
    },
    
    # ===== קטגוריה: קשרים ויחסים =====
    {
        "id": 36,
        "category": "קשרים ויחסים",
        "title": "איזה אלמנטים קשורים זה לזה?",
        "sql": """
        SELECT COUNT(*) as aggregation_relationships
        FROM ifcrelaggregates
        """,
        "description": "מספר קשרי הקבצה בין אלמנטים"
    },
    
    {
        "id": 37,
        "category": "קשרים ויחסים",
        "title": "איזה אלמנטים מחוברים בנתיבים?",
        "sql": """
        SELECT COUNT(*) as path_connections
        FROM ifcrelconnectspathelements
        """,
        "description": "חיבורי נתיבים בין אלמנטים"
    },
    
    {
        "id": 38,
        "category": "קשרים ויחסים",
        "title": "איזה יציאות מחוברות לאלמנטים?",
        "sql": """
        SELECT COUNT(*) as port_connections
        FROM ifcrelconnectsporttoelement
        """,
        "description": "חיבורי יציאות לאלמנטים"
    },
    
    {
        "id": 39,
        "category": "קשרים ויחסים",
        "title": "איזה קבוצות אלמנטים יש?",
        "sql": """
        SELECT COUNT(*) as group_assignments
        FROM ifcrelassignstogroup
        """,
        "description": "הקצאות אלמנטים לקבוצות"
    },
    
    {
        "id": 40,
        "category": "קשרים ויחסים",
        "title": "איזה אלמנטים מוגדרים על ידי סוגים?",
        "sql": """
        SELECT COUNT(*) as type_definitions
        FROM ifcreldefinesbytype
        """,
        "description": "הגדרות אלמנטים לפי סוגים"
    },
    
    # ===== קטגוריה: ניתוח איכות ושלמות =====
    {
        "id": 41,
        "category": "ניתוח איכות ושלמות",
        "title": "איזה אלמנטים חסרים שמות?",
        "sql": """
        SELECT im.ifc_class, COUNT(*) as unnamed_count
        FROM id_map im
        LEFT JOIN ifcwall w ON im.ifc_id = w.ifc_id AND im.ifc_class = 'IfcWall'
        LEFT JOIN ifcbeam b ON im.ifc_id = b.ifc_id AND im.ifc_class = 'IfcBeam'
        WHERE (w.Name IS NULL AND im.ifc_class = 'IfcWall') 
           OR (b.Name IS NULL AND im.ifc_class = 'IfcBeam')
        GROUP BY im.ifc_class
        """,
        "description": "אלמנטים ללא שמות"
    },
    
    {
        "id": 42,
        "category": "ניתוח איכות ושלמות",
        "title": "איזה אלמנטים חסרים Property Sets?",
        "sql": """
        SELECT im.ifc_class, COUNT(*) as no_psets_count
        FROM id_map im
        LEFT JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE p.ifc_id IS NULL
        GROUP BY im.ifc_class
        ORDER BY no_psets_count DESC
        """,
        "description": "אלמנטים ללא תכונות"
    },
    
    {
        "id": 43,
        "category": "ניתוח איכות ושלמות",
        "title": "איזה אלמנטים חסרים חומרים?",
        "sql": """
        SELECT im.ifc_class, COUNT(*) as no_material_count
        FROM id_map im
        LEFT JOIN ifcrelassociatesmaterial ram ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE ram.RelatingMaterial IS NULL
        GROUP BY im.ifc_class
        ORDER BY no_material_count DESC
        """,
        "description": "אלמנטים ללא הגדרת חומר"
    },
    
    {
        "id": 44,
        "category": "ניתוח איכות ושלמות",
        "title": "איזה אלמנטים חסרים נתוני גיאומטריה?",
        "sql": """
        SELECT im.ifc_class, COUNT(*) as no_geometry_count
        FROM id_map im
        LEFT JOIN geometry g ON CAST(im.ifc_id AS VARCHAR) = g.id
        WHERE g.id IS NULL
        AND im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
        GROUP BY im.ifc_class
        """,
        "description": "אלמנטים קונסטרוקטיביים ללא גיאומטריה"
    },
    
    {
        "id": 45,
        "category": "ניתוח איכות ושלמות",
        "title": "מהו אחוז השלמות של המידע?",
        "sql": """
        SELECT 
            COUNT(DISTINCT im.ifc_id) as total_elements,
            COUNT(DISTINCT p.ifc_id) as elements_with_properties,
            ROUND(COUNT(DISTINCT p.ifc_id) * 100.0 / COUNT(DISTINCT im.ifc_id), 2) as completion_percentage
        FROM id_map im
        LEFT JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
        """,
        "description": "אחוז השלמות של מידע תכונות"
    },
    
    # ===== קטגוריה: סטטיסטיקות מתקדמות =====
    {
        "id": 46,
        "category": "סטטיסטיקות מתקדמות",
        "title": "מהו הפילוג של סוגי האלמנטים?",
        "sql": """
        SELECT 
            im.ifc_class,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM id_map), 2) as percentage
        FROM id_map im
        GROUP BY im.ifc_class
        ORDER BY count DESC
        LIMIT 15
        """,
        "description": "פילוג אחוזי של סוגי האלמנטים"
    },
    
    {
        "id": 47,
        "category": "סטטיסטיקות מתקדמות",
        "title": "מהם הממדים הממוצעים של הקורות?",
        "sql": """
        SELECT 
            AVG(CAST(p1.value AS DOUBLE)) as avg_length,
            AVG(CAST(p2.value AS DOUBLE)) as avg_width,
            AVG(CAST(p3.value AS DOUBLE)) as avg_height
        FROM psets p1
        JOIN psets p2 ON p1.ifc_id = p2.ifc_id
        JOIN psets p3 ON p1.ifc_id = p3.ifc_id
        WHERE p1.pset_name = 'Pset_BeamCommon' 
        AND p1.name = 'Length' 
        AND p2.name = 'Width' 
        AND p3.name = 'Height'
        """,
        "description": "ממדים ממוצעים של קורות"
    },
    
    {
        "id": 48,
        "category": "סטטיסטיקות מתקדמות",
        "title": "מהו היחס בין אלמנטים קונסטרוקטיביים למערכות?",
        "sql": """
        SELECT 
            'קונסטרוקציה' as category,
            COUNT(*) as count
        FROM id_map 
        WHERE ifc_class IN ('IfcWall', 'IfcWallStandardCase', 'IfcBeam', 'IfcColumn', 'IfcSlab')
        
        UNION ALL
        
        SELECT 
            'מערכות MEP' as category,
            COUNT(*) as count
        FROM id_map 
        WHERE ifc_class IN ('IfcFlowSegment', 'IfcFlowFitting', 'IfcFlowController', 'IfcFlowTerminal')
        """,
        "description": "השוואה בין קונסטרוקציה למערכות"
    },
    
    {
        "id": 49,
        "category": "סטטיסטיקות מתקדמות",
        "title": "מהן התכונות הייחודיות של כל סוג אלמנט?",
        "sql": """
        SELECT 
            im.ifc_class,
            COUNT(DISTINCT p.name) as unique_properties
        FROM id_map im
        JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
        GROUP BY im.ifc_class
        ORDER BY unique_properties DESC
        """,
        "description": "מספר התכונות הייחודיות לכל סוג אלמנט"
    },
    
    {
        "id": 50,
        "category": "סטטיסטיקות מתקדמות",
        "title": "מהו המידע החסר ביותר במודל?",
        "sql": """
        SELECT 
            'אלמנטים ללא חומרים' as missing_info,
            COUNT(*) as count
        FROM id_map im
        LEFT JOIN ifcrelassociatesmaterial ram ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE ram.RelatingMaterial IS NULL
        AND im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab')
        
        UNION ALL
        
        SELECT 
            'אלמנטים ללא תכונות' as missing_info,
            COUNT(*) as count
        FROM id_map im
        LEFT JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE p.ifc_id IS NULL
        AND im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab')
        """,
        "description": "ניתוח המידע החסר במודל"
    }
]

def print_queries_by_category():
    """הדפסת השאילתות לפי קטגוריות"""
    
    print("🏗️ 50 שאילתות מעניינות על מסד נתונים IFC")
    print("=" * 80)
    print("פרויקט: Guy Mador - Shiba V.3.0")
    print("מסד נתונים: guy_mador_shiba.duckdb")
    print()
    
    # קיבוץ לפי קטגוריות
    categories = {}
    for query in QUERIES_50:
        cat = query["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(query)
    
    # הדפסה לפי קטגוריות
    for category, queries in categories.items():
        print(f"\n📁 {category}")
        print("-" * 60)
        
        for query in queries:
            print(f"\n{query['id']}. 🔍 {query['title']}")
            print(f"   📖 {query['description']}")
            print(f"   📝 SQL:")
            
            # ניקוי ההזחה ברווחים
            sql_lines = query['sql'].strip().split('\n')
            for line in sql_lines:
                clean_line = line.strip()
                if clean_line:
                    print(f"      {clean_line}")

def save_queries_to_file():
    """שמירת השאילתות לקובץ"""
    
    with open("50_ifc_queries.md", "w", encoding="utf-8") as f:
        f.write("# 50 שאילתות מעניינות על מסד נתונים IFC\n\n")
        f.write("**פרויקט:** Guy Mador - Shiba V.3.0  \n")
        f.write("**מסד נתונים:** guy_mador_shiba.duckdb  \n")
        f.write("**נוצר על ידי:** GitHub Copilot\n\n")
        
        # קיבוץ לפי קטגוריות
        categories = {}
        for query in QUERIES_50:
            cat = query["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(query)
        
        # כתיבה לפי קטגוריות
        for category, queries in categories.items():
            f.write(f"\n## 📁 {category}\n\n")
            
            for query in queries:
                f.write(f"### {query['id']}. 🔍 {query['title']}\n\n")
                f.write(f"**תיאור:** {query['description']}\n\n")
                f.write("**SQL:**\n```sql\n")
                f.write(query['sql'].strip())
                f.write("\n```\n\n")
                f.write("---\n\n")

if __name__ == "__main__":
    print_queries_by_category()
    save_queries_to_file()
    
    print(f"\n✅ נוצר קובץ: 50_ifc_queries.md")
    print("📁 הקובץ מכיל את כל 50 השאילתות במבנה מאורגן")
    
    print(f"\n🎯 סיכום:")
    print(f"📊 {len(QUERIES_50)} שאילתות בסך הכל")
    
    categories_count = {}
    for query in QUERIES_50:
        cat = query["category"]
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    print("📁 חלוקה לפי קטגוריות:")
    for cat, count in categories_count.items():
        print(f"   • {cat}: {count} שאילתות")