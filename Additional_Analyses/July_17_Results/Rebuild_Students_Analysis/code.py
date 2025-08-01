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

# Get student data (excluding master scan)
student_data = df[df['student_id'] != 'ECE_ScanMaster'].copy()

# Find students who used "Rebuild" strategy
rebuild_users = student_data[student_data['Rebuild'] == 1]['student_id'].unique()
print(f"Students who used 'Rebuild' strategy: {list(rebuild_users)}")

# Get all data for rebuild users
rebuild_student_data = student_data[student_data['student_id'].isin(rebuild_users)].copy()
rebuild_student_data = rebuild_student_data.sort_values(['student_id', 'step'])

# Save detailed CSV with all steps for rebuild users
csv_path = output_path / "rebuild_students_analysis.csv"
rebuild_student_data.to_csv(csv_path, index=False)

# Analyze rebuild usage patterns
rebuild_analysis = {}
for student_id in rebuild_users:
    student_steps = rebuild_student_data[rebuild_student_data['student_id'] == student_id].copy()
    
    # Find when rebuild was used
    rebuild_steps = student_steps[student_steps['Rebuild'] == 1]
    
    # Get context for each rebuild usage
    rebuild_contexts = []
    for _, rebuild_step in rebuild_steps.iterrows():
        step_num = rebuild_step['step']
        
        # What other behaviors occurred in the same step?
        concurrent_behaviors = []
        for col in all_behavior_cols:
            if col != 'Rebuild' and rebuild_step[col] == 1:
                concurrent_behaviors.append(col)
        
        # What happened in previous step?
        prev_step_behaviors = []
        if step_num > 1:
            prev_step = student_steps[student_steps['step'] == step_num - 1]
            if not prev_step.empty:
                for col in all_behavior_cols:
                    if prev_step.iloc[0][col] == 1:
                        prev_step_behaviors.append(col)
        
        # What happened in next step?
        next_step_behaviors = []
        next_step = student_steps[student_steps['step'] == step_num + 1]
        if not next_step.empty:
            for col in all_behavior_cols:
                if next_step.iloc[0][col] == 1:
                    next_step_behaviors.append(col)
        
        rebuild_contexts.append({
            'step': step_num,
            'concurrent': concurrent_behaviors,
            'previous': prev_step_behaviors,
            'next': next_step_behaviors
        })
    
    rebuild_analysis[student_id] = {
        'total_steps': len(student_steps),
        'rebuild_steps': rebuild_steps['step'].tolist(),
        'rebuild_contexts': rebuild_contexts,
        'all_behaviors_used': [col for col in all_behavior_cols if student_steps[col].sum() > 0]
    }

