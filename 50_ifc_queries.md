# 50 שאילתות מעניינות על מסד נתונים IFC

**פרויקט:** Guy Mador - Shiba V.3.0  
**מסד נתונים:** guy_mador_shiba.duckdb  
**נוצר על ידי:** GitHub Copilot


## 📁 אלמנטים קונסטרוקטיביים

### 1. 🔍 כמה קירות יש בכל קומה?

**תיאור:** מראה חלוקה של קירות לפי קומות

**SQL:**
```sql
SELECT bs.Name as storey_name, COUNT(w.ifc_id) as wall_count
        FROM ifcbuildingstorey bs
        LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
        LEFT JOIN ifcwall w ON w.ifc_id = ANY(rel.RelatedElements)
        GROUP BY bs.ifc_id, bs.Name
        ORDER BY wall_count DESC
```

---

### 2. 🔍 מהם הממדים של כל הקורות?

**תיאור:** חילוץ ממדי הקורות (אורך, רוחב, גובה)

**SQL:**
```sql
SELECT p.ifc_id, p.name, p.value
        FROM psets p
        WHERE p.pset_name = 'Pset_BeamCommon' 
        AND p.name IN ('Length', 'Width', 'Height')
        ORDER BY p.ifc_id, p.name
```

---

### 3. 🔍 איזה עמודים הכי גבוהים?

**תיאור:** רשימת 10 העמודים הגבוהים ביותר

**SQL:**
```sql
SELECT p.ifc_id, p.value as height
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcColumn' 
        AND p.name = 'Height'
        ORDER BY CAST(p.value AS DOUBLE) DESC
        LIMIT 10
```

---

### 4. 🔍 מהו השטח הכולל של כל הרצפות?

**תיאור:** חישוב סך השטח של כל הרצפות

**SQL:**
```sql
SELECT SUM(CAST(p.value AS DOUBLE)) as total_area
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcSlab' 
        AND p.name = 'Area'
```

---

### 5. 🔍 איזה קירות הכי עבים?

**תיאור:** מיון הקירות לפי עובי

**SQL:**
```sql
SELECT p.ifc_id, p.value as thickness
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcWallStandardCase')
        AND p.name = 'Width'
        ORDER BY CAST(p.value AS DOUBLE) DESC
```

---


## 📁 חומרים ומאפיינים

### 6. 🔍 איזה חומרים נמצאים בשימוש הרב ביותר?

**תיאור:** דירוג החומרים לפי שכיחות השימוש

**SQL:**
```sql
SELECT m.Name as material_name, COUNT(ram.RelatingMaterial) as usage_count
        FROM ifcmaterial m
        LEFT JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        GROUP BY m.ifc_id, m.Name
        ORDER BY usage_count DESC
```

---

### 7. 🔍 איזה אלמנטים עשויים מפלדה?

**תיאור:** אלמנטים המיוצרים מפלדה

**SQL:**
```sql
SELECT im.ifc_class, COUNT(*) as count
        FROM ifcmaterial m
        JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE m.Name LIKE '%Steel%' OR m.Name LIKE '%steel%'
        GROUP BY im.ifc_class
        ORDER BY count DESC
```

---

### 8. 🔍 מהן השכבות בקירות המרוכבים?

**תיאור:** פירוט שכבות החומרים בקירות

**SQL:**
```sql
SELECT ml.Name as layer_name, ml.LayerThickness
        FROM ifcmateriallayer ml
        ORDER BY ml.LayerThickness DESC
```

---

### 9. 🔍 איזה צבעים יש לחומרים?

**תיאור:** מידע על צבעי החומרים מנתוני הגיאומטריה

**SQL:**
```sql
SELECT materials
        FROM geometry
        WHERE materials IS NOT NULL
        LIMIT 10
```

---

### 10. 🔍 איזה אלמנטים עשויים מבטון?

**תיאור:** זיהוי אלמנטי בטון בפרויקט

**SQL:**
```sql
SELECT im.ifc_class, im.ifc_id
        FROM ifcmaterial m
        JOIN ifcrelassociatesmaterial ram ON m.ifc_id = ram.RelatingMaterial
        JOIN id_map im ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE m.Name LIKE '%Concrete%' OR m.Name LIKE '%concrete%'
```

---


## 📁 מערכות MEP

### 11. 🔍 מהו האורך הכולל של כל הצנרת?

**תיאור:** חישוב סך האורך של צנרת במערכות

