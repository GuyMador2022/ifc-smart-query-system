# 🤖 AI Integration Guide
# מדריך השימוש ב-AI עבור IFC Database Assistant

## 📋 סקירה כללית

האפליקציה תומכת כעת בתרגום שאלות בשפה טבעית לשאילתות SQL באמצעות OpenAI GPT API.

## ⚙️ הגדרה והפעלה

### 1. קבלת API Key מ-OpenAI
1. גש לאתר https://platform.openai.com/api-keys
2. צור חשבון או התחבר
3. צור API key חדש
4. העתק את המפתח

### 2. הגדרת קובץ .env
1. פתח את הקובץ `.env` בתיקיית הפרויקט
2. החלף את `your_openai_api_key_here` במפתח האמיתי שלך:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. הפעלת האפליקציה
```bash
cd "c:\Users\PC\Desktop\אפליקציות בפיתוח\ifc-2-duckdb-master - GUI\ifc-2-duckdb-master"
.\start_app.ps1
```

## 🎯 אופן השימוש

### שאלות בעברית:
- "כמה קירות יש בבניין?"
- "מה השטח הכולל של החללים?"
- "איזה חומרים משמשים בפרויקט?"
- "הראה לי את כל הדלתות"
- "כמה קומות יש בבניין?"

### שאלות באנגלית:
- "How many walls are in the building?"
- "What is the total area of all spaces?"
- "Show me all materials used"
- "List all doors and windows"
- "What's the average height of walls?"

## 🔧 הגדרות מתקדמות (בקובץ .env)

```env
# OpenAI Model Configuration
OPENAI_MODEL=gpt-4o-mini          # Model to use (gpt-4o-mini recommended for cost)
OPENAI_MAX_TOKENS=1000            # Maximum response length
OPENAI_TEMPERATURE=0.1            # Creativity level (0-2, lower = more focused)

# Application Settings
DEBUG_MODE=false                  # Enable debug logging
ENABLE_AI_TRANSLATION=true        # Enable/disable AI features
```

## 📊 מידע על עלויות

- **gpt-4o-mini**: ~$0.00015 לכל 1K tokens (מומלץ)
- **gpt-4**: ~$0.03 לכל 1K tokens (יותר מדויק, יקר יותר)
- **gpt-3.5-turbo**: ~$0.0015 לכל 1K tokens (זול, פחות מדויק)

💡 **העלות הצפויה**: כ-$0.01-0.05 לשאלה תלוי באורך התשובה

## 🚨 פתרון בעיות

### AI לא עובד?
1. ✅ בדוק שה-API key נכון בקובץ .env
2. ✅ ודא שיש לך זיכוי ב-OpenAI account
3. ✅ בדוק חיבור לאינטרנט
4. ✅ הפעל מחדש את האפליקציה

### שאלות לא מתורגמות נכון?
1. 🎯 נסה שאלות ספציפיות יותר
2. 🏗️ השתמש במונחי IFC (קירות, דלתות, חומרים)
3. 📝 כתוב בצורה ברורה ופשוטה

### שגיאות API?
- `API key not found`: בדוק את הקובץ .env
- `Rate limit exceeded`: חכה דקה ונסה שוב
- `Insufficient quota`: הוסף זיכוי לחשבון OpenAI

## 🔒 אבטחה

- ✅ קובץ .env מוגן ב-.gitignore
- ✅ רק שאילתות SELECT מותרות
- ✅ API key לא נשלח לשרת חיצוני

## 🎨 דוגמאות למשתמש

### שאלה פשוטה:
```
משתמש: "כמה קירות יש?"
AI: SELECT COUNT(*) FROM ifcwall;
תוצאה: 45 קירות
```

### שאלה מורכבת:
```
משתמש: "איזה חומרים משמשים בקירות?"
AI: SELECT DISTINCT m.Name FROM ifcwall w 
    JOIN ifcmaterial m ON w.material_id = m.ifc_id;
תוצאה: רשימת חומרים
```

## 📞 תמיכה

- 📧 לבעיות טכניות: פנה למפתח
- 💰 לבעיות עלויות: בדוק dashboard ב-OpenAI
- 🤖 לשיפור תרגומים: נסה ניסוחים שונים

---
*עודכן: ${new Date().toLocaleDateString('he-IL')} - גרסת AI 1.0*