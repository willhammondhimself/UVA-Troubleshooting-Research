# UVA ECE Troubleshooting Research: Student Observation Skills Analysis

## Project Overview

This repository documents a comprehensive research project analyzing student observation skills in electrical and computer engineering troubleshooting contexts. The research examines how students observe troubleshooting activities and how these observation skills relate to their own troubleshooting performance.

### Research Context

The project investigates two fundamental questions in engineering education:
1. **How accurately do students observe troubleshooting behavior?**
2. **What patterns emerge in student observation skills?**

The research uses a controlled experimental design where students observe both standardized video demonstrations and live peer troubleshooting sessions, providing rich data on observation accuracy and patterns.

## Research Structure

### Phase 1: Standardized Video Observation
- **Methodology**: 59 students watched the same video of Professor Caroline troubleshooting a circuit
- **Ground Truth**: Caroline's own observations ("master scan") provide expert baseline
- **Data**: ~295 observation records across 19 behavioral categories (11 actions, 8 strategies)
- **Focus**: Objective accuracy measurement and observation pattern analysis

### Phase 2: Live Peer Observation  
- **Methodology**: Students observed peers troubleshooting the same circuit in real-time
- **Data**: Live observation of various troubleshooting approaches to the same problem
- **Focus**: Peer observation dynamics and troubleshooting effectiveness patterns

## Key Research Findings

### Observation Accuracy Patterns
- **Over-Observation Bias**: 58% of students reported seeing more actions than actually occurred
- **Strategy Over-Attribution**: Students tend to see more strategic thinking than experts recognize
- **Systematic Differences**: Most students (64%) show moderate differences from expert observations

### Troubleshooting Effectiveness Insights
- **Quality over Quantity**: Successful troubleshooters used fewer actions per step (1.63 vs 1.88)
- **Hypothesis-Driven Success**: 95% of successful students formed clear hypotheses before modifications
- **Sequential Patterns**: Students follow consistent "theory-first, measurement-last" approaches

### Temporal and Co-occurrence Patterns
- **Action Relationships**: Certain actions consistently co-occur in troubleshooting steps
- **Strategy Sequences**: Advanced temporal analysis reveals strategy progression patterns
- **Rebuild Strategy**: Always used as final step, indicating last-resort approach

## Repository Structure

### [Phase 1 Analyses](./Phase_1/)
Standardized video observation analysis with expert ground truth comparison.

#### Co-occurrence Analyses
- **[Action Temporal Co-occurrence](./Phase_1/Action_Temporal_Cooccurrence/)** - Actions occurring together in same step
- **[Action Non-Temporal Co-occurrence](./Phase_1/Action_NonTemporal_Cooccurrence/)** - Actions used by same students
- **[Strategies vs Actions Temporal](./Phase_1/Strategies_vs_Actions_Temporal/)** - Strategy-action relationships in same step
- **[Strategies Temporal Co-occurrence](./Phase_1/Strategies_Temporal_Cooccurrence/)** - Strategies occurring together in same step  
- **[Strategies Non-Temporal Co-occurrence](./Phase_1/Strategies_NonTemporal_Cooccurrence/)** - Strategies used by same students

#### Observation Accuracy Analyses  
- **[Student Distribution vs Expert](./Phase_1/Student_Distribution_vs_Expert/)** - Quantitative observation differences
- **[Comprehensive Difference Index](./Phase_1/Comprehensive_Difference_Index/)** - Multi-dimensional accuracy assessment
- **[Too Many Strategies Noticed](./Phase_1/Too_Many_Strategies_Noticed/)** - Strategy over-attribution patterns
- **[Over/Under Observed Analysis](./Phase_1/Over_Under_Observed_Analysis/)** - Specific behavior observation patterns

### [Phase 2 Analyses](./Phase_2/)
Live peer observation and troubleshooting effectiveness analysis.

- **[Success Patterns Finding 1](./Phase_2/Success_Patterns_Finding_1/)** - Action efficiency and success correlation
- **[Troubleshooting Approaches Finding 2](./Phase_2/Troubleshooting_Approaches_Finding_2/)** - Sequential troubleshooting patterns
- **[Action Effectiveness Finding 3](./Phase_2/Action_Effectiveness_Finding_3/)** - Hypothesis-driven repair effectiveness
- **[Focus Types Qualitative 2](./Phase_2/Focus_Types_Qualitative_2/)** - Troubleshooting attention patterns

