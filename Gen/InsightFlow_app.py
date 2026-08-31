#http://localhost:8501/   this is the url to run the streamlit app in local host
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="InsightFlow AI - Executive Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark dashboard aesthetics
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stCard { background-color: rgba(18, 26, 43, 0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; }
    .bot-box { background-color: #0f172a; border: 1px solid #00f2fe; border-radius: 12px; padding: 16px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Data Generator & Session State Initialization
# -----------------------------------------------------------------------------
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    categories = ['Electronics', 'Furniture', 'Software', 'Services']
    regions = ['North', 'South', 'East', 'West']
    data = []
    start_date = datetime(2026, 1, 1)

    for i in range(250):
        current_date = start_date + timedelta(days=i)
        category = np.random.choice(categories)
        region = np.random.choice(regions)
        price = 199 if category == 'Software' else (450 if category == 'Electronics' else 120)
        qty = np.random.randint(1, 9)
        discount = 0.15 if np.random.rand() > 0.6 else 0.0
        revenue = round(price * qty * (1 - discount), 2)
        cost = round(revenue * (0.65 if category == 'Electronics' else 0.40), 2)
        profit = round(revenue - cost, 2)

        data.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Category": category,
            "Region": region,
            "Product": f"{category} Item {np.random.randint(1, 6)}",
            "Revenue": revenue,
            "Profit": profit,
            "Quantity": qty,
            "Discount": discount
        })
    return pd.DataFrame(data)

if 'df' not in st.session_state:
    st.session_state.df = generate_sample_data()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I'm your BI Assistant. Ask me questions like 'What is our net profit?' or 'Which category is performing best?'"}
    ]

if 'guide_step' not in st.session_state:
    st.session_state.guide_step = 0

if 'show_guide' not in st.session_state:
    st.session_state.show_guide = True

# -----------------------------------------------------------------------------
# 3. Sidebar Navigation & Data Ingestion
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🧠 InsightFlow AI")
    st.caption("Business Intelligence & Analytics Platform")
    st.divider()

    st.subheader("📁 Data Ingestion")
    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.session_state.df = uploaded_df
            st.success("Custom CSV dataset loaded successfully!")
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")

    if st.button("🔄 Reload Sample Dataset", use_container_width=True):
        st.session_state.df = generate_sample_data()
        st.rerun()

    st.divider()
    if st.button("🤖 Launch Guide Bot", use_container_width=True):
        st.session_state.show_guide = True
        st.session_state.guide_step = 0
        st.rerun()

# -----------------------------------------------------------------------------
# 4. Interactive First-Time Guide Bot
# -----------------------------------------------------------------------------
bot_steps = [
    "👋 **Welcome to InsightFlow AI!** I'm your onboarding assistant bot. Let me quickly show you around so you know how to analyze your data.",
    "📁 **Step 1: Data Ingestion**<br>Use the left sidebar to upload custom CSV transaction files or click **'Reload Sample Dataset'**.",
    "📊 **Step 2: Executive Analytics**<br>Review total revenue, net profit margin, order volume, interactive sales trend graphs, and regional pie charts.",
    "🎛️ **Step 3: What-If Strategy Simulator**<br>Adjust price and marketing sliders below to simulate strategic outcomes and real-time revenue impact.",
    "⚡ **Step 4: AI Copilot & CSV Export**<br>Ask business queries in the chatbot at the bottom, or click **'Export CSV'** at the top right to download reports!"
]

if st.session_state.show_guide:
    st.markdown('<div class="bot-box">', unsafe_allow_html=True)
    col_bot1, col_bot2 = st.columns([4, 1])
    
    with col_bot1:
        st.markdown(f"🤖 **Guide Bot (Step {st.session_state.guide_step + 1} of {len(bot_steps)})**")
        st.markdown(bot_steps[st.session_state.guide_step], unsafe_allow_html=True)
    
    with col_bot2:
        btn_cols = st.columns(2)
        if st.session_state.guide_step > 0:
            if btn_cols[0].button("Back", key="bot_prev"):
                st.session_state.guide_step -= 1
                st.rerun()
        
        if st.session_state.guide_step < len(bot_steps) - 1:
            if btn_cols[1].button("Next", key="bot_next"):
                st.session_state.guide_step += 1
                st.rerun()
        else:
            if btn_cols[1].button("Close", key="bot_close"):
                st.session_state.show_guide = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Header Bar & Export Action
# -----------------------------------------------------------------------------
df = st.session_state.df

header_left, header_right = st.columns([3, 1])
with header_left:
    st.title("Executive Command Center")
    st.caption("Turn Business Data into Strategic Decisions")

with header_right:
    st.write(" ")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Dataset (CSV)",
        data=csv_data,
        file_name=f"InsightFlow_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

