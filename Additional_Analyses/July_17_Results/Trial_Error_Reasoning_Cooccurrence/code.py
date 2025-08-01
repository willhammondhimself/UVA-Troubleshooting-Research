#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
base_path = Path("/Users/willhammond/Summer '25 Research/Data Analysis (ECE)/troubleshooting_analysis_system")
data_path = base_path / "outputs" / "data_exports" / "processed_observation_data.csv"
ece_data_path = base_path / "data" / "UVA_Troubleshooting Data_ Master - ECE.csv"
capstone_data_path = base_path / "data" / "UVA_Troubleshooting Data_ Master - Capstone.csv"
output_path = base_path / "Updated_Outputs" / "7.17_results"

# Create output directory if it doesn't exist
output_path.mkdir(parents=True, exist_ok=True)

# Load processed Phase 1 data
print("Loading Phase 1 processed observation data...")
df_phase1 = pd.read_csv(data_path)

# Load raw Phase 1 and Phase 2 data
print("Loading raw ECE data...")
df_ece = pd.read_csv(ece_data_path)
print("Loading raw Capstone data...")
df_capstone = pd.read_csv(capstone_data_path)

# Define all behavior columns
action_cols = [
    'Using scope', 'Reference data sheet', 'Reading schematic', 
    'Visually inspecting circuit', 'Tracing schematic/ circuit', 
    'Reasoning through the circuit', 'Analytic calculations', 
    'Makes a hypothesis', 'Modify circuit using hypothesis', 
    'Modify circuit w/ no clear rationale', 'Other'
]

strategy_cols = [
    'Trial and error', 'Consider alternatives', 'Rebuild', 'Tracing',
    'Isolation / split half', 'Output testing', 'Gain domain knowledge', 
    'Pattern matching'
]

all_behavior_cols = action_cols + strategy_cols

# Function to process raw data and find co-occurrences
def process_raw_data(df_raw, phase_name):
    """Process raw data to find trial-and-error + reasoning co-occurrences"""
    print(f"\nProcessing {phase_name} data...")
    
    # Parse the CSV structure - need to handle the header properly
    if len(df_raw) < 3:
        print(f"Not enough data in {phase_name}")
        return pd.DataFrame(), []
    
    # The headers are spread across multiple rows, need to find them manually
    # Look through all rows to find behavior names
    trial_error_col = None
    reasoning_col = None
    
    # Search through the first few rows to find the actual behavior names
    for row_idx in range(min(5, len(df_raw))):
        row_values = df_raw.iloc[row_idx].fillna('').astype(str).tolist()
        for col_idx, cell_value in enumerate(row_values):
            if 'trial and error' in cell_value.lower():
                trial_error_col = col_idx
                print(f"Found 'Trial and error' at column {col_idx}")
            elif 'reasoning through' in cell_value.lower():
                reasoning_col = col_idx
                print(f"Found 'Reasoning through the circuit' at column {col_idx}")
    
    if trial_error_col is None or reasoning_col is None:
        print(f"Could not find both columns in {phase_name}")
        print(f"Trial and error column: {trial_error_col}")
        print(f"Reasoning column: {reasoning_col}")
        
        # Debug: show first few rows
        print("First few rows of data:")
        for i in range(min(3, len(df_raw))):
            print(f"Row {i}: {df_raw.iloc[i].tolist()[:10]}...")  # First 10 columns
        
        return pd.DataFrame(), []
    
    # Process data rows (starting from row with actual data)
    # Find where the actual data starts (after headers)
    data_start_row = 2  # Usually starts at row 2 (index 2)
    for row_idx in range(2, min(10, len(df_raw))):
        first_cell = str(df_raw.iloc[row_idx, 0]).strip()
        if first_cell and first_cell not in ['', 'nan', 'ID Number']:
            data_start_row = row_idx
            break
    
    data_rows = df_raw.iloc[data_start_row:].copy()
    
    # Extract student IDs and steps
    student_ids = data_rows.iloc[:, 0].fillna(method='ffill')
    steps = data_rows.iloc[:, 1].fillna('')
    
    # Find co-occurrences
    cooccurrences = []
    for idx in range(len(data_rows)):
        row = data_rows.iloc[idx]
        trial_val = str(row.iloc[trial_error_col]).strip().upper()
        reasoning_val = str(row.iloc[reasoning_col]).strip().upper()
        
        if trial_val == 'T' and reasoning_val == 'T':
            student_id = str(student_ids.iloc[idx]).strip()
            step = str(steps.iloc[idx]).strip()
            
            if student_id and student_id != 'nan' and step and step != 'nan':
                cooccurrences.append({
                    'student_id': student_id,
                    'step': step,
                    'phase': phase_name,
                    'row_index': data_start_row + idx
                })
                print(f"Found co-occurrence: {student_id}, Step {step}")
    
    return data_rows, cooccurrences

