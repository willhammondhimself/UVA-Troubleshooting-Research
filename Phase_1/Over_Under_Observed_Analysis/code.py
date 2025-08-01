#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set up paths
base_path = Path("/Users/willhammond/Summer '25 Research/Data Analysis (ECE)/troubleshooting_analysis_system")
data_path = base_path / "outputs" / "data_exports" / "processed_observation_data.csv"
output_path = base_path / "Updated_Outputs" / "Phase 1"

# Create output directory if it doesn't exist
output_path.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading processed observation data...")
df = pd.read_csv(data_path)

# Define action and strategy columns
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

# Get ECE_MasterScan data (ground truth)
master_data = df[df['student_id'] == 'ECE_ScanMaster'].copy()
print(f"ECE_MasterScan has {len(master_data)} steps")

# Find what actions and strategies the master scan observed
master_actions = set()
master_strategies = set()

for _, row in master_data.iterrows():
    for action in action_cols:
        if row[action] == 1:
            master_actions.add(action)
    for strategy in strategy_cols:
        if row[strategy] == 1:
            master_strategies.add(strategy)

print(f"Master scan observed {len(master_actions)} unique actions: {master_actions}")
print(f"Master scan observed {len(master_strategies)} unique strategies: {master_strategies}")

# Get student data (excluding master scan)
student_data = df[df['student_id'] != 'ECE_ScanMaster'].copy()
total_students = len(student_data['student_id'].unique())

# Count students who have strategy data (NEW sheets)
students_with_strategies = student_data.groupby('student_id')[strategy_cols].sum().sum(axis=1)
new_sheet_students = (students_with_strategies > 0).sum()

print(f"Students with strategy data (NEW sheets): {new_sheet_students}")
print(f"Total students: {total_students}")

# Calculate observation percentages for each behavior
all_behaviors = action_cols + strategy_cols
observation_data = []

for behavior in all_behaviors:
    # Calculate percentage of students who observed this behavior
    student_observed = student_data.groupby('student_id')[behavior].sum() > 0
    pct_observed = (student_observed.sum() / total_students) * 100
    
    # Check if this behavior was in master scan
    is_action = behavior in action_cols
    if is_action:
        in_master_scan = behavior in master_actions
        behavior_type = 'Action'
    else:
        in_master_scan = behavior in master_strategies
        behavior_type = 'Strategy'
    
    observation_data.append({
        'behavior': behavior,
        'type': behavior_type,
        'pct_observed': pct_observed,
        'in_master_scan': in_master_scan,
        'students_observed': student_observed.sum()
    })

# Create DataFrame for plotting
plot_df = pd.DataFrame(observation_data)

# Sort by observation percentage for better visualization
plot_df = plot_df.sort_values('pct_observed', ascending=False)

# Create the visualization
plt.style.use('seaborn-v0_8-white')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Create colors based on master scan presence and type
colors = []
labels = []

for _, row in plot_df.iterrows():
    if row['in_master_scan']:
        if row['type'] == 'Action':
            colors.append('#2E8B57')  # Green for actions in master scan
            labels.append('Action (in Master Scan)')
        else:
            colors.append('#228B22')  # Dark green for strategies in master scan
            labels.append('Strategy (in Master Scan)')
    else:
        if row['type'] == 'Action':
            colors.append('#4682B4')  # Blue for actions NOT in master scan
            labels.append('Action (over-observed)')
        else:
            colors.append('#1E90FF')  # Light blue for strategies NOT in master scan
            labels.append('Strategy (over-observed)')

# Create bar chart
bars = ax.bar(range(len(plot_df)), plot_df['pct_observed'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)

# Add percentage labels on bars
for i, (bar, pct) in enumerate(zip(bars, plot_df['pct_observed'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{pct:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Customize the plot
ax.set_xticks(range(len(plot_df)))
ax.set_xticklabels(plot_df['behavior'], rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Percentage of Students Who Observed', fontsize=12, fontweight='bold')
ax.set_title('Student Observation Rates: Actions and Strategies vs Expert Baseline\n' + 
             f'Total Students: {total_students} | Students with Strategy Data: {new_sheet_students}', 
             fontsize=14, fontweight='bold', pad=20)

# Create legend
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='#2E8B57', alpha=0.8, edgecolor='black', label='Actions in Master Scan'),
    plt.Rectangle((0,0),1,1, facecolor='#228B22', alpha=0.8, edgecolor='black', label='Strategies in Master Scan'), 
    plt.Rectangle((0,0),1,1, facecolor='#4682B4', alpha=0.8, edgecolor='black', label='Actions NOT in Master Scan'),
    plt.Rectangle((0,0),1,1, facecolor='#1E90FF', alpha=0.8, edgecolor='black', label='Strategies NOT in Master Scan')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

# Set y-axis limits
ax.set_ylim(0, 105)

# Add grid for better readability
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_path / 'over_under_observed_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create summary text file
summary_text = f"""This analysis compares student observation rates against the expert baseline (ECE_MasterScan). 
Actions and strategies observed by students are categorized by whether they appeared in the master scan (ground truth) or not, revealing patterns of over-observation and under-observation.

Key findings: {total_students} total students analyzed, with {new_sheet_students} having strategy data from NEW observation sheets."""

with open(output_path / 'over_under_observed_analysis.txt', 'w') as f:
    f.write(summary_text)

print(f"\nAnalysis complete! Files saved to: {output_path}")
print("- over_under_observed_analysis.png")
print("- over_under_observed_analysis.txt")

# Print detailed results
print("\nDetailed Results:")
for _, row in plot_df.iterrows():
    status = "IN Master Scan" if row['in_master_scan'] else "NOT in Master Scan"
    print(f"{row['behavior']} ({row['type']}): {row['pct_observed']:.1f}% - {status}")