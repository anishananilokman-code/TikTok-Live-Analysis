import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Najeehah International - TikTok Live Analytics",
    page_icon="📊",
    layout="wide"
)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Najeehah International")
st.sidebar.subheader("TikTok Live Analytics Tool")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Exploratory Data Analysis (EDA)",
        "Purchase Behavior Analysis",  
        "PLS-SEM Findings",
        "Monitoring Tool"
    ]
)

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
    
    
    rename_dict = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'gross revenue' in col_lower or 'revenue' in col_lower:
            rename_dict[col] = 'Gross Revenue'
        elif 'product clicks' in col_lower or 'clicks' in col_lower:
            rename_dict[col] = 'Product Clicks'
        elif 'avg' in col_lower and 'duration' in col_lower:
            rename_dict[col] = 'Avg. View Duration'
        elif 'ctr' in col_lower:
            rename_dict[col] = 'Ctr'
        elif 'ctor' in col_lower:
            rename_dict[col] = 'Ctor'
        elif 'like' in col_lower:
            rename_dict[col] = 'Likes'
        elif 'comment' in col_lower:
            rename_dict[col] = 'Comments'
        elif 'share' in col_lower:
            rename_dict[col] = 'Shares'
        elif 'viewer' in col_lower:
            rename_dict[col] = 'Viewers'
            
    df = df.rename(columns=rename_dict)
    
    numeric_cols = ['Gross Revenue', 'Product Clicks', 'Likes', 'Comments', 'Shares', 'Viewers', 'Ctr', 'Ctor', 'Avg. View Duration']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df = df.fillna(0)

    # ==================================
    # EXECUTIVE DASHBOARD
    # ==================================
    if page == "Executive Dashboard":
        st.title("📊 Executive Dashboard")
        st.markdown("Overview of the January and February TikTok Live baseline performance records for Najeehah International.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Likes", f"{df['Likes'].sum():,.0f}")
        c2.metric("Total Comments", f"{df['Comments'].sum():,.0f}")
        c3.metric("Total Shares", f"{df['Shares'].sum():,.0f}")
        c4.metric("Total Viewers", f"{df['Viewers'].sum():,.0f}")

        c5, c6, c7 = st.columns(3)
        c5.metric("Gross Revenue (RM)", f"RM {df['Gross Revenue'].sum():,.2f}")
        c6.metric("Average CTR", f"{df['Ctr'].mean():.4f}")
        c7.metric("Average CTOR", f"{df['Ctor'].mean():.4f}")

        st.divider()

        behaviour = pd.DataFrame({
            "Viewer Behaviour": ["Likes", "Comments", "Shares"],
            "Total Frequency": [df["Likes"].sum(), df["Comments"].sum(), df["Shares"].sum()]
        })

        fig = px.bar(
            behaviour,
            x="Viewer Behaviour",
            y="Total Frequency",
            title="Distribution of Active and Passive Viewer Actions",
            color="Viewer Behaviour",
            text_auto='.2s'
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==================================
    # EXPLORATORY DATA ANALYSIS (EDA)
    # ==================================
    elif page == "Exploratory Data Analysis (EDA)":
        st.title("📈 Exploratory Data Analysis (EDA)")
        st.markdown("Analysis of the distribution of main variables before structural modeling.")

        tab_dist, tab_corr, tab_scatter = st.tabs(["📊 Data Distribution", "🧮 Correlation Matrix", "📉 Bivariate Scatter Plots"])
        
        with tab_dist:
            st.subheader("Data Distribution & Outlier Detection")
            st.markdown("Select a variable to view distribution patterns (*skewness*) and outliers.")
            
            selected_col = st.selectbox("Select Variable:", numeric_cols)
            
            fig_dist = px.histogram(
                df, x=selected_col, 
                marginal="box", 
                title=f"Frequency Distribution & Outlier Characteristics for {selected_col}",
                color_discrete_sequence=['#FF4B4B']
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            st.info(f"Note: If the histogram tails off to the right, this supports the Chapter 4 observation that {selected_col} is highly positively skewed (viral-driven data).")

        with tab_corr:
            st.subheader("Correlation Matrix (Heatmap)")
            corr_matrix = df[['Likes', 'Comments', 'Shares', 'Viewers', 'Avg. View Duration', 'Product Clicks', 'Gross Revenue']].corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdBu_r',
                title="Linear Correlation Matrix Between TikTok Live Variables"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            st.success("Interpretation: Values approaching 1.00 indicate a strong linear relationship (e.g., Comments vs Viewers or Clicks vs Gross Revenue).")

        with tab_scatter:
            st.subheader("Bivariate Relational Scatter Plots")
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.scatter(df, x="Comments", y="Viewers", trendline="ols",
                                  title="Comments vs Viewers (Strong Linear Algorithmic Push)")
                st.plotly_chart(fig1, use_container_width=True)
                
                fig3 = px.scatter(df, x="Likes", y="Viewers", trendline="ols",
                                  title="Likes vs Viewers (Weak/Passive Trend)")
                st.plotly_chart(fig3, use_container_width=True)

            with col2:
                fig2 = px.scatter(df, x="Shares", y="Viewers", trendline="ols",
                                  title="Shares vs Viewers (High Organic Traffic Flow)")
                st.plotly_chart(fig2, use_container_width=True)
                
                if "Avg. View Duration" in df.columns:
                    fig4 = px.scatter(df, x="Avg. View Duration", y="Viewers", trendline="ols",
                                      title="Avg. View Duration vs Viewers (Scattered Distribution)")
                    st.plotly_chart(fig4, use_container_width=True)

    # ==================================
    # PURCHASE BEHAVIOR ANALYSIS
    # ==================================
    elif page == "Purchase Behavior Analysis":
        st.title("🛒 Purchase Behavior Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(df, x="Product Clicks", y="Gross Revenue", trendline="ols",
                             title="Product Clicks vs Gross Revenue")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig2 = px.scatter(df, x="Comments", y="Gross Revenue", trendline="ols",
                              title="Comments vs Gross Revenue (Direct Monetary Link)")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Conversion Efficiency Benchmarks")
        c1, c2 = st.columns(2)
        c1.metric("Average CTR Across Sessions", f"{df['Ctr'].mean():.4f}")
        c2.metric("Average CTOR Across Sessions", f"{df['Ctor'].mean():.4f}")

    # ==================================
    # PLS-SEM FINDINGS
    # ==================================
    elif page == "PLS-SEM Findings":
        st.title("🔬 Empirical PLS-SEM Statistical Output")
        st.markdown("Validated measurement and structural parameters matching Chapter 4 analysis.")

        st.subheader("1. Measurement Model Evaluation (Outer Model)")
        tab1, tab2 = st.columns(2)
        with tab1:
            st.markdown("**Formative Construct: Viewer Behaviour (Stimulus)**")
            st.table(pd.DataFrame({
                "Indicator": ["Comments", "Shares", "Likes"],
                "Outer Weight": [0.955, 0.932, 0.684],
                "VIF Status": ["4.120 (<5.0)", "3.754 (<5.0)", "1.850 (<5.0)"]
            }))
        with tab2:
            st.markdown("**Reflective Constructs (Organism & Response)**")
            st.table(pd.DataFrame({
                "Construct": ["Engagement", "Engagement", "Purchase Behavior", "Purchase Behavior"],
                "Indicator": ["Viewers", "Avg. View Duration", "Product Clicks", "Gross Revenue"],
                "Outer Loading": [0.975, 0.297, 0.986, 0.985]
            }))

        st.subheader("2. Structural Model Diagram (S-O-R Framework)")
        
        image_path = "image_3379fa.png"
        if os.path.exists(image_path):
            st.image(image_path, caption="PLS-SEM Empirical Structural Model Mapping for Najeehah International", use_container_width=True)
        else:
            st.warning(f"Sila pastikan fail imej '{image_path}' diletakkan di dalam folder projek yang sama untuk paparan visual rajah.")

        st.subheader("3. Core Structural Hypotheses Assessment")
        st.info("📊 **Explanatory Power Summary:** R² Engagement is **79.9%**, while R² Purchase Behavior is **88.5%**.")
        st.success("🎯 **Partial Mediation Confirmed:** Viewer Engagement significantly mediates the S-O-R pipeline (β = 0.405, p < 0.001). Comments act as the ultimate algorithmic trigger.")

    # ==================================
    # MONITORING TOOL (Objective 3)
    # ==================================
    elif page == "Monitoring Tool":
        st.title("🎯 Data-Driven TikTok Live Monitoring Tool")
        st.markdown("### Objective 3 Implementation: Real-Time Diagnostic Performance Tracker")
        st.markdown("This tool utilizes the mathematically validated empirical weights from the outer model execution ($W_{comments}=0.955, W_{shares}=0.932, W_{likes}=0.684$) to evaluate stream status.")

        with st.form("session_tracker"):
            st.markdown("##### Input Live Session Stream Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                in_comments = st.number_input("Current Comment Count", min_value=0, value=50, step=1)
            with col2:
                in_shares = st.number_input("Current Shares Count", min_value=0, value=10, step=1)
            with col3:
                in_likes = st.number_input("Current Likes Count", min_value=0, value=500, step=10)
                
            in_viewers = st.number_input("Current Concurrent Viewers Count", min_value=0, value=200, step=1)
            
            submit = st.form_submit_button(label="Run Real-Time Performance Diagnostic")

        if submit:
            empirical_score = (in_comments * 0.955) + (in_shares * 0.932) + (in_likes * 0.684)
            
            st.markdown("---")
            st.subheader("📊 Diagnostic Output Report")
            
            c1, c2 = st.columns(2)
            c1.metric("Validated Interaction Score", f"{empirical_score:,.2f}")
            
            predicted_purchase_index = (empirical_score * 0.513) + (in_viewers * 0.449)
            c2.metric("Predicted Purchase Index", f"{predicted_purchase_index:,.2f}")

            if empirical_score >= 800:
                st.success("🟢 **HIGH ALGORITHMIC VELOCITY SESSION**")
                st.markdown("""
                **Operational Status & Immediate Strategic Directives:**
                * **Algorithmic Trigger Status:** Stream is highly optimized. The TikTok recommendation engine is receiving dense interaction signals via high comment loads.
                * **Host Action Needed:** Shift focus directly to the commercial funnel. Execute hard sales pushes, explicitly call out pinned items, and announce flash coupon deals.
                * **Conversion Focus:** Direct current high volumes into immediate checkouts to maximize the active stream wave.
                """)
            elif empirical_score >= 250:
                st.warning("🟡 **MODERATE ENGAGEMENT GRIDLOCK**")
                st.markdown("""
                **Operational Status & Immediate Strategic Directives:**
                * **Algorithmic Trigger Status:** S-O-R pathway is under-stimulated. Interaction level is insufficient to push the stream aggressively onto the For You Page (FYP).
                * **Host Action Needed:** Immediately pause general product explanations. Pivot to an interactive engagement block. 
                * **Tactical Plays:** Ask direct, easy-to-answer questions to clear the comment bottleneck. Run a dedicated share-incentive target sequence to expand organic visibility.
                """)
            else:
                st.error("🔴 **CRITICAL SYSTEM STAGNATION**")
                st.markdown("""
                **Operational Status & Immediate Strategic Directives:**
                * **Algorithmic Trigger Status:** Low performance session. Passive consumption or drop-offs are occurring, severely suppressing structural reach metrics.
                * **Host Action Needed:** Total operational reset. Deploy instant high-energy hooks, initiate an unexpected flash giveaway, or launch a mini-game.
                * **Tactical Plays:** Explicitly mandate chat activities ("Drop a '1' in the chat if you hear me!") to force interaction data points back into the platform distribution pipeline.
                """)

else:
    st.title("📊 Najeehah International - TikTok Live Analytics Dashboard")
    st.markdown("---")
    st.info("Please upload your TikTok Live session dataset (`.xlsx` or `.csv`) via the sidebar layout to initialize the interactive analytics dashboard.")