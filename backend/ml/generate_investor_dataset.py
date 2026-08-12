"""
Professional Synthetic Investor Dataset Generator
Generates realistic investor profiles for Random Forest training.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import random

SEED = 42
NUM_RECORDS = 50000  # change to 20000 or 100000 if required

np.random.seed(SEED)
random.seed(SEED)

GOALS = [
    "Wealth Creation",
    "Retirement",
    "Children Education",
    "Home Purchase",
    "Emergency Fund",
    "Business Expansion"
]

HORIZONS = ["<3 Years","3-5 Years","5-10 Years","10+ Years"]
RISKS = ["Low","Medium","High"]

def weighted_profile(age,income,sr,horizon,risk,goal):
    score = 0.0

    # age
    if age < 30: score += 1.8
    elif age < 45: score += 1.0
    else: score += 0.2

    # income
    if income > 200000: score += 2.0
    elif income > 100000: score += 1.3
    elif income > 50000: score += 0.7

    # savings rate
    if sr > 0.35: score += 1.8
    elif sr > 0.22: score += 1.0
    elif sr > 0.12: score += 0.5

    # horizon
    score += {
        "<3 Years":0.2,
        "3-5 Years":0.8,
        "5-10 Years":1.4,
        "10+ Years":2.0
    }[horizon]

    # risk tolerance
    score += {"Low":0.2,"Medium":1.2,"High":2.2}[risk]

    # goal
    score += {
        "Wealth Creation":1.6,
        "Business Expansion":1.5,
        "Home Purchase":0.9,
        "Children Education":0.8,
        "Emergency Fund":0.3,
        "Retirement":0.4
    }[goal]

    # realistic overlap
    score += np.random.normal(0,1.1)

    # convert score to probabilities
    if score < 4.5:
        probs=[0.80,0.18,0.02]
    elif score < 6.0:
        probs=[0.55,0.35,0.10]
    elif score < 7.5:
        probs=[0.20,0.60,0.20]
    elif score < 9.0:
        probs=[0.08,0.45,0.47]
    else:
        probs=[0.02,0.20,0.78]

    return np.random.choice(
        ["Conservative","Moderate","Aggressive"],
        p=probs
    )

rows=[]

for _ in range(NUM_RECORDS):

    age=int(np.clip(np.random.normal(37,12),18,70))

    income=int(np.clip(
        np.random.lognormal(np.log(70000),0.7),
        15000,500000))

    sr=float(np.clip(np.random.normal(0.23,0.11),0.03,0.70))

    savings=int(income*sr)

    if age<30:
        horizon=np.random.choice(HORIZONS,p=[0.05,0.15,0.35,0.45])
    elif age<45:
        horizon=np.random.choice(HORIZONS,p=[0.10,0.25,0.40,0.25])
    else:
        horizon=np.random.choice(HORIZONS,p=[0.25,0.35,0.30,0.10])

    if age<30:
        goal=np.random.choice(
            GOALS,
            p=[0.45,0.03,0.08,0.20,0.14,0.10]
        )
    elif age<45:
        goal=np.random.choice(
            GOALS,
            p=[0.28,0.12,0.18,0.20,0.12,0.10]
        )
    else:
        goal=np.random.choice(
            GOALS,
            p=[0.12,0.45,0.15,0.10,0.12,0.06]
        )

    risk=np.random.choice(RISKS,p=[0.30,0.40,0.30])

    profile=weighted_profile(
        age,income,sr,horizon,risk,goal
    )

    # 3% edge cases
    if np.random.rand()<0.03:
        profile=np.random.choice(
            ["Conservative","Moderate","Aggressive"]
        )

    rows.append({
        "Age":age,
        "Monthly_Income":income,
        "Monthly_Savings":savings,
        "Savings_Rate":round(sr*100,2),
        "Investment_Horizon":horizon,
        "Risk_Tolerance":risk,
        "Financial_Goal":goal,
        "Investor_Profile":profile
    })

df=pd.DataFrame(rows)

# Use project-relative path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
out_dir = backend_dir / "datasets"
out_dir.mkdir(exist_ok=True)

csv_path=out_dir/"investor_risk_dataset.csv"
df.to_csv(csv_path,index=False)

report=out_dir/"dataset_report.txt"

with open(report,"w") as f:
    f.write("Synthetic Investor Dataset Report\n")
    f.write("="*40+"\n\n")
    f.write(f"Rows: {len(df)}\n")
    f.write(f"Columns: {len(df.columns)}\n\n")
    f.write("Class Distribution\n")
    f.write(str(df["Investor_Profile"].value_counts(normalize=True)*100))
    f.write("\n\nMissing Values\n")
    f.write(str(df.isna().sum()))
    f.write("\n\nDuplicates: ")
    f.write(str(df.duplicated().sum()))

print("\nDataset generated successfully.")
print(csv_path)
print(df["Investor_Profile"].value_counts())
