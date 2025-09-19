#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Admin Dashboard for Query Analytics
ממשק ניהול מתקדם לצפייה ב-analytics של שאלות משתמשים
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from query_logger import query_logger
from typing import Dict, List

def render_analytics_dashboard():
    """רינדור דשבורד ניתוח נתונים"""
    
    st.header("📊 דשבורד ניתוח שאלות משתמשים")
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "מתאריך",
            value=datetime.now() - timedelta(days=7),
            max_value=datetime.now()
        )
        
    with col2:
        end_date = st.date_input(
            "עד תאריך", 
            value=datetime.now(),
            max_value=datetime.now()
        )
        
    with col3:
        if st.button("🔄 רענן נתונים", use_container_width=True):
            st.rerun()
    
    # Load data for date range
    all_queries = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        daily_queries = query_logger.load_queries_by_date(date_str)
        all_queries.extend(daily_queries)
        current_date += timedelta(days=1)
    
    if not all_queries:
        st.warning("❌ לא נמצאו שאלות בטווח התאריכים שנבחר")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_queries)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 סה\"כ שאלות",
            len(df),
            delta=None
        )
        
    with col2:
        success_rate = (df['success'].sum() / len(df) * 100) if len(df) > 0 else 0
        st.metric(
            "✅ אחוז הצלחה",
            f"{success_rate:.1f}%",
            delta=None
        )
        
    with col3:
        ai_usage = (df['ai_translation_used'].sum() / len(df) * 100) if len(df) > 0 else 0
        st.metric(
            "🤖 שימוש ב-AI",
            f"{ai_usage:.1f}%",
            delta=None
        )
        
    with col4:
        avg_time = df['execution_time_ms'].mean() if 'execution_time_ms' in df.columns else 0
        st.metric(
            "⏱️ זמן ממוצע",
            f"{avg_time:.0f}ms",
            delta=None
        )
    
    st.divider()
    
    # Charts in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 מגמות זמן", "👥 מקצועות", "📊 סוגי שאלות", 
        "🔍 שאלות פופולריות", "💾 ייצוא נתונים"
    ])
    
    with tab1:
        # Time series charts
        st.subheader("📈 מגמות לאורך זמן")
        
        # Daily questions count
        daily_counts = df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        fig_daily = px.line(
            daily_counts, 
            x='date', 
            y='count',
            title="מספר שאלות ליום",
            labels={'date': 'תאריך', 'count': 'מספר שאלות'}
        )
        fig_daily.update_layout(
            xaxis_title="תאריך",
            yaxis_title="מספר שאלות",
            font=dict(size=12)
        )
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Hourly distribution
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        fig_hourly = px.bar(
            hourly_counts,
            x='hour',
            y='count', 
            title="התפלגות שאלות לפי שעות היום",
            labels={'hour': 'שעה', 'count': 'מספר שאלות'}
        )
        fig_hourly.update_layout(
            xaxis_title="שעה ביום",
            yaxis_title="מספר שאלות",
            font=dict(size=12)
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with tab2:
        # Profession analysis
        st.subheader("👥 ניתוח לפי מקצועות")
        
        if 'profession' in df.columns and df['profession'].notna().any():
            profession_counts = df['profession'].value_counts()
            
            fig_prof = px.pie(
                values=profession_counts.values,
                names=profession_counts.index,
                title="התפלגות שאלות לפי מקצועות"
            )
            st.plotly_chart(fig_prof, use_container_width=True)
            
            # Success rate by profession
            prof_success = df.groupby('profession')['success'].agg(['count', 'sum']).reset_index()
            prof_success['success_rate'] = (prof_success['sum'] / prof_success['count'] * 100)
            
            fig_success = px.bar(
                prof_success,
                x='profession',
                y='success_rate',
                title="אחוז הצלחה לפי מקצוע",
                labels={'profession': 'מקצוע', 'success_rate': 'אחוז הצלחה'}
            )
            st.plotly_chart(fig_success, use_container_width=True)
        else:
            st.info("📝 אין נתוני מקצועות זמינים")
    
    with tab3:
        # Query types analysis
        st.subheader("📊 ניתוח סוגי שאלות")
        
        query_type_counts = df['query_type'].value_counts()
        
        fig_types = px.bar(
            x=query_type_counts.index,
            y=query_type_counts.values,
            title="התפלגות סוגי שאלות",
            labels={'x': 'סוג שאלה', 'y': 'מספר שאלות'}
        )
        fig_types.update_layout(
            xaxis_title="סוג שאלה",
            yaxis_title="מספר שאלות",
            font=dict(size=12)
        )
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Success rate by query type
        type_success = df.groupby('query_type')['success'].agg(['count', 'sum']).reset_index()
        type_success['success_rate'] = (type_success['sum'] / type_success['count'] * 100)
        
        fig_type_success = px.bar(
            type_success,
            x='query_type',
            y='success_rate',
            title="אחוז הצלחה לפי סוג שאלה",
            labels={'query_type': 'סוג שאלה', 'success_rate': 'אחוז הצלחה'}
        )
        st.plotly_chart(fig_type_success, use_container_width=True)
    
    with tab4:
        # Popular questions
        st.subheader("🔍 שאלות פופולריות")
        
        # Most asked questions
        question_counts = df['user_question'].value_counts().head(10)
        
        if len(question_counts) > 0:
            st.write("**השאלות הכי פופולריות:**")
            for i, (question, count) in enumerate(question_counts.items(), 1):
                with st.expander(f"{i}. {question[:60]}... ({count} פעמים)"):
                    st.write(f"**שאלה מלאה:** {question}")
                    st.write(f"**נשאלה:** {count} פעמים")
                    
                    # Show related queries
                    question_data = df[df['user_question'] == question]
                    success_rate = (question_data['success'].sum() / len(question_data) * 100)
                    st.write(f"**אחוז הצלחה:** {success_rate:.1f}%")
                    
                    if 'profession' in question_data.columns:
                        professions = question_data['profession'].value_counts()
                        if len(professions) > 0:
                            st.write(f"**מקצועות שואלים:** {', '.join(professions.index)}")
        else:
            st.info("📝 אין נתוני שאלות זמינים")
    
    with tab5:
        # Data export
        st.subheader("💾 ייצוא נתונים")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 ייצוא ל-CSV", use_container_width=True):
                csv_data = df.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    label="📥 הורד קובץ CSV",
                    data=csv_data,
                    file_name=f"query_analytics_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
                
        with col2:
            if st.button("📊 ייצוא ל-Excel", use_container_width=True):
                try:
                    # Create Excel file
                    output_file = f"query_analytics_{start_date}_{end_date}.xlsx"
                    
                    with pd.ExcelWriter(output_file) as writer:
                        df.to_excel(writer, sheet_name='Raw Data', index=False)
                        
                        # Summary sheet
                        summary_data = {
                            'מטריקה': ['סה"כ שאלות', 'אחוז הצלחה', 'שימוש ב-AI', 'זמן ממוצע'],
                            'ערך': [len(df), f"{success_rate:.1f}%", f"{ai_usage:.1f}%", f"{avg_time:.0f}ms"]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    st.success(f"✅ קובץ Excel נשמר: {output_file}")
                    
                except Exception as e:
                    st.error(f"❌ שגיאה בייצוא Excel: {e}")
        
        # Raw data table
        st.subheader("📋 נתונים גולמיים")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            success_filter = st.selectbox("סינון לפי הצלחה", ["הכל", "הצליח", "נכשל"])
            
        with col2:
            if 'profession' in df.columns:
                profession_filter = st.selectbox(
                    "סינון לפי מקצוע", 
                    ["הכל"] + list(df['profession'].dropna().unique())
                )
            else:
                profession_filter = "הכל"
                
        with col3:
            query_type_filter = st.selectbox(
                "סינון לפי סוג שאלה",
                ["הכל"] + list(df['query_type'].unique())
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if success_filter == "הצליח":
            filtered_df = filtered_df[filtered_df['success'] == True]
        elif success_filter == "נכשל":
            filtered_df = filtered_df[filtered_df['success'] == False]
            
        if profession_filter != "הכל" and 'profession' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['profession'] == profession_filter]
            
        if query_type_filter != "הכל":
            filtered_df = filtered_df[filtered_df['query_type'] == query_type_filter]
        
        # Display filtered data
        st.dataframe(
            filtered_df[['timestamp', 'user_question', 'profession', 'query_type', 'success', 'execution_time_ms']],
            use_container_width=True,
            height=400
        )
        
        st.write(f"📊 מציג {len(filtered_df)} מתוך {len(df)} שאלות")

def render_live_analytics():
    """צגה חיה של analytics"""
    
    st.subheader("🔴 מעקב חי")
    
    # Auto-refresh every 30 seconds
    placeholder = st.empty()
    
    # Get today's stats
    today = datetime.now().strftime('%Y-%m-%d')
    today_stats = query_logger.get_daily_stats(today)
    
    with placeholder.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 שאלות היום", today_stats.get("total_queries", 0))
            
        with col2:
            success_count = today_stats.get("successful_queries", 0)
            st.metric("✅ הצליחו", success_count)
            
        with col3:
            ai_count = today_stats.get("ai_translations", 0)
            st.metric("🤖 AI", ai_count)
            
        with col4:
            avg_time = today_stats.get("avg_execution_time", 0)
            st.metric("⏱️ זמן ממוצע", f"{avg_time:.0f}ms")
    
    # Recent questions
    if today_stats.get("total_queries", 0) > 0:
        st.subheader("📝 שאלות אחרונות")
        
        recent_queries = query_logger.load_queries_by_date(today)
        recent_queries = sorted(recent_queries, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        
        for query in recent_queries:
            with st.expander(f"🕐 {query.get('timestamp', '')[:19]} - {query.get('user_question', '')[:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**שאלה:** {query.get('user_question', '')}")
                    st.write(f"**מקצוע:** {query.get('profession', 'לא מוגדר')}")
                    st.write(f"**סוג:** {query.get('query_type', 'לא מוגדר')}")
                    
                with col2:
                    status = "✅ הצליח" if query.get('success') else "❌ נכשל"
                    st.write(f"**סטטוס:** {status}")
                    st.write(f"**AI:** {'כן' if query.get('ai_translation_used') else 'לא'}")
                    
                    if query.get('execution_time_ms'):
                        st.write(f"**זמן ביצוע:** {query.get('execution_time_ms'):.0f}ms")

if __name__ == "__main__":
    st.set_page_config(page_title="📊 Analytics Dashboard", layout="wide")
    
    st.title("📊 Dashboard Analytics - מערכת ניתוח שאלות")
    
    tab1, tab2 = st.tabs(["📈 Analytics", "🔴 Live"])
    
    with tab1:
        render_analytics_dashboard()
        
    with tab2:
        render_live_analytics()