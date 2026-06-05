import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Najeehah International - Business Performance",
    page_icon="🛒",
    layout="wide"
)

# =========================
# SIDEBAR FILE UPLOADER
# =========================
st.sidebar.title("Najeehah International")
st.sidebar.subheader("Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload Live Sessions Dataset",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    # Read Dataset
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
        
    df.columns = df.columns.str.strip()
    
    # Dynamic column mapping (Fixed to prevent duplication errors)
    rename_dict = {}
    for col in df.columns:
        col_lower = col.lower()
        
        if 'gross' in col_lower or 'reve' in col_lower:
            rename_dict[col] = 'Gross Revenue'
        elif 'product' in col_lower or 'cli' in col_lower:
            rename_dict[col] = 'Product Clicks'
        elif 'ctr' in col_lower:
            rename_dict[col] = 'Ctr'
        elif 'ctor' in col_lower:
            rename_dict[col] = 'Ctor'
        elif 'comment' in col_lower:
            rename_dict[col] = 'Comments'
        elif 'viewer' in col_lower:
            rename_dict[col] = 'Viewers'
        elif 'like' in col_lower:
            rename_dict[col] = 'Likes'
        elif 'share' in col_lower:
            rename_dict[col] = 'Shares'
        elif 'date' in col_lower:
            rename_dict[col] = 'Session Date'
        elif 'time' in col_lower or 'pukul' in col_lower or 'start' in col_lower:
            rename_dict[col] = 'Start Time'
        elif 'avg' in col_lower or 'view d' in col_lower:
            rename_dict[col] = 'Avg. View Duration'
        elif 'duration' in col_lower or 'tempoh' in col_lower:
            rename_dict[col] = 'Stream Duration'
            
    df = df.rename(columns=rename_dict)
    
    # Clean string data to numeric values for key metrics
    numeric_cols = ['Gross Revenue', 'Product Clicks', 'Comments', 'Viewers', 'Ctr', 'Ctor', 'Avg. View Duration', 'Likes', 'Shares']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df = df.fillna(0)
    
    # Sort by date chronologically
    if 'Session Date' in df.columns:
        df['Session Date'] = df['Session Date'].astype(str)
        df = df.sort_values(by='Session Date', ascending=True)
    
    # Generate unique X-axis label combining Date and Start Time
    df['Session_Label'] = df['Session Date'] if 'Session Date' in df.columns else range(1, len(df) + 1)
    if 'Start Time' in df.columns:
        df['Session_Label'] = df['Session Date'] + " (" + df['Start Time'].astype(str) + ")"

    # ==================================
    # MAIN DISPLAY: BUSINESS PERFORMANCE
    # ==================================
    st.title("🛒 4.6.5 Business Performance Dashboard")
    st.markdown("### How Viewer Behaviour Contributes to Business Outcomes")
    st.markdown("This targeted interface monitors commercial performance and evaluates how viewer activities directly drive business results, bridging empirical data with the S-O-R framework.")

    st.divider()

    # 1. KPI Cards Component
    kp1, kp2, kp3, kp4, kp5 = st.columns(5)
    kp1.metric("Total Gross Revenue", f"RM {df['Gross Revenue'].sum():,.2f}")
    kp2.metric("Total Product Clicks", f"{df['Product Clicks'].sum():,.0f}")
    kp3.metric("Average CTR", f"{df['Ctr'].mean():.4f}")
    kp4.metric("Average CTOR", f"{df['Ctor'].mean():.4f}")
    kp5.metric("Total Sessions Analyzed", f"{len(df)}")

    st.divider()

    # 2. S-O-R Framework Conversion Funnel
    st.subheader("🎯 Empirical S-O-R Conversion Pipeline Funnel")
    st.markdown("Visualization of user interaction flowing through psychological phases to generate monetary outcomes.")
    
    funnel_data = dict(
        number=[df['Comments'].sum(), df['Viewers'].sum(), df['Product Clicks'].sum(), df['Gross Revenue'].sum()],
        stage=["Stimulus: Comments (Count)", "Organism: Viewer Engagement (Viewers)", "Response: Product Clicks (Count)", "Outcome: Gross Revenue (RM)"]
    )
    fig_funnel = px.funnel(funnel_data, x='number', y='stage', color_discrete_sequence=['#FF4B4B'])
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.divider()

    # 3. INTERACTIVE REVENUE TREND & COMPARATIVE BEHAVIOR ANALYSIS
    st.subheader("📈 Chronological Trend & Comparative Behavior Analysis")
    st.markdown("Compare monetary yields alongside multiple dynamic behavioral metrics to observe co-movement patterns.")
    
    t1, t2 = st.columns([2, 3])
    
    with t1:
        fig_line = px.line(
            df, 
            x="Session_Label", 
            y="Gross Revenue", 
            title="Baseline Business Outcome: Gross Revenue Trend", 
            labels={"Session_Label": "Session Date & Start Time", "Gross Revenue": "Revenue (RM)"},
            markers=True
        )
        fig_line.update_traces(line_color='#FF4B4B')
        st.plotly_chart(fig_line, use_container_width=True)
        
    with t2:
        available_behaviors = ['Comments', 'Likes', 'Shares', 'Viewers', 'Product Clicks']
        
        selected_behaviors = st.multiselect(
            "Select Viewer Behavior Metrics for Trend Comparison:",
            options=available_behaviors,
            default=['Comments', 'Product Clicks']
        )
        
        if selected_behaviors:
            fig_compare = px.line(
                df,
                x="Session_Label",
                y=selected_behaviors,
                title="Comparative Analysis: Dynamic Viewer Behavior Trends",
                labels={"Session_Label": "Session Date & Start Time", "value": "Metric Count", "variable": "Behavior Metric"},
                markers=True
            )
            st.plotly_chart(fig_compare, use_container_width=True)
        else:
            st.warning("Please select at least one viewer behavior metric from the dropdown above to display the comparison trend.")

    st.divider()

    # 4. Engagement vs Outcomes (Scatter Plots)
    st.subheader("Bivariate Engagement vs Business Outcomes Analysis")
    sc1, sc2 = st.columns(2)
    with sc1:
        fig_sc1 = px.scatter(df, x="Comments", y="Gross Revenue", trendline="ols", title="Engagement vs Revenue (Comments vs Gross Revenue)")
        st.plotly_chart(fig_sc1, use_container_width=True)
        st.caption("Expected finding: Sessions with higher comment activity tend to generate higher gross revenue.")
    with sc2:
        fig_sc2 = px.scatter(df, x="Comments", y="Product Clicks", trendline="ols", title="Engagement vs Action (Comments vs Product Clicks)")
        st.plotly_chart(fig_sc2, use_container_width=True)
        st.caption("Expected finding: Higher levels of commenting behaviour are associated with increased product clicks.")

    st.divider()

    # 5. Top Performing Sessions Ranked Table
    st.subheader("Top Performing Sessions (Benchmarking Dataset)")
    
    table_cols = []
    table_names = []
    
    if 'Session Date' in df.columns:
        table_cols.append('Session Date')
        table_names.append('Date')
    if 'Start Time' in df.columns:
        table_cols.append('Start Time')
        table_names.append('Start Time')
    if 'Stream Duration' in df.columns:
        table_cols.append('Stream Duration')
        table_names.append('Duration')
        
    table_cols.extend(['Gross Revenue', 'Product Clicks', 'Comments'])
    table_names.extend(['Revenue (RM)', 'Product Clicks', 'Comments'])
    
    top_sessions = df[table_cols].sort_values(by='Gross Revenue', ascending=False).head(10)
    top_sessions.columns = table_names
    
    st.dataframe(top_sessions.style.format({'Revenue (RM)': 'RM {:,.2f}'}), use_container_width=True)

else:
    st.title("📊 Najeehah International - TikTok Live Business Performance")
    st.markdown("---")
    st.info("Please upload your TikTok Live session dataset (`.xlsx` or `.csv`) via the sidebar layout to display the performance dashboard.")