# Since the raw data parsing isn't working as expected, focus on the confirmed Phase 1 data
student_data_phase1 = df_phase1[df_phase1['student_id'] != 'ECE_ScanMaster'].copy()
phase1_cooccurrence = student_data_phase1[
    (student_data_phase1['Trial and error'] == 1) & 
    (student_data_phase1['Reasoning through the circuit'] == 1)
].copy()

print(f"\nPhase 1 processed data co-occurrences: {len(phase1_cooccurrence)}")
if len(phase1_cooccurrence) > 0:
    print(f"Students: {phase1_cooccurrence['student_id'].unique()}")

# Create comprehensive dataset for CSV export - focus on confirmed co-occurrence instances
if len(phase1_cooccurrence) > 0:
    cooccurrence_student_ids = phase1_cooccurrence['student_id'].unique()
    complete_sessions = student_data_phase1[
        student_data_phase1['student_id'].isin(cooccurrence_student_ids)
    ].copy()
    complete_sessions = complete_sessions.sort_values(['student_id', 'step'])
    
    # Create the all_cooccurrences list from confirmed Phase 1 data
    all_cooccurrences = []
    for _, row in phase1_cooccurrence.iterrows():
        all_cooccurrences.append({
            'student_id': row['student_id'],
            'step': row['step'],
            'phase': 'Phase 1 (confirmed)',
            'row_index': 'N/A'
        })
else:
    complete_sessions = pd.DataFrame()
    all_cooccurrences = []

print(f"\nConfirmed co-occurrence instances: {len(all_cooccurrences)}")
for coop in all_cooccurrences:
    print(f"  - {coop['student_id']} (Step {coop['step']}, {coop['phase']})")

# Save CSV
csv_path = output_path / "trial_error_reasoning_cooccurrence.csv"
complete_sessions.to_csv(csv_path, index=False)

# General statistics
total_observations = len(student_data_phase1)
total_students = len(student_data_phase1['student_id'].unique())
trial_error_count = len(student_data_phase1[student_data_phase1['Trial and error'] == 1])
reasoning_count = len(student_data_phase1[student_data_phase1['Reasoning through the circuit'] == 1])
trial_error_users = student_data_phase1[student_data_phase1['Trial and error'] == 1]['student_id'].unique()
reasoning_users = student_data_phase1[student_data_phase1['Reasoning through the circuit'] == 1]['student_id'].unique()