**SQL:**
```sql
SELECT SUM(CAST(p.value AS DOUBLE)) as total_pipe_length
        FROM psets p
        WHERE p.pset_name = 'Pset_FlowSegmentPipeSegment' 
        AND p.name = 'Length'
```

---

### 12. 🔍 איזה סוגי שסתומים יש במערכות?

**תיאור:** סוגי השסתומים ומספרם

**SQL:**
```sql
SELECT Name as valve_type, COUNT(*) as count
        FROM ifcvalvetype
        GROUP BY Name
        ORDER BY count DESC
```

---

### 13. 🔍 כמה יציאות יש לכל מערכת?

**תיאור:** ספירת יציאות החיבור במערכות

**SQL:**
```sql
SELECT COUNT(dp.ifc_id) as port_count
        FROM ifcdistributionport dp
```

---

### 14. 🔍 מהן מערכות האוורור?

**תיאור:** חישוב סך האורך של תעלות אוורור

**SQL:**
```sql
SELECT SUM(CAST(p.value AS DOUBLE)) as total_duct_length
        FROM psets p
        WHERE p.pset_name = 'Pset_FlowSegmentDuctSegment' 
        AND p.name = 'Length'
```

---

### 15. 🔍 איזה מערכות משרתות את הבניין?

**תיאור:** מספר המערכות הטכניות בבניין

**SQL:**
```sql
SELECT COUNT(*) as system_count
        FROM ifcsystem
```

---


## 📁 גיאומטריה ונפחים

### 16. 🔍 כמה אובייקטים יש עם נתוני גיאומטריה?

**תיאור:** ספירת אובייקטים עם ייצוג גיאומטרי

**SQL:**
```sql
SELECT COUNT(*) as objects_with_geometry
        FROM geometry
```

---

### 17. 🔍 מהן הצורות הגיאומטריות השכיחות?

**תיאור:** ספירת הצורות הגיאומטריות במודל

**SQL:**
```sql
SELECT COUNT(*) as shape_count
        FROM shape
```

---

### 18. 🔍 מהו הנפח הכולל של האלמנטים?

**תיאור:** חישוב סך הנפח של כל האלמנטים

**SQL:**
```sql
SELECT SUM(CAST(p.value AS DOUBLE)) as total_volume
        FROM psets p
        WHERE p.name = 'Volume'
```

---

### 19. 🔍 איזה אלמנטים הכי גדולים בשטח?

**תיאור:** 10 האלמנטים עם השטח הגדול ביותר

**SQL:**
```sql
SELECT p.ifc_id, p.value as area
        FROM psets p
        WHERE p.name = 'Area'
        ORDER BY CAST(p.value AS DOUBLE) DESC
        LIMIT 10
```

---

### 20. 🔍 כמה נקודות קרטזיות יש במודל?

**תיאור:** ספירת נקודות קרטזיות במודל הגיאומטרי

**SQL:**
```sql
SELECT COUNT(*) as cartesian_points
        FROM id_map
        WHERE ifc_class = 'IfcCartesianPoint'
```

---


## 📁 Property Sets ותכונות

### 21. 🔍 איזה Property Sets קשורים לדלתות?

**תיאור:** קבוצות תכונות של דלתות

**SQL:**
```sql
SELECT DISTINCT p.pset_name, COUNT(*) as count
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE im.ifc_class = 'IfcDoor'
        GROUP BY p.pset_name
        ORDER BY count DESC
```

---

### 22. 🔍 איזה תכונות קשורות לאבטחת אש?

**תיאור:** תכונות הקשורות לאבטחת אש

**SQL:**
```sql
SELECT p.name, p.value, COUNT(*) as count
        FROM psets p
        WHERE p.name LIKE '%Fire%' OR p.pset_name LIKE '%Fire%'
        GROUP BY p.name, p.value
        ORDER BY count DESC
```

---

### 23. 🔍 מהן התכונות הנפוצות ביותר?

**תיאור:** 20 התכונות השכיחות ביותר

**SQL:**
```sql
SELECT p.name as property_name, COUNT(*) as count
        FROM psets p
        GROUP BY p.name
        ORDER BY count DESC
        LIMIT 20
```

---

### 24. 🔍 איזה אלמנטים יש להם תכונת LoadBearing?

**תיאור:** אלמנטים נושאי משקל

**SQL:**
```sql
SELECT im.ifc_class, p.value as load_bearing, COUNT(*) as count
        FROM psets p
        JOIN id_map im ON p.ifc_id = im.ifc_id
        WHERE p.name = 'LoadBearing'
        GROUP BY im.ifc_class, p.value
        ORDER BY count DESC
```

