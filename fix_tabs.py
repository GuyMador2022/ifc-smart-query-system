#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Quick Fix for Tab Order
תיקון מהיר לסדר הטאבים
"""

import re

def fix_app_file():
    """תיקון קובץ app.py"""
    
    print("🔧 מתקן קובץ app.py...")
    
    try:
        # קריאת הקובץ
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("📖 קרא את הקובץ")
        
        # מציאת הבלוק הבעייתי
        old_tabs_pattern = r'tab1, tab2, tab3, tab4, tab5 = st\.tabs\(\[\s*"[^"]*שאלה חופשית",[^]]*\]\)'
        
        new_tabs_block = '''tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 שאלה חופשית",
        "👷‍♀️ אדריכל", 
        "🔧 מהנדס", 
        "💼 בעל פרויקט",
        "📊 Analytics"
    ])'''
        
        # החלפה
        content = re.sub(old_tabs_pattern, new_tabs_block, content, flags=re.DOTALL)
        
        # תיקון התוכן של הטאבים - ודא שטאב 1 הוא שאלה חופשית
        # חיפוש הדפוס של with tab1:
        old_tab1_pattern = r'# Free form question tab \(default\)\s*with tab1:\s*render_chat_interface\(\)'
        new_tab1_block = '''# Free form question tab (default)
    with tab1:
        render_chat_interface()'''
        
        if "# Free form question tab (default)" in content:
            content = re.sub(old_tab1_pattern, new_tab1_block, content, flags=re.DOTALL)
        else:
            # אם לא קיים, נוסיף אותו
            content = content.replace(
                "with tab1:\n        render_chat_interface()",
                "# Free form question tab (default)\n    with tab1:\n        render_chat_interface()"
            )
        
        # תיקון טאבים אחרים
        content = content.replace('render_profession_interface("�‍♀️ אדריכל")', 'render_profession_interface("👷‍♀️ אדריכל")')
        content = content.replace('render_profession_interface("� מהנדס")', 'render_profession_interface("🔧 מהנדס")')
        
        # שמירה
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("✅ הקובץ תוקן בהצלחה!")
        print("💬 טאב 'שאלה חופשית' הוא עכשיו ברירת המחדל")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    fix_app_file()