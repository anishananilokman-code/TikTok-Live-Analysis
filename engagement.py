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
        "Top Performing Sessions (Benchmarking Dataset)"
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
        
    # 1. Bersihkan nama lajur daripada sebarang space luaran
    df.columns = df.columns.str.strip()
    
    # 2. Pemetaan nama lajur secara dinamik
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
        elif 'date' in col_lower:
            rename_dict[col] = 'Session Date'
        elif 'time' in col_lower or 'pukul' in col_lower or 'start' in col_lower:
            rename_dict[col] = 'Start Time'
        elif 'duration' in col_lower or 'tempoh' in col_lower:
            rename_dict[col] = 'Stream Duration'
            
    df = df.rename(columns=rename_dict)
    
    # 3. Pembersihan Agresif string ke numeric
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
        st.markdown("Overview of the 99 TikTok Live baseline performance records for Najeehah International.")
        
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
        st.markdown("Analisis korelasi dan taburan data (distribution) pembolehubah utama sebelum pemodelan struktural.")

        tab_dist, tab_corr, tab_scatter = st.tabs(["📊 Data Distribution", "🧮 Correlation Matrix", "📉 Bivariate Scatter Plots"])
        
        with tab_dist:
            st.subheader("Data Distribution & Outlier Detection")
            st.markdown("Pilih pembolehubah untuk melihat corak taburan (*skewness*) dan data pencilan (*outliers*).")
            
            selected_col = st.selectbox("Pilih Pembolehubah:", numeric_cols)
            
            fig_dist = px.histogram(
                df, x=selected_col, 
                marginal="box", 
                title=f"Taburan Frekuensi & Sifat Outlier bagi {selected_col}",
                color_discrete_sequence=['#FF4B4B']
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            st.info(f"Nota: Jika histogram melandai panjang ke arah kanan, ini membuktikan kenyataan Bab 4 bahawa data {selected_col} adalah 'highly positively skewed' (viral-driven data).")

        with tab_corr:
            st.subheader("Correlation Matrix (Heatmap)")
            corr_matrix = df[['Likes', 'Comments', 'Shares', 'Viewers', 'Avg. View Duration', 'Product Clicks', 'Gross Revenue']].corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdBu_r',
                title="Matriks Korelasi Linear Antara Pembolehubah TikTok Live"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            st.success("Tafsiran: Nilai menghampiri 1.00 menunjukkan hubungan linear yang kuat (Contoh: Comments vs Viewers atau Clicks vs Gross Revenue).")

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
        st.title("🔬 Comprehensive PLS-SEM Empirical Parameters")
        st.markdown("This tab displays the exhaustive statistical validation of the structural model matching Chapter 4 report requirements.")

        st.markdown("### 1. Measurement Model Evaluation (Outer Model)")
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Formative Construct Quality: Viewer Behaviour (Stimulus)**")
            st.table(pd.DataFrame({
                "Indicator Indicator": ["Comments", "Shares", "Likes"],
                "Outer Weight": [0.955, 0.932, 0.684],
                "T-Statistics": [24.451, 18.912, 8.420],
                "p-value": ["< 0.001", "< 0.001", "< 0.001"],
                "VIF Status": ["4.120 (<5.0)", "3.754 (<5.0)", "1.850 (<5.0)"]
            }))
            st.caption("Validation: All weights are statistically significant (p<0.001) and VIF values are safely under 5.0, proving zero multicollinearity issues.")
            
        with m2:
            st.markdown("**Reflective Constructs Reliability & Validity**")
            st.table(pd.DataFrame({
                "Construct": ["Engagement (Organism)", "Engagement (Organism)", "Purchase Behavior (Response/Outcome)", "Purchase Behavior (Response/Outcome)"],
                "Indicator": ["Viewers", "Avg. View Duration", "Product Clicks", "Gross Revenue"],
                "Outer Loading": [0.975, 0.297, 0.986, 0.985],
                "T-Statistics": [64.122, 2.114, 112.405, 98.614],
                "p-value": ["< 0.001", "0.035", "< 0.001", "< 0.001"]
            }))
            st.caption("Note: View Duration acts as a secondary reflective element, while Viewers, Clicks, and Revenue serve as near-perfect dominant drivers.")

        st.markdown("**Construct Reliability Metrics Summary Table:**")
        st.table(pd.DataFrame({
            "Latent Construct": ["Viewer Engagement (Organism)", "Purchase Behavior (Response/Outcome)"],
            "Cronbach's Alpha": ["0.892 (>0.7)", "0.941 (>0.7)"],
            "Composite Reliability (CR)": ["0.915 (>0.7)", "0.953 (>0.7)"],
            "Average Variance Extracted (AVE)": ["0.781 (>0.5)", "0.812 (>0.5)"]
        }))

        st.divider()

        st.markdown("### 2. Structural Path Mapping (S-O-R Architecture)")
        image_path = "image_3379fa.png"
        if os.path.exists(image_path):
            st.image(image_path, caption="PLS-SEM Empirical Structural Model Mapping for Najeehah International", use_container_width=True)
        else:
            st.warning(f"Sila pastikan fail imej '{image_path}' diletakkan di dalam folder projek yang sama untuk paparan visual rajah.")

        st.divider()

        st.markdown("### 3. Hypotheses Testing & Explanatory Power Evaluation")
        
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown("**Direct and Indirect Relationship Path Coefficients:**")
            st.table(pd.DataFrame({
                "Hypothesis": ["H1: Behaviour -> Engagement", "H2: Engagement -> Purchase Behavior", "H3: Behaviour -> Purchase Behavior", "H4 (Mediation): Behaviour -> Engagement -> Purchase Behavior"],
                "Path Type": ["Direct Effect", "Direct Effect", "Direct Effect", "Indirect Effect (Mediation)"],
                "Beta (β)": [0.894, 0.449, 0.513, 0.405],
                "T-Statistic": [28.452, 4.115, 5.234, 3.982],
                "p-value": ["< 0.001", "< 0.001", "< 0.001", "< 0.001"],
                "Empirical Result": ["Supported", "Supported", "Supported", "Supported (Partial Mediation)"]
            }))
        with h_col2:
            st.markdown("**Model Target Fit & R² Values:**")
            st.metric("R² Viewer Engagement", "79.9%")
            st.metric("R² Purchase Behavior", "88.5%")
            st.metric("Model SRMR Fit index", "0.062 (<0.08)")

    # ==================================
    # TOP PERFORMING SESSIONS (BENCHMARKING DATASET)
    # ==================================
    elif page == "Top Performing Sessions (Benchmarking Dataset)":
        st.title("🏆 Top Performing Sessions (Benchmarking Dataset)")
        st.markdown("### Benchmarking the Highest-Yielding TikTok Live Streams")
        st.markdown("This targeted section automatically extracts and visualizes the top 10 historical live sessions ranked by total commercial yield to establish robust performance standard operating procedures (SOPs).")

        # Sort data to isolate the top 10 sessions chronologically or by yield
        top_10 = df.sort_values(by='Gross Revenue', ascending=False).head(10).copy()
        top_10['Session_Rank'] = [f"Rank {i+1}" for i in range(len(top_10))]
        
        # Visualizing Benchmarking metrics side-by-side
        st.subheader("📊 Revenue & Engagement Volatility Breakdown")
        v1, v2 = st.columns(2)
        with v1:
            fig_top_rev = px.bar(
                top_10, 
                x='Session_Rank', 
                y='Gross Revenue', 
                title='Gross Revenue Yield Across Top 10 Sessions (RM)',
                color='Gross Revenue',
                color_continuous_scale='blues',
                text_auto='.2s'
            )
            st.plotly_chart(fig_top_rev, use_container_width=True)
        with v2:
            fig_top_clicks = px.bar(
                top_10, 
                x='Session_Rank', 
                y='Product Clicks', 
                title='Product Click Volume Performance for Top 10 Sessions',
                color='Product Clicks',
                color_continuous_scale='oranges',
                text_auto='.2s'
            )
            st.plotly_chart(fig_top_clicks, use_container_width=True)

        st.divider()

        # Dynamic table composition based on available dataset columns
        st.subheader("📋 Top Performing Sessions Leaderboard Ledger")
        
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
            
        table_cols.extend(['Gross Revenue', 'Product Clicks', 'Comments', 'Likes', 'Shares', 'Viewers'])
        table_names.extend(['Revenue (RM)', 'Product Clicks', 'Comments', 'Likes', 'Shares', 'Viewers'])
        
        display_top = top_10[table_cols].copy()
        display_top.columns = table_names
        
        st.dataframe(display_top.style.format({'Revenue (RM)': 'RM {:,.2f}'}), use_container_width=True)

else:
    st.title("📊 Najeehah International - TikTok Live Analytics Dashboard")
    st.markdown("---")
    st.info("Please upload your TikTok Live session dataset (`.xlsx` or `.csv`) via the sidebar layout to initialize the interactive analytics dashboard.")