---

### 25. 🔍 מהן תכונות הקיימות (Sustainability)?

**תיאור:** תכונות קיימות וסביבה

**SQL:**
```sql
SELECT p.name, p.value
        FROM psets p
        WHERE p.name LIKE '%Sustainability%' OR p.pset_name LIKE '%Environmental%'
```

---


## 📁 מבנה הבניין

### 26. 🔍 מהם פרטי הפרויקט?

**תיאור:** מידע כללי על הפרויקט

**SQL:**
```sql
SELECT *
        FROM ifcproject
```

---

### 27. 🔍 מהם פרטי האתר?

**תיאור:** מידע על האתר

**SQL:**
```sql
SELECT *
        FROM ifcsite
```

---

### 28. 🔍 מהן הקומות בבניין?

**תיאור:** רשימת קומות וגובהן

**SQL:**
```sql
SELECT Name as storey_name, Elevation
        FROM ifcbuildingstorey
        ORDER BY Elevation
```

---

### 29. 🔍 כמה אלמנטים יש בכל קומה?

**תיאור:** חלוקת אלמנטים לפי קומות

**SQL:**
```sql
SELECT bs.Name as storey_name, COUNT(rel.RelatedElements) as element_count
        FROM ifcbuildingstorey bs
        LEFT JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
        GROUP BY bs.ifc_id, bs.Name
        ORDER BY element_count DESC
```

---

### 30. 🔍 מהן המחלקות (Classifications) של האלמנטים?

**תיאור:** מחלקות האלמנטים לפי תקנים

**SQL:**
```sql
SELECT cr.Name as classification, COUNT(*) as count
        FROM ifcclassificationreference cr
        GROUP BY cr.Name
        ORDER BY count DESC
```

---


## 📁 פתחים (דלתות וחלונות)

### 31. 🔍 מהן תכונות הדלתות?

**תיאור:** ממדי הדלתות

**SQL:**
```sql
SELECT d.Name, d.OverallHeight, d.OverallWidth
        FROM ifcdoor d
        WHERE d.Name IS NOT NULL
```

---

### 32. 🔍 מהן תכונות החלונות?

**תיאור:** ממדי החלונות

**SQL:**
```sql
SELECT w.Name, w.OverallHeight, w.OverallWidth
        FROM ifcwindow w
        WHERE w.Name IS NOT NULL
```

---

### 33. 🔍 כמה פתחים יש בקירות?

**תיאור:** מספר הפתחים בקירות

**SQL:**
```sql
SELECT COUNT(*) as opening_count
        FROM ifcopeningelement
```

---

### 34. 🔍 איזה סגנונות דלתות יש?

**תיאור:** סגנונות הדלתות בפרויקט

**SQL:**
```sql
SELECT ds.Name as door_style, COUNT(*) as count
        FROM ifcdoorstyle ds
        GROUP BY ds.Name
```

---

### 35. 🔍 איזה סגנונות חלונות יש?

**תיאור:** סגנונות החלונות בפרויקט

**SQL:**
```sql
SELECT ws.Name as window_style, COUNT(*) as count
        FROM ifcwindowstyle ws
        GROUP BY ws.Name
```

---


## 📁 קשרים ויחסים

### 36. 🔍 איזה אלמנטים קשורים זה לזה?

**תיאור:** מספר קשרי הקבצה בין אלמנטים

**SQL:**
```sql
SELECT COUNT(*) as aggregation_relationships
        FROM ifcrelaggregates
```

---

### 37. 🔍 איזה אלמנטים מחוברים בנתיבים?

**תיאור:** חיבורי נתיבים בין אלמנטים

**SQL:**
```sql
SELECT COUNT(*) as path_connections
        FROM ifcrelconnectspathelements
```

---

### 38. 🔍 איזה יציאות מחוברות לאלמנטים?

**תיאור:** חיבורי יציאות לאלמנטים

**SQL:**
```sql
SELECT COUNT(*) as port_connections
        FROM ifcrelconnectsporttoelement
```

---

### 39. 🔍 איזה קבוצות אלמנטים יש?

**תיאור:** הקצאות אלמנטים לקבוצות

**SQL:**
```sql
SELECT COUNT(*) as group_assignments
        FROM ifcrelassignstogroup
```

---

### 40. 🔍 איזה אלמנטים מוגדרים על ידי סוגים?

