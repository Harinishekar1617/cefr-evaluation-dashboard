"""
Utility functions for data processing and aggregation.
Contains helpers for filtering, cleaning, and organizing transcript data.
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple
import subprocess
import sys


def install_if_needed(package_name: str, import_name: str = None) -> None:
    """
    Install a Python package if it's not already installed.

    Args:
        package_name: Name to use with pip install (e.g., "openpyxl")
        import_name: Name to use with import (defaults to package_name if not specified)
    """
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name} is already installed")
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")


def filter_by_topics(df: pd.DataFrame, topics: List[str]) -> pd.DataFrame:
    """
    Keep only rows with specific topics.

    Args:
        df: DataFrame with a 'topic' column
        topics: List of topic names to keep (e.g., ['Introducing Yourself', 'General talk'])

    Returns:
        Filtered DataFrame
    """
    df_filtered = df[df['topic'].isin(topics)].copy()
    print(f"Filtered for topics {topics}: {len(df_filtered)} rows")
    return df_filtered


def keep_latest_session_per_student(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each student-activity pair, keep only rows from the LATEST session date.

    This ensures we're evaluating their most recent performance.

    Args:
        df: DataFrame with 'student_name', 'activity_name', and 'session_date' columns

    Returns:
        Filtered DataFrame with only latest sessions
    """
    # Find the maximum (latest) date for each student-activity combination
    max_dates = df.groupby(['student_name', 'activity_name'])['session_date'].max().reset_index()
    max_dates.columns = ['student_name', 'activity_name', 'max_session_date']

    # Keep only rows matching the latest date
    df_filtered = df.merge(max_dates,
                          left_on=['student_name', 'activity_name', 'session_date'],
                          right_on=['student_name', 'activity_name', 'max_session_date'])

    df_filtered = df_filtered.drop('max_session_date', axis=1)
    df_filtered = df_filtered.sort_values(['student_name', 'session_date']).reset_index(drop=True)

    print(f"✅ Kept latest session per student-activity: {len(df_filtered)} rows")
    print(f"   Unique students: {df_filtered['student_name'].nunique()}")

    return df_filtered


def calculate_word_count_per_turn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total word count for each dialogue turn.

    Args:
        df: DataFrame with 'interviewer_text' and 'student_text' columns

    Returns:
        DataFrame with new 'total_words' column
    """
    df = df.copy()
    df['total_words'] = (
        df['interviewer_text'].str.split().str.len() +
        df['student_text'].str.split().str.len()
    )
    return df


def get_mode_words_per_student(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the MODE (most frequent word count) for each student.

    MODE is preferred over MEAN/MEDIAN because it shows the typical turn length.

    Args:
        df: DataFrame with 'student_name' and 'total_words' columns

    Returns:
        DataFrame with student_name and mode_words columns
    """
    from scipy import stats

    mode_words_list = []

    for student_name in df['student_name'].unique():
        student_words = df[df['student_name'] == student_name]['total_words'].values

        try:
            # Use scipy to calculate mode (most frequent value)
            mode_val = stats.mode(student_words, keepdims=True).mode[0]
        except:
            # Fallback to median if mode calculation fails
            mode_val = df[df['student_name'] == student_name]['total_words'].median()

        mode_words_list.append({
            'student_name': student_name,
            'mode_words': mode_val
        })

    df_mode = pd.DataFrame(mode_words_list)
    return df_mode.sort_values('mode_words', ascending=False)


def filter_by_min_mode_words(df: pd.DataFrame, min_mode_words: int) -> Tuple[pd.DataFrame, List[str]]:
    """
    Filter for students whose typical word count is above a threshold.

    This ensures we only evaluate students who speak enough to be assessed fairly.

    Args:
        df: DataFrame with 'student_name' column
        min_mode_words: Minimum mode word count threshold

    Returns:
        Tuple of (filtered DataFrame, list of qualified student names)
    """
    df_mode = get_mode_words_per_student(df)

    print(f"\nMODE words by student (top 10):")
    print(df_mode.head(10))

    # Get students above threshold
    qualified_students = df_mode[df_mode['mode_words'] >= min_mode_words]['student_name'].tolist()

    # Filter main dataframe
    df_filtered = df[df['student_name'].isin(qualified_students)].copy()

    print(f"\n✅ Filtered for mode words >= {min_mode_words}: {len(df_filtered)} rows")
    print(f"   Students qualified: {len(qualified_students)}/{df['student_name'].nunique()}")

    return df_filtered, qualified_students


def filter_by_word_count_per_turn(df: pd.DataFrame, min_words: int) -> pd.DataFrame:
    """
    Filter for dialogue turns with word count above a threshold.

    This removes very short turns that don't provide enough data for evaluation.

    Args:
        df: DataFrame with 'total_words' column
        min_words: Minimum word count per turn

    Returns:
        Filtered DataFrame
    """
    df = df.copy()
    df_filtered = df[df['total_words'] > min_words].copy()

    print(f"After filtering for word_count > {min_words}: {len(df_filtered)} rows")
    print(f"Students with {min_words}+ word turns: {df_filtered['student_name'].nunique()}")

    return df_filtered


