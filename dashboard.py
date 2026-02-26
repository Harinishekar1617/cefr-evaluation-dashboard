"""
CEFR Evaluation Dashboard
Streamlit app to explore and compare CEFR evaluation results across different prompt versions and LLM models.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import numpy as np

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="CEFR Evaluation Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PASSWORD PROTECTION
# ============================================================================
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("dashboard_password", "cefr2024"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.markdown("## 🔐 CEFR Evaluation Dashboard")
        st.markdown("Protected Access")
        st.text_input(
            "Enter Dashboard Password:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show error
        st.error("❌ Incorrect password. Please try again.")
        st.text_input(
            "Enter Dashboard Password:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

st.title("🎓 CEFR Evaluation Dashboard")
st.markdown("Compare evaluation results across prompt versions and LLM models")

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    """Load all evaluation data from CSV files."""
    output_dir = Path("/Users/hshekar/CEFR Evaluation/output")

    data = {
        'v1_key_indicators_only': {
            'aggregated': pd.read_csv(output_dir / 'cefr_aggregated_all_students_v1_key_indicators_only.csv'),
            'individual': pd.read_csv(output_dir / 'cefr_individual_turns_all_students_v1_key_indicators_only.csv')
        },
        'v2_full_guidelines': {
            'aggregated': pd.read_csv(output_dir / 'cefr_aggregated_all_students_v2_full_guidelines.csv'),
            'individual': pd.read_csv(output_dir / 'cefr_individual_turns_all_students_v2_full_guidelines.csv')
        },
        'v3_measurable_evidence': {
            'aggregated': pd.read_csv(output_dir / 'cefr_aggregated_all_students_v3_measurable_evidence.csv'),
            'individual': pd.read_csv(output_dir / 'cefr_individual_turns_all_students_v3_measurable_evidence.csv')
        },
        'v3_measurable_evidence_deepseek': {
            'aggregated': None,  # No aggregated file for deepseek
            'individual': pd.read_csv(output_dir / 'cefr_individual_turns_all_students_v3_measurable_evidence_deepseek.csv')
        }
    }

    return data

try:
    data = load_data()
    st.success("✅ Data loaded successfully")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ============================================================================
# TAB 1: OVERVIEW & COMPARISON
# ============================================================================
def tab_overview():
    st.header("📊 Overview & Comparison")
    st.markdown("How do different evaluation approaches affect student scores?")

    df_v1 = data['v1_key_indicators_only']['aggregated']
    df_v2 = data['v2_full_guidelines']['aggregated']
    df_v3 = data['v3_measurable_evidence']['aggregated']

    # Distribution comparison - main chart
    st.subheader("CEFR Level Distribution")

    dist_data = {
        'Key Indicators': df_v1['overall_mode'].value_counts().sort_index(),
        'Full Guidelines': df_v2['overall_mode'].value_counts().sort_index(),
        'Measurable Evidence': df_v3['overall_mode'].value_counts().sort_index()
    }

    fig = go.Figure()
    for version, dist in dist_data.items():
        fig.add_trace(go.Bar(
            name=version,
            x=dist.index,
            y=dist.values,
            text=dist.values,
            textposition='auto',
        ))

    fig.update_layout(
        barmode='group',
        xaxis_title="CEFR Level",
        yaxis_title="Number of Students",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Key findings
    st.subheader("Key Findings")

    col1, col2, col3 = st.columns(3)

    a1_v1 = (df_v1['overall_mode'] == 'A1').sum()
    a1_v2 = (df_v2['overall_mode'] == 'A1').sum()
    a1_v3 = (df_v3['overall_mode'] == 'A1').sum()

    with col1:
        st.metric("Key Indicators (A1)", a1_v1)
    with col2:
        st.metric("Full Guidelines (A1)", a1_v2)
    with col3:
        st.metric("Measurable Evidence (A1)", a1_v3)

    # Comparison insight
    st.info(f"""
    **Key Insight:** Measurable Evidence is the strictest approach, placing {a1_v3} students at A1
    compared to {a1_v1} with Key Indicators only. This suggests requiring quantifiable evidence
    results in more conservative (stricter) evaluations.
    """)

    # Student-level comparison table
    st.subheader("Student Score Comparison")

    df_comparison = pd.DataFrame({
        'Student': df_v3['student_name'],
        'Key Indicators': df_v1.set_index('student_name').loc[df_v3['student_name'], 'overall_mode'].values,
        'Full Guidelines': df_v2.set_index('student_name').loc[df_v3['student_name'], 'overall_mode'].values,
        'Measurable Evidence': df_v3['overall_mode'].values
    })

    # Check agreement
    df_comparison['All Agree'] = (df_comparison['Key Indicators'] == df_comparison['Full Guidelines']) & \
                                  (df_comparison['Full Guidelines'] == df_comparison['Measurable Evidence'])

    st.dataframe(df_comparison, use_container_width=True)

    # Agreement stats
    agreement_count = df_comparison['All Agree'].sum()
    disagreement_count = len(df_comparison) - agreement_count

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **Full Agreement**: {agreement_count} students scored identically across all approaches")
    with col2:
        st.warning(f"⚠️ **Disagreement**: {disagreement_count} students have varying scores")

    # Turn-wise comparison
    st.divider()
    st.subheader("🎙️ Turn-Wise Comparison")
    st.markdown("How consistent are evaluations across different dialogue turns?")

    df_v1_indiv = data['v1_key_indicators_only']['individual']
    df_v2_indiv = data['v2_full_guidelines']['individual']
    df_v3_indiv = data['v3_measurable_evidence']['individual']

    # Create turn-wise comparison
    turn_comparison = pd.DataFrame({
        'Student': df_v3_indiv['student_name'].values,
        'Turn': df_v3_indiv['dialogue_turn_number'].values,
        'Key Indicators': df_v1_indiv['overall_cefr_level'].values,
        'Full Guidelines': df_v2_indiv['overall_cefr_level'].values,
        'Measurable Evidence': df_v3_indiv['overall_cefr_level'].values,
    })

    # Add agreement column
    turn_comparison['Agreement'] = (turn_comparison['Key Indicators'] == turn_comparison['Full Guidelines']) & \
                                    (turn_comparison['Full Guidelines'] == turn_comparison['Measurable Evidence'])

    # Filter option
    col1, col2 = st.columns(2)
    with col1:
        show_all = st.checkbox("Show all turns", value=False)
    with col2:
        if not show_all:
            st.write("**Showing only controversial turns** (where scores differ)")

    # Display turns
    if show_all:
        display_turns = turn_comparison
        st.info(f"Showing all {len(turn_comparison)} dialogue turns")
    else:
        display_turns = turn_comparison[~turn_comparison['Agreement']]
        st.warning(f"Found {len(display_turns)} controversial turns where approaches disagree")

    st.dataframe(display_turns, use_container_width=True, hide_index=True)

    # Key insights on turns
    st.subheader("Turn Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_turns = len(turn_comparison)
        agreed_turns = turn_comparison['Agreement'].sum()
        st.metric("Turns with Full Agreement", agreed_turns, f"({agreed_turns/total_turns*100:.0f}%)")

    with col2:
        controversial_turns = len(display_turns)
        st.metric("Controversial Turns", controversial_turns, f"({controversial_turns/total_turns*100:.0f}%)")

    with col3:
        # Most controversial student
        controversial_by_student = turn_comparison[~turn_comparison['Agreement']].groupby('Student').size().sort_values(ascending=False)
        if len(controversial_by_student) > 0:
            most_controversial = controversial_by_student.index[0]
            st.metric("Most Controversial Student", most_controversial, f"{controversial_by_student.iloc[0]} turns")

# ============================================================================
# TAB 2: STUDENT DRILL-DOWN
# ============================================================================
def tab_student_drilldown():
    st.header("🔍 Student Drill-Down")
    st.markdown("Explore how a student is evaluated across different approaches")

    df_v1_agg = data['v1_key_indicators_only']['aggregated']
    students = sorted(df_v1_agg['student_name'].unique())

    selected_student = st.selectbox("Select Student", students, key="student_select")

    if selected_student:
        # Get aggregated data for selected student
        df_v1_indiv = data['v1_key_indicators_only']['individual']
        df_v2_indiv = data['v2_full_guidelines']['individual']
        df_v3_indiv = data['v3_measurable_evidence']['individual']

        v1_student = df_v1_indiv[df_v1_indiv['student_name'] == selected_student]
        v2_student = df_v2_indiv[df_v2_indiv['student_name'] == selected_student]
        v3_student = df_v3_indiv[df_v3_indiv['student_name'] == selected_student]

        # Student summary - aggregated across all 5 turns
        st.subheader("Summary Scores (Mode across 5 turns)")

        summary_data = []
        for version, v_student in [('Key Indicators', v1_student), ('Full Guidelines', v2_student), ('Measurable Evidence', v3_student)]:
            if len(v_student) > 0:
                summary_data.append({
                    'Approach': version,
                    'Range': v_student['range'].mode().values[0] if len(v_student['range'].mode()) > 0 else 'N/A',
                    'Accuracy': v_student['accuracy'].mode().values[0] if len(v_student['accuracy'].mode()) > 0 else 'N/A',
                    'Fluency': v_student['fluency'].mode().values[0] if len(v_student['fluency'].mode()) > 0 else 'N/A',
                    'Coherence': v_student['coherence'].mode().values[0] if len(v_student['coherence'].mode()) > 0 else 'N/A',
                })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Drill down to individual turns
        st.subheader(f"Individual Dialogue Turns ({len(v3_student)} turns)")

        if len(v3_student) > 0:
            num_turns = len(v3_student)

            for idx in range(num_turns):
                with st.expander(f"Turn {idx + 1} - Detailed Comparison"):
                    col1, col2, col3 = st.columns(3)

                    # v1
                    with col1:
                        st.write("**Key Indicators**")
                        if idx < len(v1_student):
                            v1_row = v1_student.iloc[idx]
                            st.write(f"Range: **{v1_row['range']}**")
                            st.write(f"Accuracy: **{v1_row['accuracy']}**")
                            st.write(f"Fluency: **{v1_row['fluency']}**")
                            st.write(f"Coherence: **{v1_row['coherence']}**")

                    # v2
                    with col2:
                        st.write("**Full Guidelines**")
                        if idx < len(v2_student):
                            v2_row = v2_student.iloc[idx]
                            st.write(f"Range: **{v2_row['range']}**")
                            st.write(f"Accuracy: **{v2_row['accuracy']}**")
                            st.write(f"Fluency: **{v2_row['fluency']}**")
                            st.write(f"Coherence: **{v2_row['coherence']}**")

                    # v3
                    with col3:
                        st.write("**Measurable Evidence**")
                        if idx < len(v3_student):
                            v3_row = v3_student.iloc[idx]
                            st.write(f"Range: **{v3_row['range']}**")
                            st.write(f"Accuracy: **{v3_row['accuracy']}**")
                            st.write(f"Fluency: **{v3_row['fluency']}**")
                            st.write(f"Coherence: **{v3_row['coherence']}**")

                    # v3 Detailed Evidence
                    st.write("---")
                    st.write("**Evaluation Evidence (Measurable Evidence approach):**")
                    if idx < len(v3_student):
                        justification = v3_student.iloc[idx]['justification']
                        st.text(justification)
        else:
            st.warning(f"No data found for {selected_student}")

# ============================================================================
# TAB 3: DIMENSION ANALYSIS
# ============================================================================
def tab_dimension_analysis():
    st.header("📐 Dimension Analysis")
    st.markdown("How do students score on each dimension?")

    dimensions = ['range', 'accuracy', 'fluency', 'coherence']
    selected_dim = st.selectbox("Select Dimension", dimensions)

    # Get student-level aggregates
    df_v1_agg = data['v1_key_indicators_only']['aggregated']
    df_v2_agg = data['v2_full_guidelines']['aggregated']
    df_v3_agg = data['v3_measurable_evidence']['aggregated']

    dim_col = f"{selected_dim}_mode"

    st.subheader(f"Student-Level {selected_dim.capitalize()} Scores")

    # Create student comparison for this dimension
    student_dim_data = pd.DataFrame({
        'Student': df_v3_agg['student_name'],
        'Key Indicators': df_v1_agg.set_index('student_name').loc[df_v3_agg['student_name'], dim_col].values,
        'Full Guidelines': df_v2_agg.set_index('student_name').loc[df_v3_agg['student_name'], dim_col].values,
        'Measurable Evidence': df_v3_agg[dim_col].values
    })

    st.dataframe(student_dim_data, use_container_width=True, hide_index=True)

    # Distribution summary
    st.subheader(f"Distribution of {selected_dim.capitalize()}")

    df_v1_indiv = data['v1_key_indicators_only']['individual']
    df_v2_indiv = data['v2_full_guidelines']['individual']
    df_v3_indiv = data['v3_measurable_evidence']['individual']

    fig = go.Figure()

    for df, version in [
        (df_v1_indiv, 'Key Indicators'),
        (df_v2_indiv, 'Full Guidelines'),
        (df_v3_indiv, 'Measurable Evidence')
    ]:
        dist = df[selected_dim].value_counts().sort_index()
        fig.add_trace(go.Bar(
            name=version,
            x=dist.index,
            y=dist.values,
            text=dist.values,
            textposition='auto',
        ))

    fig.update_layout(
        barmode='group',
        xaxis_title=f"{selected_dim.capitalize()} Level",
        yaxis_title="Count (across all 105 turns)",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Optional: drill down to individual turns
    with st.expander(f"📊 Detailed Breakdown - All {selected_dim.capitalize()} Scores per Turn"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Key Indicators**")
            dist_v1 = df_v1_indiv[selected_dim].value_counts().sort_index()
            st.bar_chart(dist_v1)

        with col2:
            st.write("**Full Guidelines**")
            dist_v2 = df_v2_indiv[selected_dim].value_counts().sort_index()
            st.bar_chart(dist_v2)

        with col3:
            st.write("**Measurable Evidence**")
            dist_v3 = df_v3_indiv[selected_dim].value_counts().sort_index()
            st.bar_chart(dist_v3)

# ============================================================================
# TAB 4: LLM COMPARISON
# ============================================================================
def tab_llm_comparison():
    st.header("🤖 LLM Comparison")
    st.markdown("Compare v3 Measurable Evidence results between gpt-4o-mini and DeepSeek R1 Distill")

    df_v3_gpt = data['v3_measurable_evidence']['individual']
    df_v3_ds = data['v3_measurable_evidence_deepseek']['individual']

    # Summary statistics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("GPT-4o-mini")
        st.metric("Students Evaluated", df_v3_gpt['student_name'].nunique())
        st.metric("Dialogue Turns", len(df_v3_gpt))
        st.metric("A1 Count", (df_v3_gpt['overall_cefr_level'] == 'A1').sum())
        st.metric("A2 Count", (df_v3_gpt['overall_cefr_level'] == 'A2').sum())

    with col2:
        st.subheader("DeepSeek R1 Distill")
        st.metric("Students Evaluated", df_v3_ds['student_name'].nunique())
        st.metric("Dialogue Turns", len(df_v3_ds))
        st.metric("A1 Count", (df_v3_ds['overall_cefr_level'] == 'A1').sum())
        st.metric("A2 Count", (df_v3_ds['overall_cefr_level'] == 'A2').sum())

    # Distribution comparison
    st.subheader("CEFR Level Distribution Comparison")

    dist_gpt = df_v3_gpt['overall_cefr_level'].value_counts().sort_index()
    dist_ds = df_v3_ds['overall_cefr_level'].value_counts().sort_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='GPT-4o-mini', x=dist_gpt.index, y=dist_gpt.values, text=dist_gpt.values, textposition='auto'))
    fig.add_trace(go.Bar(name='DeepSeek R1 Distill', x=dist_ds.index, y=dist_ds.values, text=dist_ds.values, textposition='auto'))

    fig.update_layout(
        barmode='group',
        title="Overall CEFR Level Distribution: GPT-4o-mini vs DeepSeek",
        xaxis_title="CEFR Level",
        yaxis_title="Count",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Student-level comparison
    st.subheader("Student-Level Comparison")

    # Create comparison dataframe
    gpt_agg = df_v3_gpt.groupby('student_name').agg({
        'overall_cefr_level': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'range': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'accuracy': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'fluency': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
    }).rename(columns={
        'overall_cefr_level': 'Overall (GPT)',
        'range': 'Range (GPT)',
        'accuracy': 'Accuracy (GPT)',
        'fluency': 'Fluency (GPT)'
    })

    ds_agg = df_v3_ds.groupby('student_name').agg({
        'overall_cefr_level': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'range': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'accuracy': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
        'fluency': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
    }).rename(columns={
        'overall_cefr_level': 'Overall (DeepSeek)',
        'range': 'Range (DeepSeek)',
        'accuracy': 'Accuracy (DeepSeek)',
        'fluency': 'Fluency (DeepSeek)'
    })

    comparison = pd.concat([gpt_agg, ds_agg], axis=1)

    # Add agreement column
    comparison['Overall Agreement'] = comparison['Overall (GPT)'] == comparison['Overall (DeepSeek)']

    st.dataframe(comparison, use_container_width=True)

    # Key insights
    st.subheader("📊 Key Insights")

    agreement_count = comparison['Overall Agreement'].sum()
    total_students = len(comparison)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Students with Same Overall Score", agreement_count, f"({agreement_count/total_students*100:.0f}%)")

    with col2:
        disagreement = total_students - agreement_count
        st.metric("Students with Different Scores", disagreement, f"({disagreement/total_students*100:.0f}%)")

    with col3:
        # Which model is stricter
        a1_gpt = (df_v3_gpt['overall_cefr_level'] == 'A1').sum()
        a1_ds = (df_v3_ds['overall_cefr_level'] == 'A1').sum()
        if a1_gpt > a1_ds:
            st.info(f"**GPT-4o-mini is stricter** ({a1_gpt} A1 vs {a1_ds} A1)")
        else:
            st.info(f"**DeepSeek is stricter** ({a1_ds} A1 vs {a1_gpt} A1)")

    # Heatmap of disagreements
    st.subheader("Disagreement Heatmap")

    disagreement_students = comparison[~comparison['Overall Agreement']].index.tolist()

    if disagreement_students:
        st.write(f"Students with disagreement: {disagreement_students}")

        # Show detailed comparison for disagreement cases
        st.subheader("Detailed View of Disagreements")
        for student in disagreement_students[:5]:  # Show first 5
            with st.expander(f"{student}"):
                st.write(f"**GPT-4o-mini**: {comparison.loc[student, 'Overall (GPT)']}")
                st.write(f"**DeepSeek**: {comparison.loc[student, 'Overall (DeepSeek)']}")
    else:
        st.success("✅ Both models agree on all students!")

# ============================================================================
# MAIN APP STRUCTURE
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview & Comparison",
    "🔍 Student Drill-Down",
    "📐 Dimension Analysis",
    "🤖 LLM Comparison"
])

with tab1:
    tab_overview()

with tab2:
    tab_student_drilldown()

with tab3:
    tab_dimension_analysis()

with tab4:
    tab_llm_comparison()

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
---
**About this Dashboard:**
- **v1: Key Indicators Only** - Simplified evaluation using only key CEFR indicators
- **v2: Full Guidelines** - Comprehensive evaluation with full CEFR guidelines
- **v3: Measurable Evidence** - Rigorous evaluation requiring quantifiable evidence
- **GPT-4o-mini** - Primary LLM model used for v1, v2, and v3
- **DeepSeek R1 Distill** - Alternative model for comparison with v3

Dashboard built with Streamlit | Data from CEFR Evaluation Pipeline
""")
