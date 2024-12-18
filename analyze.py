import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.gridspec import GridSpec

def create_comprehensive_report(exercise_mappings, year=2024, figsize=(20, 28)):
    """
    Create a single comprehensive report combining detailed stats and visualizations.
    """
    # Run the analysis first
    stats, dfs = analyze_exercises(exercise_mappings)
    main_exercises = list(exercise_mappings.keys())
    
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(5, 2, figure=fig, height_ratios=[1.2, 0.8, 0.8, 0.8, 0.8])
    
    # title for the entire report
    fig.suptitle(f'Training Analysis Report - {year}', fontsize=24, y=0.95)
    
    # 1. stats table
    ax_stats = fig.add_subplot(gs[0, :])
    create_detailed_stats_table(ax_stats, stats, main_exercises)
    
    # 2. training days 
    ax_days = fig.add_subplot(gs[1, 0])
    create_training_days_plot(ax_days, stats, main_exercises)
    
    # 3. sets per session
    ax_sets = fig.add_subplot(gs[1, 1])
    create_sets_per_session_plot(ax_sets, stats, main_exercises)
    
    # 4. volume comparison
    ax_volume = fig.add_subplot(gs[2, :])
    create_volume_plot(ax_volume, stats, main_exercises)
    
    # 5. weight progression
    ax_progress = fig.add_subplot(gs[3:, :])
    create_weight_progression_plot(ax_progress, dfs, main_exercises)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/training_report.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_detailed_stats_table(ax, stats, exercises):
    """Create a detailed table visualization of all statistics"""
    ax.axis('tight')
    ax.axis('off')
    
    headers = [
        'Exercise',
        'Training\nDays',
        'Total\nSets',
        'Sets per\nSession',
        'Total\nReps',
        'Total\nVolume (lbs)',
        'Average\nWeight (lbs)',
        'Max\nWeight (lbs)'
    ]
    
    table_data = []
    for ex in exercises:
        if ex in stats:
            s = stats[ex]
            name = ex.replace(" (Barbell)", "")
            sets_per_day = s['total_sets'] / s['training_days']
            row = [
                name,
                f"{s['training_days']}",
                f"{s['total_sets']}",
                f"{sets_per_day:.1f}",
                f"{s['total_reps']:,}",
                f"{s['total_volume']:,.0f}",
                f"{s['avg_weight']:.1f}",
                f"{s['max_weight']:.1f}"
            ]
            table_data.append(row)
    
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        loc='center',
        cellLoc='center'
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Color the header row
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#E6E6E6')
    
    ax.set_title('Detailed Exercise Statistics', pad=20, fontsize=14)

def create_sets_per_session_plot(ax, stats, exercises):
    """Create a bar plot showing average sets per session"""
    sets_per_session = [stats[ex]['total_sets']/stats[ex]['training_days'] 
                       for ex in exercises if ex in stats]
    labels = [ex.replace(" (Barbell)", "") for ex in exercises if ex in stats]
    
    ax.bar(labels, sets_per_session, alpha=0.8)
    ax.set_title('Average Sets per Session')
    ax.set_ylabel('Sets')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(sets_per_session):
        ax.text(i, v, f'{v:.1f}', ha='center', va='bottom')
    
    ax.tick_params(axis='x', rotation=45)

def create_training_days_plot(ax, stats, exercises):
    """Create the training days comparison plot"""
    days = [stats[ex]['training_days'] for ex in exercises if ex in stats]
    labels = [ex.replace(" (Barbell)", "") for ex in exercises if ex in stats]
    
    ax.bar(labels, days, alpha=0.8)
    ax.set_title('Training Days Comparison')
    ax.set_ylabel('Number of Days')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(days):
        ax.text(i, v, f'{v}', ha='center', va='bottom')
    
    ax.tick_params(axis='x', rotation=45)

def create_volume_plot(ax, stats, exercises):
    """Create the volume comparison plot"""
    volumes = [stats[ex]['total_volume'] for ex in exercises if ex in stats]
    labels = [ex.replace(" (Barbell)", "") for ex in exercises if ex in stats]
    
    bars = ax.bar(labels, volumes, alpha=0.8)
    ax.set_title('Total Volume Comparison')
    ax.set_ylabel('Total Volume (lbs)')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom')
    
    ax.tick_params(axis='x', rotation=45)

def create_weight_progression_plot(ax, dfs, exercises):
    """Create the weight progression plot"""
    for exercise in exercises:
        if exercise not in dfs:
            continue
            
        df = dfs[exercise]
        label = exercise.replace(" (Barbell)", "")
        
        ax.scatter(df['Date'], df['Weight'], alpha=0.5, label=label, s=30)
        
        # Add trend line
        z = np.polyfit(df['Date'].astype(np.int64), df['Weight'], 1)
        p = np.poly1d(z)
        ax.plot(df['Date'], p(df['Date'].astype(np.int64)), "--", alpha=0.8)
    
    ax.set_title('Weight Progression Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Weight (lbs)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

def analyze_exercises(exercise_mappings, year=2024):
    df = pd.read_csv('data/strong.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'].dt.year == year]
    
    all_stats = {}
    all_dfs = {}
    
    for main_exercise, alt_names in exercise_mappings.items():
        exercise_df = df[df['Exercise Name'].isin(alt_names)].copy()
        
        if len(exercise_df) == 0:
            continue
        
        exercise_df['Volume'] = exercise_df['Weight'] * exercise_df['Reps']
        exercise_df = exercise_df.sort_values('Date')
        
        unique_days = exercise_df['Date'].dt.date.nunique()
        
        stats = {
            'total_volume': exercise_df['Volume'].sum(),
            'total_sets': len(exercise_df),
            'total_reps': exercise_df['Reps'].sum(),
            'avg_weight': exercise_df['Weight'].mean(),
            'max_weight': exercise_df['Weight'].max(),
            'training_days': unique_days
        }
        
        all_stats[main_exercise] = stats
        all_dfs[main_exercise] = exercise_df
    
    return all_stats, all_dfs

if __name__ == "__main__":
    try:
        exercise_mappings = {
            "Squat (Barbell)": ["Squat (Barbell)"],
            "Deadlift (Barbell)": ["Deadlift (Barbell)", "Deadlift Old Data "],
            "Bench Press (Barbell)": ["Bench Press (Barbell)", "Bench press Backup "]
        }
        
        create_comprehensive_report(exercise_mappings)
        print("Report has been generated and saved as 'output/training_report.png'")
        
    except FileNotFoundError:
        print("Error: Could not find 'data/strong.csv'. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
