# frontend/components/progress_charts.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show_progress_charts(username, get_weight_history, log_weight, get_workout_stats, delete_weight_entry):
    """Display progress charts for weight and workouts"""
    
    st.markdown("## 📊 Your Progress Dashboard")
    st.markdown("Track your fitness journey over time")
    
    tab1, tab2, tab3 = st.tabs(["⚖️ Weight Tracking", "🏋️ Workout Log", "📈 Stats Summary"])
    
    # ============================================
    # TAB 1: WEIGHT TRACKING
    # ============================================
    
    with tab1:
        st.markdown("### Track Your Weight")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input for new weight
            new_weight = st.number_input(
                "Enter your weight (kg)",
                min_value=30.0,
                max_value=300.0,
                step=0.5,
                key="chart_new_weight"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("➕ Log Weight", key="chart_log_weight_btn"):
                    if new_weight:
                        log_weight(username, new_weight)
                        st.success(f"Weight {new_weight} kg logged for today!")
                        st.rerun()
        
        with col2:
            st.markdown("### 📅 Filter")
            days = st.selectbox(
                "Show last",
                [30, 60, 90, 180, 365],
                index=2,
                key="chart_weight_days"
            )
        
        # Display weight chart
        weight_history = get_weight_history(username, days)
        
        if weight_history and len(weight_history) > 1:
            df = pd.DataFrame(weight_history)
            
            # Calculate stats
            start_weight = df.iloc[0]['weight']
            current_weight = df.iloc[-1]['weight']
            change = current_weight - start_weight
            change_percent = (change / start_weight) * 100
            
            # Display metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Starting Weight", f"{start_weight} kg")
            with metric_col2:
                st.metric("Current Weight", f"{current_weight} kg", 
                         delta=f"{change:+.1f} kg" if change != 0 else None)
            with metric_col3:
                st.metric("Total Change", f"{change_percent:+.1f}%")
            
            # Create line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['weight'],
                mode='lines+markers',
                name='Weight',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=6, color='#27ae60')
            ))
            
            fig.update_layout(
                title="Weight Progress Over Time",
                xaxis_title="Date",
                yaxis_title="Weight (kg)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            with st.expander("View Weight History Table"):
                df_display = df.copy()
                df_display['change'] = df_display['weight'].diff().round(1)
                st.dataframe(df_display, use_container_width=True)
                
                # Delete entry option
                st.markdown("### Delete Entry")
                date_to_delete = st.selectbox(
                    "Select date to delete",
                    df['date'].tolist(),
                    key="chart_delete_weight_date"
                )
                if st.button("🗑️ Delete Selected Entry", key="chart_delete_weight"):
                    delete_weight_entry(username, date_to_delete)
                    st.success(f"Deleted entry for {date_to_delete}")
                    st.rerun()
        else:
            st.info("Not enough data yet. Log at least 2 weight entries to see your progress chart!")
            st.markdown("**Tips:**")
            st.markdown("- Log your weight weekly (same day, same time)")
            st.markdown("- Morning weight after bathroom is most consistent")
    
    # ============================================
    # TAB 2: WORKOUT LOG
    # ============================================
    
    with tab2:
        st.markdown("### Log Your Workout")
        
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_name = st.text_input("Exercise Name", placeholder="e.g., Bench Press", key="chart_exercise_name")
            sets = st.number_input("Sets", min_value=1, max_value=10, value=3, key="chart_workout_sets")
        
        with col2:
            reps = st.number_input("Reps", min_value=1, max_value=50, value=10, key="chart_workout_reps")
            weight_used = st.number_input("Weight (kg)", min_value=0.0, step=2.5, key="chart_workout_weight")
        
        if st.button("💪 Log Workout", key="chart_log_workout_btn"):
            if exercise_name:
                from backend.database import log_workout_completion
                log_workout_completion(username, exercise_name, sets, reps, weight_used)
                st.success(f"Logged: {exercise_name} - {sets}×{reps} @ {weight_used}kg")
                st.rerun()
            else:
                st.warning("Please enter an exercise name")
        
        st.markdown("---")
        st.markdown("### Recent Workout Activity")
        
        chart_days = st.selectbox("Show last", [7, 14, 30, 60], index=1, key="chart_workout_days")
        workout_stats = get_workout_stats(username, chart_days)
        
        if workout_stats:
            df_workouts = pd.DataFrame(workout_stats)
            
            # Create bar chart
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_workouts['date'],
                y=df_workouts['count'],
                name='Workouts',
                marker_color='#3498db'
            ))
            
            fig2.update_layout(
                title="Workout Frequency",
                xaxis_title="Date",
                yaxis_title="Number of Exercises Logged",
                height=350
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            total_workouts = df_workouts['count'].sum()
            avg_per_day = total_workouts / chart_days
            st.metric("Total Exercises Logged", total_workouts, 
                     delta=f"{avg_per_day:.1f} per day" if chart_days > 0 else None)
        else:
            st.info("No workouts logged yet. Start logging your workouts to see charts!")
    
    # ============================================
    # TAB 3: STATS SUMMARY
    # ============================================
    
    with tab3:
        st.markdown("### Your Fitness Summary")
        
        # Weight stats
        weight_data = get_weight_history(username, 90)
        workout_data = get_workout_stats(username, 30)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if weight_data and len(weight_data) > 0:
                start_w = weight_data[0]['weight']
                current_w = weight_data[-1]['weight']
                st.metric("Weight Change", f"{current_w - start_w:+.1f} kg",
                         delta=f"{((current_w - start_w)/start_w*100):+.1f}%")
            else:
                st.metric("Weight Change", "N/A")
        
        with col2:
            if workout_data:
                total = sum(w['count'] for w in workout_data)
                st.metric("Total Exercises (30d)", total)
            else:
                st.metric("Total Exercises (30d)", "0")
        
        with col3:
            if weight_data and len(weight_data) >= 2:
                first = weight_data[0]['weight']
                last = weight_data[-1]['weight']
                trend = "📉" if last < first else "📈" if last > first else "➡️"
                st.metric("Trend", trend)
            else:
                st.metric("Trend", "Not enough data")
        
        with col4:
            # Calculate consistency (days with workouts vs total days)
            if workout_data:
                days_with_workouts = len(workout_data)
                st.metric("Active Days (30d)", f"{days_with_workouts}/30")
            else:
                st.metric("Active Days (30d)", "0/30")
        
        st.markdown("---")
        st.markdown("### 💡 Tips for Better Progress")
        st.markdown("""
        - 📅 **Log consistently**: Same day, same time each week for weight
        - 📝 **Track workouts**: Record every set to see improvement
        - 📊 **Watch trends**: Focus on direction, not daily fluctuations
        - 💧 **Hydration matters**: Drink water before weighing
        - 😴 **Sleep impacts weight**: Morning weigh-ins are most accurate
        """)