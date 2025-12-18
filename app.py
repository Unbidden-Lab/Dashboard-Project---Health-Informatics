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

# --- CUSTOM CSS THAT AUTO-ADJUSTS TO USER THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    div[data-testid="stMetric"], .stPlotlyChart, div[data-testid="stExpander"], .story-box, .corr-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .story-box {
        border-left: 5px solid #764ba2;
        margin-bottom: 20px;
    }
    
    .corr-card {
        border-left: 5px solid #FF4B4B;
        margin-bottom: 10px;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
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
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
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
    
    # --- SMART IMPUTATION FOR OCCUPATION---
    def assign_occupation(row):
        age = row['Age']
        stress = row['Stress Score']
        activity = row['Activity Level']
        
        if age >= 65:
            return 'Retired'
        elif age < 22:
            return 'Student'
        else:
            if stress >= 8:
                return 'Executive / Tech'
            elif activity == 'High':
                return 'Manual / Field Labor'
            elif activity == 'Moderate':
                return 'Healthcare / Education'
            else:
                return 'Office / Admin'

    df['Occupation'] = df.apply(assign_occupation, axis=1)
    
    # Move columns
    cols = ['Hypertension', 'Occupation'] + [c for c in df.columns if c not in ['Hypertension', 'Occupation']]
    df = df[cols]
    
    return df

df = load_data()
global_htn_rate = (len(df[df['Hypertension'] == 'Yes']) / len(df)) * 100
global_bmi = df['BMI'].mean()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏥 Analytics Hub")
    st.markdown("---")
    st.markdown("#### 🎯 Cohort Filters")
    
    # 1. Occupation Filter
    occupation_filter = st.multiselect("Occupation Sector", options=df['Occupation'].unique(), default=df['Occupation'].unique())
    
    # 2. Age Filter
    age_range = st.slider("Age Range", 18, 90, (20, 65))
    
    # 3. Family History Filter
    family_hist = st.multiselect("Family History", options=df['Family History'].unique(), default=df['Family History'].unique())
    
    # 4. Activity Level Filter 
    exercise_filter = st.multiselect("Activity Level", options=df['Activity Level'].unique(), default=df['Activity Level'].unique())
    
    st.markdown("---")
    st.caption("Developed for Health Informatics (ITE3)")

filtered_df = df[
    (df['Age'].between(age_range[0], age_range[1])) &
    (df['Family History'].isin(family_hist)) &
    (df['Occupation'].isin(occupation_filter)) &
    (df['Activity Level'].isin(exercise_filter))
]

# --- MAIN DASHBOARD ---
st.title("Hypertension Risk Intelligence")
st.markdown('<div class="subtitle-badge">v5.0 • Final Edition</div>', unsafe_allow_html=True)

# --- DYNAMIC STORY ENGINE ---
total_p = len(filtered_df)
current_risk = 0
risk_delta = 0
avg_bmi = 0
bmi_delta = 0
avg_sleep = 0

if total_p > 0:
    hyp_count = len(filtered_df[filtered_df['Hypertension'] == 'Yes'])
    current_risk = (hyp_count / total_p * 100)
    risk_delta = current_risk - global_htn_rate
    
    avg_bmi = filtered_df['BMI'].mean()
    bmi_delta = avg_bmi - global_bmi
    avg_sleep = filtered_df['Sleep Duration'].mean()
    
    dom_occ = filtered_df['Occupation'].mode()[0] if not filtered_df.empty else "Mixed"
    avg_stress = filtered_df['Stress Score'].mean()
    stress_desc = "High" if avg_stress > 6 else "Moderate" if avg_stress > 4 else "Low"
    
    story_text = f"""
    <b>Cohort Analysis:</b> analyzing <b>{total_p}</b> patients, predominantly in the <b>{dom_occ}</b> sector. 
    <br>The hypertension risk is <b>{current_risk:.1f}%</b> (<span style='color: {'#FF4B4B' if risk_delta > 0 else '#00C9A7'}'>
    <b>{abs(risk_delta):.1f}% {'above' if risk_delta > 0 else 'below'} global avg</b></span>).
    <br>This group exhibits <b>{stress_desc}</b> stress levels. 
    <i>(Notice how 'Executives' tend to have higher stress and risk compared to 'Manual Labor'.)</i>
    """
else:
    story_text = "No patients match the current filters. Please adjust your selection."

st.markdown(f'<div class="story-box">{story_text}</div>', unsafe_allow_html=True)

# KPI CARDS
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("👥 Total Cohort", f"{total_p:,}", "Records Selected")
with col2: st.metric("⚠️ HTN Prevalence", f"{current_risk:.1f}%", f"{risk_delta:+.1f}% vs Global", delta_color="inverse")
with col3: st.metric("📊 Mean BMI", f"{avg_bmi:.1f}", f"{bmi_delta:+.1f} vs Global", delta_color="inverse")
with col4: st.metric("😴 Avg Sleep", f"{avg_sleep:.1f}h", "Target: 7-9h")

st.markdown("---")

# --- CHARTS AREA ---
c_left, c_right = st.columns([2.5, 1])
custom_colors = {'Yes': '#FF4B4B', 'No': '#00C9A7'} 

with c_left:
    st.subheader("📈 Multifactorial Risk Analysis")
    fig_scatter = px.scatter(
        filtered_df, x="BMI", y="Salt Intake", color="Hypertension", size="Stress Score",
        hover_data=['Age', 'Occupation'], color_discrete_map=custom_colors, opacity=0.8,
        title="Impact of BMI & Salt on Hypertension (Size = Stress)"
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, x=0), margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig_scatter, width="stretch")

