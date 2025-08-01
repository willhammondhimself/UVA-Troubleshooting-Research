#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
base_path = Path("/Users/willhammond/Summer '25 Research/Data Analysis (ECE)/troubleshooting_analysis_system")
data_path = base_path / "outputs" / "data_exports" / "processed_observation_data.csv"
output_path = base_path / "Updated_Outputs" / "7.17_results"

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

# Create temporal +1 step co-occurrence matrix including "N/A (last strategy)" column
# For each strategy X in step N, what % of time does strategy Y occur in step N+1?
# Include tracking for strategies that appear in the final step (no next step)
extended_cols = strategy_cols + ['N/A (last strategy)']
temporal_plus1_matrix = np.zeros((len(strategy_cols), len(extended_cols)))
strategy_counts = np.zeros(len(strategy_cols))
last_step_counts = np.zeros(len(strategy_cols))

# Process each student separately
for student_id in students_with_strategy_data:
    student_steps = strategy_student_data[strategy_student_data['student_id'] == student_id].sort_values('step')
    
    # Look at consecutive steps
    for i in range(len(student_steps) - 1):
        current_step = student_steps.iloc[i]
        next_step = student_steps.iloc[i + 1]
        
        # Check if steps are truly consecutive
        if next_step['step'] == current_step['step'] + 1:
            # For each strategy in current step
            for j, strategy_x in enumerate(strategy_cols):
                if current_step[strategy_x] == 1:
                    strategy_counts[j] += 1
                    # Check what strategies occur in next step
                    for k, strategy_y in enumerate(strategy_cols):
                        if next_step[strategy_y] == 1:
                            temporal_plus1_matrix[j][k] += 1
    
    # Check the final step for each student (no next step available)
    if len(student_steps) > 0:
        final_step = student_steps.iloc[-1]
        for j, strategy_x in enumerate(strategy_cols):
            if final_step[strategy_x] == 1:
                last_step_counts[j] += 1

# Add last step counts to the matrix and strategy counts
for i in range(len(strategy_cols)):
    strategy_counts[i] += last_step_counts[i]
    temporal_plus1_matrix[i][-1] = last_step_counts[i]  # Last column is "N/A (last strategy)"

# Convert counts to percentages
for i in range(len(strategy_cols)):
    if strategy_counts[i] > 0:
        temporal_plus1_matrix[i] = (temporal_plus1_matrix[i] / strategy_counts[i]) * 100

# Create DataFrame for easier handling
temporal_plus1_df = pd.DataFrame(
    temporal_plus1_matrix,
    index=strategy_cols,
    columns=extended_cols
)

# Save matrix to CSV
csv_path = output_path / "strategies_vs_strategies_temporal_plus1.csv"
temporal_plus1_df.to_csv(csv_path)