# Create detailed analysis text
txt_path = output_path / "rebuild_students_analysis.txt"
with open(txt_path, 'w') as f:
    f.write("REBUILD STRATEGY USAGE ANALYSIS\n")
    f.write("=" * 35 + "\n\n")
    
    f.write("OVERVIEW:\n")
    f.write("This analysis examines the 4 students who used the 'Rebuild' strategy\n")
    f.write("during their troubleshooting process, providing detailed context about\n")
    f.write("when and how they employed this strategy.\n\n")
    
    f.write("STUDENTS WHO USED REBUILD:\n")
    for i, student_id in enumerate(rebuild_users, 1):
        f.write(f"{i}. {student_id}\n")
    f.write("\n")
    
    f.write("DETAILED STUDENT ANALYSIS:\n")
    f.write("-" * 30 + "\n")
    
    for student_id in rebuild_users:
        analysis = rebuild_analysis[student_id]
        f.write(f"\nSTUDENT: {student_id}\n")
        f.write(f"Total troubleshooting steps: {analysis['total_steps']}\n")
        f.write(f"Used rebuild in step(s): {analysis['rebuild_steps']}\n")
        f.write(f"Total behaviors used: {len(analysis['all_behaviors_used'])}\n")
        
        f.write(f"\nBehaviors used throughout session:\n")
        for behavior in analysis['all_behaviors_used']:
            f.write(f"  - {behavior}\n")
        
        f.write(f"\nREBUILD CONTEXT ANALYSIS:\n")
        for i, context in enumerate(analysis['rebuild_contexts'], 1):
            f.write(f"  Rebuild usage #{i} (Step {context['step']}):\n")
            f.write(f"    Concurrent behaviors: {', '.join(context['concurrent']) if context['concurrent'] else 'None'}\n")
            f.write(f"    Previous step behaviors: {', '.join(context['previous']) if context['previous'] else 'None'}\n")
            f.write(f"    Next step behaviors: {', '.join(context['next']) if context['next'] else 'None'}\n")
        
        f.write("\n" + "="*50 + "\n")
    
    f.write("\nCROSS-STUDENT PATTERNS:\n")
    f.write("-" * 25 + "\n")
    
    # Analyze common patterns
    all_concurrent = []
    all_previous = []
    all_next = []
    
    for student_id in rebuild_users:
        for context in rebuild_analysis[student_id]['rebuild_contexts']:
            all_concurrent.extend(context['concurrent'])
            all_previous.extend(context['previous'])
            all_next.extend(context['next'])
    
    f.write(f"Most common concurrent behaviors with rebuild:\n")
    concurrent_counts = pd.Series(all_concurrent).value_counts()
    for behavior, count in concurrent_counts.items():
        f.write(f"  - {behavior}: {count} times\n")
    
    f.write(f"\nMost common behaviors before rebuild:\n")
    previous_counts = pd.Series(all_previous).value_counts()
    for behavior, count in previous_counts.items():
        f.write(f"  - {behavior}: {count} times\n")
    
    f.write(f"\nMost common behaviors after rebuild:\n")
    next_counts = pd.Series(all_next).value_counts()
    for behavior, count in next_counts.items():
        f.write(f"  - {behavior}: {count} times\n")
    
    f.write(f"\nINTERPRETATION:\n")
    f.write("The 'Rebuild' strategy appears to be used when students recognize that\n")
    f.write("their current approach isn't working and they need to start over with\n")
    f.write("a different configuration. Context analysis reveals the circumstances\n")
    f.write("that typically lead to and follow from rebuild decisions.\n")

# Create visualization showing rebuild usage timeline
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Rebuild Strategy Usage Analysis', fontsize=16, y=0.98)

# Flatten axes for easier indexing
axes = axes.flatten()

for i, student_id in enumerate(rebuild_users):
    student_steps = rebuild_student_data[rebuild_student_data['student_id'] == student_id].copy()
    
    # Create a timeline showing all behaviors
    behavior_matrix = student_steps[all_behavior_cols].values
    
    # Create heatmap
    sns.heatmap(behavior_matrix.T, 
                cmap='viridis', 
                cbar=False,
                ax=axes[i],
                xticklabels=student_steps['step'].values,
                yticklabels=all_behavior_cols)
    
    axes[i].set_title(f'{student_id}', fontsize=12)
    axes[i].set_xlabel('Step Number')
    axes[i].set_ylabel('Behaviors')
    
    # Highlight rebuild steps
    rebuild_steps = student_steps[student_steps['Rebuild'] == 1]['step'].values
    for step in rebuild_steps:
        step_idx = student_steps[student_steps['step'] == step].index[0] - student_steps.index[0]
        rebuild_row = all_behavior_cols.index('Rebuild')
        axes[i].add_patch(plt.Rectangle((step_idx, rebuild_row), 1, 1, 
                                       fill=False, edgecolor='red', lw=3))

plt.tight_layout()

# Save visualization
png_path = output_path / "rebuild_students_analysis.png"
plt.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"\nRebuild analysis complete! Files saved to {output_path}")
print(f"- Student data: {csv_path}")
print(f"- Analysis: {txt_path}")
print(f"- Visualization: {png_path}")
print(f"\nFound {len(rebuild_users)} students who used rebuild strategy")
print(f"Total steps analyzed: {len(rebuild_student_data)}")