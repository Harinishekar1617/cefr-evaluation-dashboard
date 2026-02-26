"""
Functions for reading, parsing, and loading student transcripts.
Extracts dialogue turns, metadata, and prepares data for evaluation.
"""

import re
import pandas as pd
from pathlib import Path
from typing import List, Dict


def parse_transcript_from_csv_row(row: pd.Series, transcript_id: str) -> List[Dict]:
    """
    Parse a single transcript from CSV row and extract dialogue turns.

    Expected transcript format in CSV:
    [Interviewer]: Question text
    [Student]: Answer text
    ...

    Args:
        row: Pandas Series containing the CSV row
        transcript_id: Unique identifier for this transcript

    Returns:
        List of dictionaries, one per Q&A pair
        Each dict contains: student_name, topic, activity_name, session_time,
                           interviewer_text, student_text, transcript_id
    """
    dialogue_section = row.get('transcript', '')

    if not dialogue_section:
        return []

    # ========================================================================
    # EXTRACT METADATA FROM ROW
    # ========================================================================
    metadata = {
        'student_name': row.get('student_name', ''),
        'topic': row.get('topic_name', ''),
        'activity_name': row.get('activity_name', ''),
        'session_time': row.get('created_at', '')
    }

    # ========================================================================
    # PARSE DIALOGUE TURNS FROM TRANSCRIPT COLUMN
    # ========================================================================
    dialogue_turns = []
    lines = dialogue_section.split('\n')

    current_interviewer = None
    current_student = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line is from interviewer
        if line.startswith('[Interviewer]:'):
            # Extract text after "[Interviewer]:"
            match = re.match(r'\[Interviewer\]:\s*(.*)', line)
            if match:
                # If we have a complete Q&A pair, save it
                if current_interviewer is not None and current_student is not None:
                    dialogue_turns.append({
                        'transcript_id': transcript_id,
                        'student_name': metadata.get('student_name', ''),
                        'topic': metadata.get('topic', ''),
                        'activity_name': metadata.get('activity_name', ''),
                        'session_time': metadata.get('session_time', ''),
                        'interviewer_text': current_interviewer,
                        'student_text': current_student
                    })

                # Start new interviewer turn
                current_interviewer = match.group(1)
                current_student = None

        # Check if line is from student
        elif line.startswith('[Student]:'):
            # Extract text after "[Student]:"
            match = re.match(r'\[Student\]:\s*(.*)', line)
            if match:
                # Concatenate multiple student lines
                if current_student is None:
                    current_student = match.group(1)
                else:
                    current_student += ' ' + match.group(1)

    # Don't forget the last pair if it exists
    if current_interviewer is not None and current_student is not None:
        dialogue_turns.append({
            'transcript_id': transcript_id,
            'student_name': metadata.get('student_name', ''),
            'topic': metadata.get('topic', ''),
            'activity_name': metadata.get('activity_name', ''),
            'session_time': metadata.get('session_time', ''),
            'interviewer_text': current_interviewer,
            'student_text': current_student
        })

    return dialogue_turns


def load_all_transcripts(csv_file_path: Path) -> pd.DataFrame:
    """
    Load and parse all transcripts from CSV file(s).
    Supports single CSV or multiple CSV files (DET + FSSA).

    Args:
        csv_file_path: Path to CSV file or directory containing transcript CSVs

    Returns:
        DataFrame with all dialogue turns from all transcripts
    """
    # Determine if we have a single file or need to load multiple files
    if isinstance(csv_file_path, str):
        csv_file_path = Path(csv_file_path)

    all_data = []
    total_transcripts = 0

    # Handle directory with multiple CSVs
    if csv_file_path.is_dir():
        csv_files = list(csv_file_path.glob("*.csv"))
    else:
        csv_files = [csv_file_path]

    # Load each CSV file
    for csv_file in sorted(csv_files):
        if csv_file.name.startswith('.'):
            continue

        df_csv = pd.read_csv(csv_file)
        print(f"Found {len(df_csv)} transcripts in {csv_file.name}")
        total_transcripts += len(df_csv)

        # Parse each row and collect results
        for idx, row in df_csv.iterrows():
            # Generate transcript_id from student_name and row index
            transcript_id = f"{row.get('student_name', f'student_{idx}')}_{idx}"
            parsed_turns = parse_transcript_from_csv_row(row, transcript_id)
            all_data.extend(parsed_turns)

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    if len(df) > 0:
        # Convert session_time to datetime
        df['session_time'] = pd.to_datetime(df['session_time'])

        # Extract session date (without time)
        df['session_date'] = df['session_time'].dt.date

    print(f"✅ Parsed {len(df)} dialogue turns from {total_transcripts} transcripts")

    return df