### [Additional Analyses](./Additional_Analyses/)
Advanced and updated analyses with refined methodologies.

#### [July 17 Results](./Additional_Analyses/July_17_Results/)
Specialized analyses from continued research efforts.

- **[Rebuild Students Analysis](./Additional_Analyses/July_17_Results/Rebuild_Students_Analysis/)** - Detailed analysis of rebuild strategy users
- **[Strategies Temporal Plus1](./Additional_Analyses/July_17_Results/Strategies_Temporal_Plus1/)** - Advanced sequential strategy analysis
- **[Trial Error Reasoning Co-occurrence](./Additional_Analyses/July_17_Results/Trial_Error_Reasoning_Cooccurrence/)** - Rare simultaneous strategy usage

#### [Continued Results](./Additional_Analyses/Continued_Results/)
Updated versions of Phase 1 analyses with refined methodologies.

- **[Action Temporal Co-occurrence (Updated)](./Additional_Analyses/Continued_Results/Action_Temporal_Cooccurrence/)**
- **[Action Non-Temporal Co-occurrence (Updated)](./Additional_Analyses/Continued_Results/Action_NonTemporal_Cooccurrence/)**
- **[Over/Under Observed Analysis (Updated)](./Additional_Analyses/Continued_Results/Over_Under_Observed_Analysis/)**
- **[Strategies vs Actions Temporal (Updated)](./Additional_Analyses/Continued_Results/Strategies_vs_Actions_Temporal/)**
- **[Strategies Non-Temporal Co-occurrence (Updated)](./Additional_Analyses/Continued_Results/Strategies_NonTemporal_Cooccurrence/)**
- **[Strategies Temporal Co-occurrence (Updated)](./Additional_Analyses/Continued_Results/Strategies_Temporal_Cooccurrence/)**

## Data Collection Methodology

### Observation Categories

#### Actions (11 categories)
1. Using scope
2. Reference data sheet  
3. Reading schematic
4. Visually inspecting circuit
5. Tracing schematic/circuit
6. Reasoning through the circuit
7. Analytic calculations
8. Makes a hypothesis
9. Modify circuit using hypothesis
10. Modify circuit w/ no clear rationale
11. Other

#### Strategies (8 categories)
1. Trial and error
2. Consider alternatives
3. Rebuild
4. Tracing
5. Isolation / split half
6. Output testing
7. Gain domain knowledge
8. Pattern matching

### Data Collection Issues

**Important Note**: The research encountered a significant methodological issue where two different observation sheets were used:
- **OLD SHEET**: Only contained actions (resulted in 0 strategy observations)
- **NEW SHEET**: Contained both actions and strategies

This affected 47 students (OLD sheet) vs 12 students (NEW sheet), requiring careful analysis separation and methodology adjustments in later analyses.

## Statistical Overview

- **Total Students**: 59 (Phase 1) + additional Phase 2 participants
- **Total Observations**: 293 step observations (Phase 1)
- **Expert Baseline**: Caroline's master scan (6 troubleshooting steps)
- **Strategy Data**: Limited to 12 students due to sheet versioning

## Research Impact

This research provides crucial insights for engineering education:

1. **Observation Training**: Students need explicit training in accurate troubleshooting observation
2. **Hypothesis Formation**: The most critical skill for troubleshooting success
3. **Efficiency Focus**: Teaching focused, methodical approaches over comprehensive action lists
4. **Pattern Recognition**: Understanding normal co-occurrence patterns helps identify effective troubleshooting

## Technical Implementation

All analyses were implemented in Python using:
- **pandas** for data processing
- **numpy** for numerical computations
- **matplotlib/seaborn** for visualization
- **pathlib** for file management

Each analysis directory contains:
- `figure.png` - The visualization
- `README.md` - Detailed analysis description and interpretation
- `code.py` - Complete Python implementation (where available)

---

*This repository represents a comprehensive analysis of engineering student observation and troubleshooting skills, providing valuable insights for engineering education research and curriculum development.*