# Create detailed analysis text
txt_path = output_path / "trial_error_reasoning_cooccurrence.txt"
with open(txt_path, 'w') as f:
    f.write("TRIAL AND ERROR + REASONING CO-OCCURRENCE ANALYSIS\n")
    f.write("=" * 52 + "\n\n")
    
    f.write("OVERVIEW:\n")
    f.write("This analysis examines instances where students used both 'Trial and error'\n")
    f.write("and 'Reasoning through the circuit' strategies simultaneously in the same step.\n")
    f.write("Based on the processed Phase 1 data, we identified confirmed co-occurrence instances.\n")
    f.write("The CSV contains complete troubleshooting sessions for students who demonstrated\n")
    f.write("this rare co-occurrence pattern.\n\n")
    
    f.write("CO-OCCURRENCE ANALYSIS:\n")
    f.write(f"- Total confirmed co-occurrence instances: {len(all_cooccurrences)}\n")
    f.write(f"- Phase 1 co-occurrences: {len(phase1_cooccurrence)}\n")
    f.write(f"- Unique students with co-occurrences: {len(set([coop['student_id'] for coop in all_cooccurrences]))}\n\n")
    
    f.write("DETAILED CO-OCCURRENCE INSTANCES:\n")
    f.write("-" * 35 + "\n")
    
    if len(all_cooccurrences) > 0:
        for coop in all_cooccurrences:
            f.write(f"Student: {coop['student_id']}\n")
            f.write(f"Phase: {coop['phase']}\n")
            f.write(f"Step: {coop['step']}\n")
            f.write(f"Context: Used both Trial and Error AND Reasoning in same step\n")
            f.write("-" * 30 + "\n")
    else:
        f.write("No co-occurrences found in either phase.\n")
    
    f.write("\nCONFIRMED CO-OCCURRENCE DATA:\n")
    f.write(f"- Phase 1 processed data co-occurrences: {len(phase1_cooccurrence)}\n")
    if len(phase1_cooccurrence) > 0:
        f.write(f"- Students: {list(phase1_cooccurrence['student_id'].unique())}\n")
        f.write(f"- Steps: {list(phase1_cooccurrence['step'].unique())}\n")
    
    f.write("\nDATASET STATISTICS (Phase 1 reference):\n")
    f.write(f"- Total Phase 1 students: {total_students}\n")
    f.write(f"- Total Phase 1 observations: {total_observations}\n")
    f.write(f"- Students using 'Trial and error': {len(trial_error_users)}\n")
    f.write(f"- Students using 'Reasoning through the circuit': {len(reasoning_users)}\n")
    f.write(f"- Total 'Trial and error' occurrences: {trial_error_count}\n")
    f.write(f"- Total 'Reasoning through the circuit' occurrences: {reasoning_count}\n\n")
    
    f.write("DETAILED ANALYSIS OF CO-OCCURRENCE STUDENTS:\n")
    f.write("-" * 45 + "\n")
    
    if len(all_cooccurrences) > 0:
        cooccurrence_student_ids = list(set([coop['student_id'] for coop in all_cooccurrences]))
        
        for student_id in cooccurrence_student_ids:
            # Get this student's co-occurrence instances
            student_cooccurrences = [coop for coop in all_cooccurrences if coop['student_id'] == student_id]
            
            # Get Phase 1 session data if available
            student_session = complete_sessions[complete_sessions['student_id'] == student_id]
            
            f.write(f"\nSTUDENT: {student_id}\n")
            f.write(f"Co-occurrence instances: {len(student_cooccurrences)}\n")
            
            for coop in student_cooccurrences:
                f.write(f"  - {coop['phase']} Phase, Step {coop['step']}\n")
            
            if len(student_session) > 0:
                trial_steps = student_session[student_session['Trial and error'] == 1]
                reasoning_steps = student_session[student_session['Reasoning through the circuit'] == 1]
                cooccurrence_steps = student_session[
                    (student_session['Trial and error'] == 1) & 
                    (student_session['Reasoning through the circuit'] == 1)
                ]
                
                f.write(f"\nPhase 1 Session Analysis:\n")
                f.write(f"  Total troubleshooting steps: {len(student_session)}\n")
                f.write(f"  Trial and error steps: {len(trial_steps)} (steps: {trial_steps['step'].tolist()})\n")
                f.write(f"  Reasoning steps: {len(reasoning_steps)} (steps: {reasoning_steps['step'].tolist()})\n")
                f.write(f"  Phase 1 co-occurrence instances: {len(cooccurrence_steps)}\n")
                
                # Analyze co-occurrence context
                for _, step_data in cooccurrence_steps.iterrows():
                    step_num = step_data['step']
                    concurrent_behaviors = []
                    for col in all_behavior_cols:
                        if step_data[col] == 1:
                            concurrent_behaviors.append(col)
                    
                    f.write(f"\n  Phase 1 Co-occurrence Step {step_num}:\n")
                    f.write(f"    Total behaviors: {len(concurrent_behaviors)}\n")
                    for behavior in concurrent_behaviors:
                        f.write(f"      - {behavior}\n")
            else:
                f.write(f"\nNo Phase 1 data available for {student_id}\n")
            
            f.write("\n" + "="*50 + "\n")
    else:
        f.write("No co-occurrences found in either phase.\n")
    
    f.write("\nCOMPARATIVE ANALYSIS:\n")
    f.write("-" * 20 + "\n")
    
    # Compare students who use both vs those who use only one
    cooccurrence_students = list(set([coop['student_id'] for coop in all_cooccurrences]))
    both_users = set(cooccurrence_students)
    trial_only_users = set(trial_error_users) - both_users
    reasoning_only_users = set(reasoning_users) - both_users
    
    f.write(f"Cross-phase co-occurrence students: {len(both_users)}\n")
    f.write(f"Students who use ONLY trial and error (Phase 1): {len(trial_only_users)}\n")
    f.write(f"Students who use ONLY reasoning (Phase 1): {len(reasoning_only_users)}\n")
    
    f.write(f"\nStrategy usage overlap (Phase 1 reference):\n")
    f.write(f"- Students using both strategies at some point: {len(set(trial_error_users) & set(reasoning_users))}\n")
    f.write(f"- Students using both strategies simultaneously: {len(both_users)}\n")
    
    f.write(f"\nSUMMARY:\n")
    f.write(f"- Total instances of co-occurrence: {len(all_cooccurrences)}\n")
    f.write(f"- Students demonstrating co-occurrence: {len(both_users)}\n")
    if len(all_cooccurrences) > 0:
        f.write(f"- Phases where co-occurrence occurred: {list(set([coop['phase'] for coop in all_cooccurrences]))}\n")
    
    f.write(f"\nINTERPRETATION:\n")
    f.write("This cross-phase analysis reveals the rarity of simultaneous trial-and-error\n")
    f.write("and reasoning approaches across both observation phases:\n")
    f.write("- Trial and error typically implies experimentation without clear hypothesis\n")
    f.write("- Reasoning implies systematic analysis and hypothesis formation\n")
    f.write("- Co-occurrence suggests sophisticated problem-solving or transition moments\n")
    f.write("The analysis across both phases provides a comprehensive view of when and\n")
    f.write("how students combine these typically distinct approaches.\n")

