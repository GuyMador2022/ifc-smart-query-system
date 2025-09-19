# 🛠️ פתרון בעיות נפוצות ב-Streamlit Cloud

## ❌ שגיאות Dependencies

### שגיאה: `ModuleNotFoundError: No module named 'dotenv'`
**פתרון**: הוספתי try/except - האפליקציה תעבוד בלי dotenv

### שגיאה: `ModuleNotFoundError: No module named 'ifcopenshell'`
**פתרון**: 
1. השתמש ב-`requirements_minimal.txt` במקום `requirements.txt`
2. או הסר את ifcopenshell מה-requirements אם לא נדרש

### שגיאה: `ModuleNotFoundError: No module named 'query_logger'`
**פתרון**: הוספתי fallback - Analytics יהיה מושבת אבל האפליקציה תעבוד

## 🔧 Streamlit Cloud Setup

### 1. הגדרת האפליקציה
```
Repository: GuyMador2022/ifc-smart-query-system
Branch: main
Main file path: app.py
```

### 2. Dependencies Options
**אופציה 1 - מלא (מומלץ)**:
- השתמש ב-`requirements.txt`

**אופציה 2 - מינימלי (אם יש בעיות)**:
- שנה ל-`requirements_minimal.txt`

### 3. סביבת משתנים (Secrets)
```toml
# אופציונלי - רק אם רוצים AI
OPENAI_API_KEY = "sk-your-key-here"
ENABLE_AI_TRANSLATION = "true"

# הגדרות אפליקציה
APP_TITLE = "IFC Smart Query System"
```

## 🚀 מצבי פעולה

### מצב מלא (עם כל התכונות)
- ✅ כל המודולים זמינים
- ✅ AI translation עובד
- ✅ Analytics זמין
- ✅ לוגים פועלים

### מצב מינימלי (cloud fallback)
- ✅ ממשק בסיסי עובד
- ⚠️ AI ללא API key
- ⚠️ Analytics מושבת
- ✅ העלאת database עובדת

## 📊 בדיקת סטטוס

כשהאפליקציה רצה, בדוק:

1. **הודעות שגיאה**: אם אין - הכל בסדר
2. **טאב Analytics**: אם זמין - הלוגים עובדים
3. **שאלה חופשית**: אם יש תיבת טקסט - AI זמין
4. **העלאת קבצים**: אמור לעבוד תמיד

## 🔄 אם יש בעיות

### צעד 1: בדוק לוגים
ב-Streamlit Cloud Dashboard → לוגים

### צעד 2: שנה requirements
אם יש שגיאת dependencies, עבור ל-`requirements_minimal.txt`

### צעד 3: הסר תכונות
- הסר `OPENAI_API_KEY` אם לא נדרש
- Analytics יהיה מושבת אוטומטית אם יש בעיה

## ✅ הצלחה!

אם האפליקציה נטענת ואתה רואה:
```
🏗️ מערכת ניתוח נתוני IFC
📤 אנא העלה קובץ מסד נתונים DuckDB
```

**זה מושלם!** המערכת מוכנה לשימוש.

## 📞 עזרה נוספת

אם עדיין יש בעיות, בדוק:
1. GitHub repository: https://github.com/GuyMador2022/ifc-smart-query-system
2. לוגים ב-Streamlit Cloud
3. הגדרות Secrets נכונות

---

**💡 זכור**: האפליקציה תעבוד גם ללא כל התכונות המתקדמות!