# -----------------------------------------------------------------------------
# 6. KPI Calculation & Dashboard Metrics
# -----------------------------------------------------------------------------
total_rev = df['Revenue'].sum() if 'Revenue' in df.columns else 0.0
total_prof = df['Profit'].sum() if 'Profit' in df.columns else 0.0
orders_count = len(df)
aov = total_rev / orders_count if orders_count > 0 else 0.0
profit_margin = (total_prof / total_rev * 100) if total_rev > 0 else 0.0

mid_point = len(df) // 2
prev_rev = df.iloc[:mid_point]['Revenue'].sum() if 'Revenue' in df.columns else 1
curr_rev = df.iloc[mid_point:]['Revenue'].sum() if 'Revenue' in df.columns else 0
growth_rate = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Revenue", f"${total_rev:,.2f}", f"{growth_rate:+.1f}% Growth")
kpi2.metric("Net Profit", f"${total_prof:,.2f}", f"{profit_margin:.1f}% Margin")
kpi3.metric("Total Transactions", f"{orders_count:,}")
kpi4.metric("Avg Order Value (AOV)", f"${aov:,.2f}")

st.divider()

# -----------------------------------------------------------------------------
# 7. Visual Analytics Charts
# -----------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    st.subheader("Revenue Performance Trend")
    if 'Date' in df.columns and 'Revenue' in df.columns:
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M').astype(str)
        trend_df = df.groupby('Month')['Revenue'].sum().reset_index()
        fig_trend = px.line(trend_df, x='Month', y='Revenue', markers=True, line_shape='spline',
                            color_discrete_sequence=['#00f2fe'])
        fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#f1f5f9'))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Insufficient data columns for trend rendering.")

with chart_col2:
    st.subheader("Regional Revenue Share")
    if 'Region' in df.columns and 'Revenue' in df.columns:
        region_df = df.groupby('Region')['Revenue'].sum().reset_index()
        fig_region = px.pie(region_df, values='Revenue', names='Region', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Blugrn)
        fig_region.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'))
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("Insufficient data columns for regional rendering.")

st.divider()

# -----------------------------------------------------------------------------
# 8. AI Insights & Risk Radar
# -----------------------------------------------------------------------------
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.subheader("💡 Automated Business Insights")
    top_cat = df.groupby('Category')['Revenue'].sum().idxmax() if 'Category' in df.columns else "N/A"
    st.success(f"**Revenue Trend:** Revenue achieved **{growth_rate:.1f}% growth** across the dataset timeline.")
    st.info(f"**Category Leader:** The **{top_cat}** category represents the primary revenue driver.")

with insight_col2:
    st.subheader("⚠️ Risk & Opportunity Radar")
    st.warning(f"**Margin Alert:** Current net profit margin is sitting at **{profit_margin:.1f}%**. Watch operating costs.")
    st.error("**Growth Vector:** Expanding digital marketing in East & North regions can boost overall volume by ~12%.")

st.divider()

# -----------------------------------------------------------------------------
# 9. What-If Strategy Simulator & Copilot Assistant
# -----------------------------------------------------------------------------
sim_col, chat_col = st.columns(2)

with sim_col:
    st.subheader("🎛️ What-If Strategy Simulator")
    price_adj = st.slider("Price Adjustment (%)", min_value=-20, max_value=20, value=0, step=1)
    mkt_invest = st.slider("Marketing Investment (+%)", min_value=0, max_value=100, value=0, step=5)

    price_factor = 1 + (price_adj / 100)
    mkt_factor = 1 + ((mkt_invest * 0.25) / 100)
    projected_rev = total_rev * price_factor * mkt_factor
    revenue_delta = ((projected_rev - total_rev) / total_rev * 100) if total_rev > 0 else 0.0

    st.markdown("### Simulation Output")
    st.write(f"**Projected Total Revenue:** `${projected_rev:,.2f}`")
    st.write(f"**Projected Net Impact:** `{revenue_delta:+.1f}%`")

with chat_col:
    st.subheader("🤖 InsightFlow Copilot Chat")
    
    # Render chat message history
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query = st.chat_input("Ask a business query (e.g., 'What is our profit margin?')...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        query_lower = user_query.lower()
        if "revenue" in query_lower or "sales" in query_lower:
            reply = f"Total gross revenue is currently **${total_rev:,.2f}**, showing a **{growth_rate:.1f}%** trend shift."
        elif "profit" in query_lower or "margin" in query_lower:
            reply = f"Net profit stands at **${total_prof:,.2f}**, representing an overall margin of **{profit_margin:.1f}%**."
        elif "risk" in query_lower or "problem" in query_lower:
            reply = f"Primary Risk Warning: Net profit margin is **{profit_margin:.1f}%**. Maintain focus on procurement overheads."
        else:
            reply = f"Dataset evaluated ({orders_count} transactions). Total Revenue is **${total_rev:,.2f}** with a profit margin of **{profit_margin:.1f}%**."

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)