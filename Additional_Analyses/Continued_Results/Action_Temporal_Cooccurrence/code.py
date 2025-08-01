#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
base_path = Path("/Users/willhammond/Summer '25 Research/Data Analysis (ECE)/troubleshooting_analysis_system")
data_path = base_path / "outputs" / "data_exports" / "processed_observation_data.csv"
output_path = base_path / "Updated_Outputs" / "continued_results"

# Create output directory if it doesn't exist
output_path.mkdir(parents=True, exist_ok=True)

# Load data
print("Loading processed observation data...")
df = pd.read_csv(data_path)

# Define action columns in the desired order (bottom to top for Y-axis)
action_cols_ordered = [
    'Other',  # Bottom (row 0, displayed at bottom)
    'Modify circuit w/ no clear rationale',
    'Modify circuit using hypothesis', 
    'Makes a hypothesis',
    'Analytic calculations',
    'Reasoning through the circuit',
    'Tracing schematic/ circuit',
    'Visually inspecting circuit',
    'Reading schematic',
    'Reference data sheet',
    'Using scope'  # Top (row 10, displayed at top)
]

# Get student data (excluding master scan)
student_data = df[df['student_id'] != 'ECE_ScanMaster'].copy()
total_students = len(student_data['student_id'].unique())

print(f"Total students: {total_students}")
print(f"Total student step observations: {len(student_data)}")

# Create temporal co-occurrence matrix
# For each action X, what % of steps with X also have action Y?
cooccurrence_matrix = np.zeros((len(action_cols_ordered), len(action_cols_ordered)))

for i, action_x in enumerate(action_cols_ordered):
    # Find all steps where action X occurs
    steps_with_x = student_data[student_data[action_x] == 1]
    total_x_steps = len(steps_with_x)
    
    if total_x_steps > 0:
        for j, action_y in enumerate(action_cols_ordered):
            # Count how many of those steps also have action Y
            steps_with_both = len(steps_with_x[steps_with_x[action_y] == 1])
            # Calculate percentage
            cooccurrence_matrix[i, j] = (steps_with_both / total_x_steps) * 100
    else:
        # If action X never occurs, set all percentages to 0
        cooccurrence_matrix[i, :] = 0

# Create the visualization
plt.style.use('seaborn-v0_8-white')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# Create figure
fig, ax = plt.subplots(figsize=(14, 12))

# Flip the matrix so that "Using scope" appears in bottom-left corner
# We need to reverse the Y-axis ordering (flip rows)
cooccurrence_matrix_flipped = np.flipud(cooccurrence_matrix)
action_cols_flipped = list(reversed(action_cols_ordered))

# Create heatmap
im = ax.imshow(cooccurrence_matrix_flipped, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)

# Set ticks and labels
ax.set_xticks(range(len(action_cols_ordered)))
ax.set_yticks(range(len(action_cols_ordered)))

# Create shorter labels for better readability
short_labels = [
    'Other', 'Modify (no rationale)', 'Modify (hyp)', 'Hypothesis', 'Calculations',
    'Reasoning', 'Trace circuit', 'Visual inspect', 'Schematic', 'Data sheet', 'Scope'
]

# For X-axis, use normal order
ax.set_xticklabels(short_labels, rotation=45, ha='right', fontsize=9)

# For Y-axis, use flipped order to match the flipped matrix
short_labels_flipped = list(reversed(short_labels))
ax.set_yticklabels(short_labels_flipped, fontsize=9)

# Add percentage text to each cell
for i in range(len(action_cols_ordered)):
    for j in range(len(action_cols_ordered)):
        text = ax.text(j, i, f'{cooccurrence_matrix_flipped[i, j]:.0f}%',
                      ha="center", va="center", 
                      color="black" if cooccurrence_matrix_flipped[i, j] < 50 else "white",
                      fontsize=8, fontweight='bold')

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.6)
cbar.set_label('Co-occurrence Percentage', rotation=270, labelpad=20, fontsize=12)

# Set title and labels
ax.set_title('Actions vs Actions Co-occurrence Matrix (Temporal)\n' + 
             'Row Action → Column Action: % of steps with Row Action that also have Column Action\n' +
             f'Based on {len(student_data)} step observations from {total_students} students', 
             fontsize=14, fontweight='bold', pad=20)

ax.set_xlabel('Action Y (co-occurring)', fontsize=12, fontweight='bold')
ax.set_ylabel('Action X (reference)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_path / 'actions_vs_actions_temporal_cooccurrence.png', dpi=300, bbox_inches='tight')
plt.show()

# Create summary text file
summary_text = f"""Temporal co-occurrence matrix showing when actions occur together in the same step. 
Each cell shows: "Of steps where Row Action occurred, what percentage also had Column Action?"

Matrix layout: Using scope appears in bottom-left corner, with actions arranged symmetrically on both axes.
Analysis based on {len(student_data)} step observations from {total_students} students. Diagonal shows 100% (actions always co-occur with themselves)."""

with open(output_path / 'actions_vs_actions_temporal_cooccurrence.txt', 'w') as f:
    f.write(summary_text)

print(f"\nAnalysis complete! Files saved to: {output_path}")
print("- actions_vs_actions_temporal_cooccurrence.png")
print("- actions_vs_actions_temporal_cooccurrence.txt")

# Print some key insights for verification
print("\nKey Insights:")
print("Actions with highest average co-occurrence with other actions:")
avg_cooccurrence = np.mean(cooccurrence_matrix, axis=1)
for i, action in enumerate(action_cols_ordered):
    print(f"  {action}: {avg_cooccurrence[i]:.1f}%")

print("\nMost common action pairs (temporal):")
# Find highest co-occurrence pairs (excluding diagonal)
max_pairs = []
for i in range(len(action_cols_ordered)):
    for j in range(len(action_cols_ordered)):
        if i != j and cooccurrence_matrix[i, j] > 30:  # Threshold for "high" co-occurrence
            max_pairs.append((action_cols_ordered[i], action_cols_ordered[j], cooccurrence_matrix[i, j]))

max_pairs.sort(key=lambda x: x[2], reverse=True)
for pair in max_pairs[:10]:  # Top 10 pairs
    print(f"  {pair[0]} → {pair[1]}: {pair[2]:.1f}%")

print(f"\nMatrix verification:")
print(f"  - Bottom-left corner (Using scope → Using scope): {cooccurrence_matrix_flipped[-1, 0]:.1f}%")
print(f"  - Second position (Data sheet → Data sheet): {cooccurrence_matrix_flipped[-2, 1]:.1f}%")