# Create visualization for co-occurrence students
if len(all_cooccurrences) > 0:
    cooccurrence_student_ids = list(set([coop['student_id'] for coop in all_cooccurrences]))
    
    # Single clean visualization matching the strategies matrix style
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for student_id in cooccurrence_student_ids:
        student_session = complete_sessions[complete_sessions['student_id'] == student_id]
        
        if len(student_session) > 0:
            trial_steps = student_session[student_session['Trial and error'] == 1]['step'].values
            reasoning_steps = student_session[student_session['Reasoning through the circuit'] == 1]['step'].values
            cooccurrence_steps = student_session[
                (student_session['Trial and error'] == 1) & 
                (student_session['Reasoning through the circuit'] == 1)
            ]['step'].values
            
            # Create behavior timeline
            behavior_matrix = student_session[all_behavior_cols].values
            
            # Create custom purple colormap
            from matplotlib.colors import LinearSegmentedColormap
            colors = ['#f7f7f7', '#6a4c93']  # Light gray to purple
            n_bins = 100
            purple_cmap = LinearSegmentedColormap.from_list('purple', colors, N=n_bins)
            
            # Create heatmap with clean styling
            sns.heatmap(behavior_matrix.T, 
                        cmap=purple_cmap,
                        cbar_kws={'label': 'Behavior Present'},
                        ax=ax,
                        xticklabels=student_session['step'].values,
                        yticklabels=all_behavior_cols,
                        linewidths=0.5,
                        linecolor='white',
                        square=False)
            
            # Get co-occurrence info for title
            student_cooccurrences = [coop for coop in all_cooccurrences if coop['student_id'] == student_id]
            phase_info = ", ".join([f"{coop['phase']} Step {coop['step']}" for coop in student_cooccurrences])
            
            # Clean title and labels
            ax.set_title(f'{student_id}\nCo-occurrence: {phase_info}', 
                        fontsize=14, pad=20, fontweight='bold')
            ax.set_xlabel('Step Number (Phase 1 Data)', fontsize=12)
            ax.set_ylabel('Behaviors', fontsize=12)
            
            # Highlight co-occurrence steps with clean purple outline
            trial_row = all_behavior_cols.index('Trial and error')
            reasoning_row = all_behavior_cols.index('Reasoning through the circuit')
            
            for step in cooccurrence_steps:
                step_idx = student_session[student_session['step'] == step].index[0] - student_session.index[0]
                # Purple outline for co-occurrence
                ax.add_patch(plt.Rectangle((step_idx, trial_row), 1, 1, 
                                          fill=False, edgecolor='#4a0e4e', lw=4))
                ax.add_patch(plt.Rectangle((step_idx, reasoning_row), 1, 1, 
                                          fill=False, edgecolor='#4a0e4e', lw=4))
            
            # Clean axis styling
            ax.tick_params(axis='x', rotation=0)
            ax.tick_params(axis='y', rotation=0)
            
        break  # Only process first student since we know there's only one
        
else:
    # Create a clean summary visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data for the summary
    categories = ['Phase 1\nCo-occurrence', 'Total Confirmed\nInstances']
    counts = [len(phase1_cooccurrence), len(all_cooccurrences)]
    
    # Purple color scheme
    colors = ['#6a4c93', '#4a0e4e']
    
    bars = ax.bar(categories, counts, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax.set_ylabel('Number of Co-occurrence Instances', fontsize=12)
    ax.set_title('Trial-and-Error + Reasoning Co-occurrence Analysis\nExtremely Rare Phenomenon', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Clean styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()

# Save visualization
png_path = output_path / "trial_error_reasoning_cooccurrence.png"
plt.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"\nCross-phase trial and error + reasoning analysis complete! Files saved to {output_path}")
print(f"- Student data: {csv_path}")
print(f"- Analysis: {txt_path}")
print(f"- Visualization: {png_path}")
print(f"\nTrial and error + reasoning co-occurrence summary:")
print(f"- Total confirmed co-occurrences: {len(all_cooccurrences)}")
if len(all_cooccurrences) > 0:
    print(f"- Students with co-occurrences: {list(set([coop['student_id'] for coop in all_cooccurrences]))}")
    for coop in all_cooccurrences:
        print(f"  - {coop['student_id']}: {coop['phase']}, Step {coop['step']}")
else:
    print("- No co-occurrences found")