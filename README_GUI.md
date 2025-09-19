# 🏗️ IFC Database Assistant - הוראות הפעלה

## דרישות מקדימות

1. **Python 3.8+** מותקן על המחשב
2. **מסד הנתונים** `guy_mador_shiba.duckdb` בתיקייה

## התקנה והפעלה

### שלב 1: התקנת הספריות הנדרשות

```powershell
# התקנת הספריות מקובץ requirements
pip install -r requirements_gui.txt
```

או התקנה ידנית:
```powershell
pip install streamlit duckdb pandas ifcopenshell numpy
```

### שלב 2: הפעלת האפליקציה

```powershell
# נווט לתיקיית הפרויקט
cd "c:\Users\PC\Desktop\אפליקציות בפיתוח\ifc-2-duckdb-master - GUI\ifc-2-duckdb-master"

# הפעל את האפליקציה
streamlit run app.py
```

### שלב 3: פתיחת הדפדפן

האפליקציה תפתח אוטומטית בדפדפן בכתובת:
```
http://localhost:8501
```

## תכונות עיקריות

### 🔍 שאילתות מוכנות (35 שאילתות)
- **אלמנטים קונסטרוקטיביים** - קירות, קורות, עמודים, רצפות
- **חומרים ומאפיינים** - ניתוח חומרים וצבעים
- **מערכות MEP** - צנרת, אוורור, חשמל
- **גיאומטריה ונפחים** - נתוני תלת-ממד
- **Property Sets ותכונות** - מאפייני אלמנטים
- **מבנה הבניין** - קומות ומבנה היררכי
- **פתחים** - דלתות וחלונות
- **סטטיסטיקות** - נתונים כמותיים

### 💻 שאילתות SQL מותאמות אישית
- תמיכה בשאילתות SELECT, SHOW, DESCRIBE
- הגנה מפני שאילתות מזיקות
- הצגת תוצאות בטבלה אינטראקטיבית

### 🔄 תכונות נוספות
- **חיפוש** בשאילתות המוכנות
- **הורדת תוצאות** כקובץ CSV
- **ממשק דו-לשוני** (עברית ואנגלית)
- **מידע על המסד** בזמן אמת

## דוגמאות שימוש

### שאילתות בסיסיות:
```sql
-- הצגת כל הטבלאות
SHOW TABLES

-- ספירת קירות
SELECT COUNT(*) FROM ifcwall

-- מבנה טבלת הקירות
DESCRIBE ifcwall
```

### שאילתות מתקדמות:
```sql
-- קירות לפי קומות
SELECT bs.Name as storey, COUNT(w.ifc_id) as walls
FROM ifcbuildingstorey bs
JOIN ifcrelcontainedinspatialstructure rel ON bs.ifc_id = rel.RelatingStructure
JOIN ifcwall w ON w.ifc_id = ANY(rel.RelatedElements)
GROUP BY bs.Name
```

## פתרון בעיות נפוצות

### שגיאת מפתחות כפולים (Duplicate Key Error)
```
StreamlitDuplicateElementKey: There are multiple elements with the same key
```
**פתרון:** רענן את הדף בדפדפן (F5) או סגור ופתח שוב את האפליקציה

### שגיאת חיבור למסד הנתונים
```
❌ שגיאה בחיבור למסד הנתונים
```
**פתרון:** ודא שהקובץ `guy_mador_shiba.duckdb` נמצא בתיקיית הפרויקט

### שגיאת התקנה
```
ERROR: Could not install packages
```
**פתרון:** 
```powershell
# עדכן pip
python -m pip install --upgrade pip

# התקן בפירוט
pip install streamlit --verbose
```

### האפליקציה לא נפתחת
**פתרון:**
1. בדוק שהטרמינל מציג: "Local URL: http://localhost:8501"
2. פתח את הקישור ידנית בדפדפן
3. נסה פורט אחר: `streamlit run app.py --server.port 8502`

## הרחבות עתידיות

- [ ] שמירת היסטוריית שאילתות
- [ ] ייצוא לפורמטים נוספים (Excel, PDF)
- [ ] גרפים ווויזואליזציות
- [ ] שאילתות מורכבות עם JOIN
- [ ] מעקב אחר ביצועים

## תמיכה

במקרה של בעיות:
1. בדוק את הלוגים בטרמינל
2. ודא שכל הקבצים במקום הנכון
3. נסה להריץ שאילתה פשוטה: `SHOW TABLES`

---

**נוצר על ידי:** GitHub Copilot  
**פרויקט:** Guy Mador - Shiba V.3.0  
**תאריך:** ספטמבר 2025