**תיאור:** הגדרות אלמנטים לפי סוגים

**SQL:**
```sql
SELECT COUNT(*) as type_definitions
        FROM ifcreldefinesbytype
```

---


## 📁 ניתוח איכות ושלמות

### 41. 🔍 איזה אלמנטים חסרים שמות?

**תיאור:** אלמנטים ללא שמות

**SQL:**
```sql
SELECT im.ifc_class, COUNT(*) as unnamed_count
        FROM id_map im
        LEFT JOIN ifcwall w ON im.ifc_id = w.ifc_id AND im.ifc_class = 'IfcWall'
        LEFT JOIN ifcbeam b ON im.ifc_id = b.ifc_id AND im.ifc_class = 'IfcBeam'
        WHERE (w.Name IS NULL AND im.ifc_class = 'IfcWall') 
           OR (b.Name IS NULL AND im.ifc_class = 'IfcBeam')
        GROUP BY im.ifc_class
```

---

### 42. 🔍 איזה אלמנטים חסרים Property Sets?

**תיאור:** אלמנטים ללא תכונות

**SQL:**
```sql
SELECT im.ifc_class, COUNT(*) as no_psets_count
        FROM id_map im
        LEFT JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE p.ifc_id IS NULL
        GROUP BY im.ifc_class
        ORDER BY no_psets_count DESC
```

---

### 43. 🔍 איזה אלמנטים חסרים חומרים?

**תיאור:** אלמנטים ללא הגדרת חומר

**SQL:**
```sql
SELECT im.ifc_class, COUNT(*) as no_material_count
        FROM id_map im
        LEFT JOIN ifcrelassociatesmaterial ram ON im.ifc_id = ANY(ram.RelatedObjects)
        WHERE ram.RelatingMaterial IS NULL
        GROUP BY im.ifc_class
        ORDER BY no_material_count DESC
```

---

### 44. 🔍 איזה אלמנטים חסרים נתוני גיאומטריה?

**תיאור:** אלמנטים קונסטרוקטיביים ללא גיאומטריה

**SQL:**
```sql
SELECT im.ifc_class, COUNT(*) as no_geometry_count
        FROM id_map im
        LEFT JOIN geometry g ON CAST(im.ifc_id AS VARCHAR) = g.id
        WHERE g.id IS NULL
        AND im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
        GROUP BY im.ifc_class
```

---

### 45. 🔍 מהו אחוז השלמות של המידע?

**תיאור:** אחוז השלמות של מידע תכונות

**SQL:**
```sql
SELECT 
            COUNT(DISTINCT im.ifc_id) as total_elements,
            COUNT(DISTINCT p.ifc_id) as elements_with_properties,
            ROUND(COUNT(DISTINCT p.ifc_id) * 100.0 / COUNT(DISTINCT im.ifc_id), 2) as completion_percentage
        FROM id_map im
        LEFT JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
```

---


## 📁 סטטיסטיקות מתקדמות

### 46. 🔍 מהו הפילוג של סוגי האלמנטים?

**תיאור:** פילוג אחוזי של סוגי האלמנטים

**SQL:**
```sql
SELECT 
            im.ifc_class,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM id_map), 2) as percentage
        FROM id_map im
        GROUP BY im.ifc_class
        ORDER BY count DESC
        LIMIT 15
```

---

### 47. 🔍 מהם הממדים הממוצעים של הקורות?

**תיאור:** ממדים ממוצעים של קורות

**SQL:**
```sql
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
```

---

### 48. 🔍 מהו היחס בין אלמנטים קונסטרוקטיביים למערכות?

**תיאור:** השוואה בין קונסטרוקציה למערכות

**SQL:**
```sql
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
```

---

### 49. 🔍 מהן התכונות הייחודיות של כל סוג אלמנט?

**תיאור:** מספר התכונות הייחודיות לכל סוג אלמנט

**SQL:**
```sql
SELECT 
            im.ifc_class,
            COUNT(DISTINCT p.name) as unique_properties
        FROM id_map im
        JOIN psets p ON im.ifc_id = p.ifc_id
        WHERE im.ifc_class IN ('IfcWall', 'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcDoor', 'IfcWindow')
        GROUP BY im.ifc_class
        ORDER BY unique_properties DESC
```

---

### 50. 🔍 מהו המידע החסר ביותר במודל?

**תיאור:** ניתוח המידע החסר במודל

**SQL:**
```sql
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
```

---