def sample_turns_per_student(df: pd.DataFrame, n_samples: int = 5, random_state: int = 42) -> pd.DataFrame:
    """
    Sample a fixed number of dialogue turns per student.

    This creates a balanced dataset where each student contributes the same number of samples.

    Args:
        df: DataFrame with 'student_name' column
        n_samples: Number of turns to sample per student
        random_state: Random seed for reproducibility

    Returns:
        DataFrame with sampled turns
    """
    df_sampled = df.groupby('student_name', group_keys=False).apply(
        lambda x: x.sample(n=min(n_samples, len(x)), random_state=random_state)
    ).reset_index(drop=True)

    print(f"\nTotal rows after sampling: {len(df_sampled)}")
    print(f"Students: {df_sampled['student_name'].nunique()}")
    print(f"Expected: {df_sampled['student_name'].nunique()} students × {n_samples} turns")

    return df_sampled


def aggregate_by_mode(df_individual: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate individual dialogue turn scores to student level using MODE.

    MODE (most frequent level) is more robust than mean for categorical CEFR levels.

    Args:
        df_individual: DataFrame with individual dialogue turn evaluations
                      Must have columns: student_name, range, accuracy, fluency, coherence, overall_cefr_level

    Returns:
        DataFrame with one row per student, showing mode score for each dimension
    """
    aggregated = []

    for student_name in sorted(df_individual['student_name'].unique()):
        student_evals = df_individual[df_individual['student_name'] == student_name]

        # Calculate mode (most frequent value) for each dimension
        def get_mode(series):
            mode_vals = series.mode()
            return mode_vals[0] if len(mode_vals) > 0 else 'Unknown'

        aggregated.append({
            'student_name': student_name,
            'num_dialogue_turns': len(student_evals),
            'range_mode': get_mode(student_evals['range']),
            'accuracy_mode': get_mode(student_evals['accuracy']),
            'fluency_mode': get_mode(student_evals['fluency']),
            'coherence_mode': get_mode(student_evals['coherence']),
            'overall_mode': get_mode(student_evals['overall_cefr_level']),
            'range_variance': f"{student_evals['range'].min()} to {student_evals['range'].max()}",
            'accuracy_variance': f"{student_evals['accuracy'].min()} to {student_evals['accuracy'].max()}",
            'fluency_variance': f"{student_evals['fluency'].min()} to {student_evals['fluency'].max()}",
        })

    return pd.DataFrame(aggregated)


def save_results_to_excel(df_individual: pd.DataFrame,
                          df_aggregated: pd.DataFrame,
                          output_path: Path) -> None:
    """
    Save evaluation results to Excel with multiple sheets.

    Args:
        df_individual: DataFrame with individual dialogue turn results
        df_aggregated: DataFrame with aggregated student-level results
        output_path: Path to save the Excel file
    """
    # Install openpyxl if needed (required for Excel writing)
    install_if_needed('openpyxl')

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Individual dialogue turns
        df_individual.to_excel(
            writer,
            sheet_name='Individual Turns',
            index=False
        )
        print(f"✅ Saved {len(df_individual)} individual dialogue turn results")

        # Sheet 2: Aggregated student-level results
        df_aggregated.to_excel(
            writer,
            sheet_name='Aggregated by MODE',
            index=False
        )
        print(f"✅ Saved aggregated results")

        # Sheet 3: Summary statistics
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Dialogue Turns',
                'Number of Students',
                'Average Turns per Student'
            ],
            'Value': [
                len(df_individual),
                len(df_aggregated),
                len(df_individual) / len(df_aggregated)
            ]
        })
        summary_stats.to_excel(
            writer,
            sheet_name='Summary',
            index=False
        )
        print(f"✅ Saved summary statistics")


def save_results_to_csv(df_individual: pd.DataFrame,
                        df_aggregated: pd.DataFrame,
                        output_dir: Path,
                        file_suffix: str = "") -> None:
    """
    Save evaluation results to CSV files as backup.

    Args:
        df_individual: DataFrame with individual dialogue turn results
        df_aggregated: DataFrame with aggregated student-level results
        output_dir: Directory to save CSV files
        file_suffix: Suffix to add to filenames (e.g., "all_students")
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Individual results
    csv_individual = output_dir / f"cefr_individual_turns_{file_suffix}.csv"
    df_individual.to_csv(csv_individual, index=False)
    print(f"✅ Individual turns CSV: {csv_individual}")

    # Aggregated results
    csv_aggregated = output_dir / f"cefr_aggregated_{file_suffix}.csv"
    df_aggregated.to_csv(csv_aggregated, index=False)
    print(f"✅ Aggregated results CSV: {csv_aggregated}")


def convert_justifications_to_full_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert justifications from compact format to full JSON format.

    Use this if you need to switch an existing Excel file from compact to full format.
    Reads the file, converts the justification column, and saves it back.

    Args:
        df: DataFrame with 'justification' column containing compact format

    Returns:
        DataFrame with justifications converted to full JSON format (no-op if already full format)
    """
    # Note: This is a placeholder. In practice, you would need to re-run evaluations
    # to get the full JSON format, since compact format discards score information
    print("⚠️  To switch to full format, re-run evaluations with format_type='full'")
    print("    The compact format cannot be losslessly converted back to full format.")
    return df
