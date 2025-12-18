import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Health Analytics Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME-AWARE CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * { font-family: 'Inter', sans-serif; }
    
    /* Custom Card Styling */
    div[data-testid="stMetric"],
    .stPlotlyChart,
    div[data-testid="stExpander"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Header Styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Subtitle Badge */
    .subtitle-badge {
        display: inline-block;
        background: var(--secondary-background-color);
        color: #764ba2;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #764ba2 !important;
        color: white !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('hypertension_dataset.csv')
    df['Medication'] = df['Medication'].fillna('None')
    
    # RENAME COLUMNS
    df.rename(columns={
        'Has_Hypertension': 'Hypertension',
        'Smoking_Status': 'Smoking Status',
        'Salt_Intake': 'Salt Intake',
        'Stress_Score': 'Stress Score',
        'BP_History': 'BP History',
        'Sleep_Duration': 'Sleep Duration',
        'Exercise_Level': 'Activity Level',
        'Family_History': 'Family History'
    }, inplace=True)
    
    # FIX: Move 'Hypertension' (Target) to the FIRST column so it's never hidden
    cols = ['Hypertension'] + [c for c in df.columns if c != 'Hypertension']
    df = df[cols]
    
    return df

df = load_data()

# --- CALCULATE GLOBAL AVERAGES ---
global_htn_rate = (len(df[df['Hypertension'] == 'Yes']) / len(df)) * 100
global_bmi = df['BMI'].mean()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏥 Analytics Hub")
    st.markdown("---")
    
    st.markdown("#### 🎯 Cohort Filters")
    age_range = st.slider("Age Range", 18, 90, (20, 65))
    
    family_hist = st.multiselect(
        "Family History", 
        options=df['Family History'].unique(),
        default=df['Family History'].unique()
    )
    
    exercise_filter = st.multiselect(
        "Activity Level",
        options=df['Activity Level'].unique(),
        default=df['Activity Level'].unique()
    )
    
    st.markdown("---")
    st.caption("Developed for Health Informatics (ITE3)")

# Apply Filters
filtered_df = df[
    (df['Age'].between(age_range[0], age_range[1])) &
    (df['Family History'].isin(family_hist)) &
    (df['Activity Level'].isin(exercise_filter))
]

# --- MAIN DASHBOARD ---

st.title("Hypertension Risk Intelligence")
st.markdown('<div class="subtitle-badge">v2.5 • Live Clinical Dashboard</div>', unsafe_allow_html=True)

# 1. KPI CARDS
col1, col2, col3, col4 = st.columns(4)

total_p = len(filtered_df)
hyp_count = len(filtered_df[filtered_df['Hypertension'] == 'Yes'])
avg_bmi = filtered_df['BMI'].mean()

current_risk = (hyp_count / total_p * 100) if total_p > 0 else 0
risk_delta = current_risk - global_htn_rate
bmi_delta = avg_bmi - global_bmi

with col1:
    st.metric("👥 Total Cohort", f"{total_p:,}", "Records Selected")
with col2:
    st.metric("⚠️ HTN Prevalence", f"{current_risk:.1f}%", f"{risk_delta:+.1f}% vs Global", delta_color="inverse")
with col3:
    st.metric("📊 Mean BMI", f"{avg_bmi:.1f}", f"{bmi_delta:+.1f} vs Global", delta_color="inverse")
with col4:
    avg_sleep = filtered_df['Sleep Duration'].mean()
    st.metric("😴 Avg Sleep", f"{avg_sleep:.1f}h", "Target: 7-9h")

st.markdown("---")

# 2. MAIN ANALYTICS ROW
c_left, c_right = st.columns([2.5, 1])
custom_colors = {'Yes': '#FF4B4B', 'No': '#00C9A7'} 

with c_left:
    st.subheader("📈 Multifactorial Risk Analysis")
    fig_scatter = px.scatter(
        filtered_df,
        x="BMI",
        y="Salt Intake",
        color="Hypertension",
        size="Stress Score",
        hover_data=['Age', 'Medication'],
        color_discrete_map=custom_colors,
        opacity=0.8,
        title="Impact of BMI & Salt on Hypertension (Size = Stress)"
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # FIX: Moved Legend to Bottom (-0.2) so it doesn't get pushed off screen
        legend=dict(orientation="h", y=-0.1, x=0),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig_scatter, width="stretch")

with c_right:
    st.subheader("🩺 Diagnosis Split")
    bp_counts = filtered_df['BP History'].value_counts()
    
    bp_colors = {'Normal': '#00C9A7', 'Prehypertension': '#FFD166', 'Hypertension': '#FF4B4B'}
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=bp_counts.index,
        values=bp_counts.values,
        hole=0.6,
        marker=dict(colors=[bp_colors.get(x, '#95A5A6') for x in bp_counts.index]),
        textinfo='percent',
        hoverinfo='label+value'
    )])
    
    fig_pie.update_layout(
        showlegend=True,
        # FIX: Moved Legend to Bottom
        legend=dict(orientation="h", y=-0.1),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"{current_risk:.0f}%<br>Risk", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(fig_pie, width="stretch")

# 3. DEEP DIVE TABS
st.markdown("### 🔬 Deep Dive Analytics")
tab1, tab2, tab3 = st.tabs(["🚬 Behavioral Impact", "📅 Age Demographics", "💊 Treatments"])

with tab1:
    col_graph, col_stats = st.columns([3, 1])
    with col_graph:
        fig_violin = px.violin(
            filtered_df,
            y="Stress Score",
            x="Smoking Status",
            color="Hypertension",
            box=True,
            points="all",
            color_discrete_map=custom_colors,
        )
        fig_violin.update_layout(
            height=400, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            # FIX: Legend at bottom
            legend=dict(orientation="h", y=-0.1, x=0),
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
        )
        st.plotly_chart(fig_violin, width="stretch")
    
    with col_stats:
        st.info("💡 **Observation:** High stress combined with smoking significantly correlates with hypertension cases (Red distribution).")

with tab2:
    fig_hist = px.histogram(
        filtered_df,
        x="Age",
        color="Hypertension",
        marginal="box",
        nbins=25,
        color_discrete_map=custom_colors,
        barmode="overlay"
    )
    fig_hist.update_layout(
        height=400, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        # FIX: Legend at bottom
        legend=dict(orientation="h", y=-0.1, x=0),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    fig_hist.update_traces(opacity=0.75)
    st.plotly_chart(fig_hist, width="stretch")

with tab3:
    med_counts_df = filtered_df['Medication'].value_counts().reset_index()
    med_counts_df.columns = ['Medication', 'Count'] 
    med_counts_df = med_counts_df.head(10)

    fig_bar = px.bar(
        med_counts_df,
        x='Count',
        y='Medication',
        orientation='h',
        color='Count',
        color_continuous_scale='Purples'
    )
    
    fig_bar.update_layout(
        title="Most Prescribed Medications",
        xaxis_title="Patient Count",
        yaxis_title="Medication",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig_bar, width="stretch")

# --- FOOTER ---
st.markdown("---")
with st.expander("📂 View Raw Data Source"):
    # This table will now have Hypertension as the FIRST column
    st.dataframe(filtered_df.style.background_gradient(cmap="Purples", subset=["Age", "BMI", "Stress Score"]))
    st.caption("Data Source: Medical Hypertension Research Dataset (2024)")