# Create detailed analysis text
txt_path = output_path / "strategies_vs_strategies_temporal_plus1.txt"
with open(txt_path, 'w') as f:
    f.write("STRATEGIES VS STRATEGIES TEMPORAL +1 STEP ANALYSIS\n")
    f.write("=" * 55 + "\n\n")
    
    f.write("METHODOLOGY:\n")
    f.write("This analysis examines temporal sequences in troubleshooting strategies.\n")
    f.write("For each strategy X that occurs in step N, we calculate the percentage\n")
    f.write("of time that strategy Y occurs in step N+1 (the immediately following step).\n")
    f.write("Only consecutive steps within the same student's session are considered.\n")
    f.write("Additionally, we track when strategies appear in the final step of a session\n")
    f.write("(marked as 'N/A (last strategy)' since no next step exists).\n\n")
    
    f.write("DATASET INFORMATION:\n")
    f.write(f"- Students with strategy data: {total_strategy_students}\n")
    f.write(f"- Total strategy observations: {total_strategy_steps}\n")
    f.write(f"- Strategy categories analyzed: {len(strategy_cols)}\n")
    f.write(f"- Consecutive step pairs analyzed: {int(sum(strategy_counts))}\n\n")
    
    f.write("STRATEGY OCCURRENCE COUNTS:\n")
    for i, strategy in enumerate(strategy_cols):
        total_count = int(strategy_counts[i])
        last_step_count = int(last_step_counts[i])
        continuing_count = total_count - last_step_count
        f.write(f"- {strategy}: {total_count} total ({continuing_count} with next step, {last_step_count} final step)\n")
    f.write("\n")
    
    f.write("TOP TEMPORAL SEQUENCES (Strategy X → Strategy Y):\n")
    # Find top sequences
    sequences = []
    for i, strategy_x in enumerate(strategy_cols):
        for j, strategy_y in enumerate(extended_cols):
            if temporal_plus1_matrix[i][j] > 0:
                sequences.append((strategy_x, strategy_y, temporal_plus1_matrix[i][j], int(strategy_counts[i])))
    
    # Sort by percentage
    sequences.sort(key=lambda x: x[2], reverse=True)
    
    for seq in sequences[:20]:  # Top 20 sequences including final steps
        f.write(f"- {seq[0]} → {seq[1]}: {seq[2]:.1f}% (based on {seq[3]} occurrences)\n")
    
    f.write("\n\nSELF-CONTINUATION PATTERNS:\n")
    f.write("(How often a strategy continues to the next step vs. ends the session)\n")
    for i, strategy in enumerate(strategy_cols):
        if strategy_counts[i] > 0:
            self_continuation = temporal_plus1_matrix[i][i]
            final_step_pct = temporal_plus1_matrix[i][-1]  # Last column is "N/A (last strategy)"
            f.write(f"- {strategy}: {self_continuation:.1f}% continue, {final_step_pct:.1f}% final step\n")
    
    f.write("\n\nFINAL STEP ANALYSIS:\n")
    f.write("(Which strategies most commonly appear in the final troubleshooting step)\n")
    final_step_data = [(strategy_cols[i], temporal_plus1_matrix[i][-1], int(last_step_counts[i])) 
                       for i in range(len(strategy_cols)) if last_step_counts[i] > 0]
    final_step_data.sort(key=lambda x: x[1], reverse=True)
    for strategy, pct, count in final_step_data:
        f.write(f"- {strategy}: {pct:.1f}% of its occurrences are final steps ({count} instances)\n")
    
    f.write("\n\nINTERPRETATION:\n")
    f.write("High percentages indicate strong temporal associations between strategies.\n")
    f.write("Self-continuation patterns show how persistent each strategy tends to be.\n")
    f.write("Final step analysis reveals which strategies typically conclude troubleshooting sessions.\n")
    f.write("The 'N/A (last strategy)' column shows completion patterns - strategies that\n")
    f.write("frequently appear in final steps may indicate successful problem resolution.\n")

# Create visualization
plt.figure(figsize=(14, 10))
mask = temporal_plus1_matrix == 0
sns.heatmap(temporal_plus1_df, 
            annot=True, 
            fmt='.1f', 
            cmap='viridis',
            mask=mask,
            square=False,
            linewidths=0.5,
            cbar_kws={'label': 'Percentage (%)'})
plt.title('Strategies vs Strategies Temporal +1 Step Matrix\n(% of time Strategy Y follows Strategy X, including final steps)', 
          fontsize=14, pad=20)
plt.xlabel('Strategy in Step N+1 (or Session End)', fontsize=12)
plt.ylabel('Strategy in Step N', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

# Add a vertical line to separate the "N/A (last strategy)" column
ax = plt.gca()
ax.axvline(x=len(strategy_cols), color='red', linewidth=2, linestyle='--', alpha=0.7)

plt.tight_layout()

# Save visualization
png_path = output_path / "strategies_vs_strategies_temporal_plus1.png"
plt.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"\nAnalysis complete! Files saved to {output_path}")
print(f"- Matrix: {csv_path}")
print(f"- Analysis: {txt_path}")
print(f"- Visualization: {png_path}")