import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

def generate_chart(skill_counts: Counter, filename: str = "trend_chart.png"):
    """Generates and saves a bar chart of the top 10 skills."""
    # Get top 10 skills and convert to a Pandas DataFrame
    top_skills = skill_counts.most_common(10)
    
    if not top_skills:
        print("No skills to plot.")
        return
        
    df = pd.DataFrame(top_skills, columns=["Skill", "Frequency"])
    
    # Set up the visual style
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Create the bar plot
    ax = sns.barplot(x="Frequency", y="Skill", data=df, hue="Skill", palette="viridis", legend=False)
    
    plt.title("Top In-Demand Skills for Python Developers This Week", fontsize=16)
    plt.xlabel("Number of Mentions in Job Postings", fontsize=12)
    plt.ylabel("Technology", fontsize=12)
    plt.tight_layout()
    
    # Save the file locally
    plt.savefig(filename)
    plt.close()
    return filename
