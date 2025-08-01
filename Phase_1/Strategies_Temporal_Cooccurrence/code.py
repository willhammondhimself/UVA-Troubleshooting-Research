#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Define strategy columns
strategy_cols = [
    'Trial and error', 'Consider alternatives', 'Rebuild', 'Tracing',
    'Isolation / split half', 'Output testing', 'Gain domain knowledge', 
    'Pattern matching'
]

# Get student data (excluding master scan)
student_data = df[df['student_id'] != 'ECE_ScanMaster'].copy()

# Filter to only students who have strategy data (NEW sheets)
students_with_strategies = student_data.groupby('student_id')[strategy_cols].sum().sum(axis=1) > 0
students_with_strategy_data = students_with_strategies[students_with_strategies].index
strategy_student_data = student_data[student_data['student_id'].isin(students_with_strategy_data)]

total_strategy_students = len(students_with_strategy_data)
total_strategy_steps = len(strategy_student_data)

print(f"Students with strategy data: {total_strategy_students}")
print(f"Total strategy student step observations: {total_strategy_steps}")

# Create temporal co-occurrence matrix
# For each strategy X, what % of steps with strategy X also have strategy Y?
cooccurrence_matrix = np.zeros((len(strategy_cols), len(strategy_cols)))

for i, strategy_x in enumerate(strategy_cols):
    # Find all steps where strategy X occurs
    steps_with_x = strategy_student_data[strategy_student_data[strategy_x] == 1]
    total_x_steps = len(steps_with_x)
    
    if total_x_steps > 0:
        for j, strategy_y in enumerate(strategy_cols):
            # Count how many of those steps also have strategy Y
            steps_with_both = len(steps_with_x[steps_with_x[strategy_y] == 1])
            # Calculate percentage
            cooccurrence_matrix[i, j] = (steps_with_both / total_x_steps) * 100
    else:
        # If strategy X never occurs, set all percentages to 0
        cooccurrence_matrix[i, :] = 0

# Create the visualization
plt.style.use('seaborn-v0_8-white')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# Create figure
fig, ax = plt.subplots(figsize=(12, 10))

# Create heatmap
im = ax.imshow(cooccurrence_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)

# Set ticks and labels
ax.set_xticks(range(len(strategy_cols)))
ax.set_yticks(range(len(strategy_cols)))

# Create shorter labels for better readability
strategy_short_labels = [
    'Trial/error', 'Consider alt', 'Rebuild', 'Tracing',
    'Isolation', 'Output test', 'Gain knowledge', 'Pattern match'
]

ax.set_xticklabels(strategy_short_labels, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(strategy_short_labels, fontsize=9)

# Add percentage text to each cell
for i in range(len(strategy_cols)):
    for j in range(len(strategy_cols)):
        text = ax.text(j, i, f'{cooccurrence_matrix[i, j]:.0f}%',
                      ha="center", va="center", color="black" if cooccurrence_matrix[i, j] < 50 else "white",
                      fontsize=8, fontweight='bold')

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.6)
cbar.set_label('Co-occurrence Percentage', rotation=270, labelpad=20, fontsize=12)

# Set title and labels
ax.set_title('Strategies vs Strategies Co-occurrence Matrix (Temporal)\n' + 
             'Row Strategy → Column Strategy: % of steps with Row Strategy that also have Column Strategy\n' +
             f'Based on {total_strategy_steps} step observations from {total_strategy_students} students with strategy data', 
             fontsize=14, fontweight='bold', pad=20)

ax.set_xlabel('Strategy Y (co-occurring)', fontsize=12, fontweight='bold')
ax.set_ylabel('Strategy X (reference)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_path / 'strategies_vs_strategies_temporal_cooccurrence.png', dpi=300, bbox_inches='tight')
plt.show()

# Create summary text file
summary_text = f"""Temporal co-occurrence matrix showing when strategies occur together in the same step. 
Each cell shows: "Of steps where Row Strategy occurred, what percentage also had Column Strategy?"

Analysis limited to {total_strategy_students} students with strategy data (NEW observation sheets). 
Based on {total_strategy_steps} step observations from these students. Diagonal shows 100% (strategies always co-occur with themselves)."""

with open(output_path / 'strategies_vs_strategies_temporal_cooccurrence.txt', 'w') as f:
    f.write(summary_text)

print(f"\nAnalysis complete! Files saved to: {output_path}")
print("- strategies_vs_strategies_temporal_cooccurrence.png")
print("- strategies_vs_strategies_temporal_cooccurrence.txt")

# Print some key insights
print("\nKey Insights:")
print("Strategies with highest average co-occurrence with other strategies:")
avg_cooccurrence = np.mean(cooccurrence_matrix, axis=1)
for i, strategy in enumerate(strategy_cols):
    print(f"  {strategy}: {avg_cooccurrence[i]:.1f}%")

print("\nMost common strategy pairs (temporal):")
# Find highest co-occurrence pairs (excluding diagonal)
max_pairs = []
for i in range(len(strategy_cols)):
    for j in range(len(strategy_cols)):
        if i != j and cooccurrence_matrix[i, j] > 10:  # Lower threshold since strategies are less frequent
            max_pairs.append((strategy_cols[i], strategy_cols[j], cooccurrence_matrix[i, j]))

max_pairs.sort(key=lambda x: x[2], reverse=True)
for pair in max_pairs[:10]:  # Top 10 pairs
    print(f"  {pair[0]} → {pair[1]}: {pair[2]:.1f}%")

# Print strategy usage counts
print("\nStrategy usage in steps:")
strategy_usage = strategy_student_data[strategy_cols].sum().sort_values(ascending=False)
for strategy in strategy_usage.index:
    if strategy_usage[strategy] > 0:
        print(f"  {strategy}: {strategy_usage[strategy]} steps ({strategy_usage[strategy]/total_strategy_steps*100:.1f}%)")