with c_right:
    st.subheader("🩺 Diagnosis Split")
    bp_counts = filtered_df['BP History'].value_counts()
    bp_colors = {'Normal': '#00C9A7', 'Prehypertension': '#FFD166', 'Hypertension': '#FF4B4B'}
    fig_pie = go.Figure(data=[go.Pie(
        labels=bp_counts.index, values=bp_counts.values, hole=0.6,
        marker=dict(colors=[bp_colors.get(x, '#95A5A6') for x in bp_counts.index]),
        textinfo='percent', hoverinfo='label+value'
    )])
    fig_pie.update_layout(
        showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(l=20, r=20, t=20, b=20),
        height=300, paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"{current_risk:.0f}%<br>Risk", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(fig_pie, width="stretch")

# --- TABS ---
st.markdown("### 🔬 Deep Dive Analytics")
tab1, tab2, tab3, tab4 = st.tabs(["💼 Occupation Analysis", "🚬 Behavioral", "💊 Treatments", "🔗 Correlation Lab"])

with tab1:
    col_graph, col_stats = st.columns([3, 1])
    with col_graph:
        occ_risk = filtered_df.groupby('Occupation')['Hypertension'].value_counts(normalize=True).unstack().fillna(0)
        occ_risk = occ_risk.reset_index()
        if 'Yes' in occ_risk.columns:
            occ_risk['Risk Score'] = occ_risk['Yes'] * 100 
            occ_risk = occ_risk.sort_values('Risk Score', ascending=False)
            fig_occ = px.bar(
                occ_risk, x='Risk Score', y='Occupation', orientation='h',
                title="Hypertension Risk by Sector", color='Risk Score',
                color_continuous_scale='Reds', text_auto='.1f'
            )
            fig_occ.update_layout(
                height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Hypertension Probability (%)", yaxis_title=None,
                yaxis=dict(gridcolor='rgba(128,128,128,0.2)'), xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_occ, width="stretch")
            
    with col_stats:
        st.info("💡 **Occupational Insight:** We imputed occupation based on Age, Stress, and Activity. Note how **Executives** (High Stress) and **Retired** (Age) have the highest risk profiles.")

with tab2:
    fig_violin = px.violin(
        filtered_df, y="Stress Score", x="Smoking Status", color="Hypertension",
        box=True, points="all", color_discrete_map=custom_colors,
        title="Distribution of Stress & Smoking"
    )
    fig_violin.update_layout(
        height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, x=0), yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig_violin, width="stretch")

with tab3:
    med_counts_df = filtered_df['Medication'].value_counts().reset_index()
    med_counts_df.columns = ['Medication', 'Count'] 
    med_counts_df = med_counts_df.head(10)
    fig_bar = px.bar(
        med_counts_df, x='Count', y='Medication', orientation='h',
        color='Count', color_continuous_scale='Purples'
    )
    fig_bar.update_layout(
        title="Most Prescribed Medications", xaxis_title="Patient Count",
        height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False, xaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig_bar, width="stretch")

# --- CORRELATION LAB  ---
with tab4:
    st.markdown("##### 🕵️ Data Detective: Pinpoint Correlations")
    
    corr_df = filtered_df.copy()
    for col in corr_df.select_dtypes(include=['object']).columns:
        corr_df[col] = corr_df[col].astype('category').cat.codes
        
    corr_matrix = corr_df.corr().round(2)
    c = corr_matrix.abs()
    s = c.unstack()
    so = s.sort_values(kind="quicksort", ascending=False)
    so = so[so < 1.0] 
    so = so[so > 0.1] 
    
    unique_pairs = []
    seen = set()
    for index, val in so.items():
        pair = sorted([index[0], index[1]])
        pair_str = f"{pair[0]} ↔ {pair[1]}"
        if pair_str not in seen:
            seen.add(pair_str)
            unique_pairs.append((f"{pair[0]} & {pair[1]} ({val:.2f})", pair[0], pair[1], val))
    
    col_sel, col_viz = st.columns([1, 2])
    
    with col_sel:
        st.write("Significant relationships detected:")
        options = [x[0] for x in unique_pairs]
        if options:
            selected_option = st.selectbox("Select to Explore:", options)
            sel_data = next(x for x in unique_pairs if x[0] == selected_option)
            col_x, col_y, corr_val = sel_data[1], sel_data[2], sel_data[3]
            st.markdown(f"<div class='corr-card'><h3>{corr_val}</h3><small>{col_x} ↔ {col_y}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No strong correlations found.")
            col_x, col_y = "Age", "BMI" 
            
    with col_viz:
        if options:
            corr_df['Hypertension Label'] = filtered_df['Hypertension'].reset_index(drop=True)
            fig_corr = px.scatter(
                corr_df, x=col_x, y=col_y, color="Hypertension Label", 
                trendline="ols", title=f"{col_x} vs {col_y}",
                color_discrete_map={'Yes': '#FF4B4B', 'No': '#00C9A7'}, opacity=0.7
            )
            fig_corr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=350, xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
                yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
            )
            st.plotly_chart(fig_corr, width="stretch")

# --- FOOTER ---
st.markdown("---")
with st.expander("📂 View Raw Data Source"):
    st.dataframe(filtered_df.style.background_gradient(cmap="Purples", subset=["Age", "BMI", "Stress Score"]))
    
    st.markdown("""
    <small>
        <b>Data Citation:</b> 
        <a href="https://www.kaggle.com/datasets/miadul/hypertension-risk-prediction-dataset" target="_blank">
            Hypertension Risk Prediction Dataset
        </a> 
        by Miadul (Kaggle). Accessed December 2025.
    </small>
    """, unsafe_allow_html=True)