import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Keep this .py file and dataset (1)(1).csv in the same folder.
BASE = Path(__file__).resolve().parent
CSV = BASE / "dataset (1)(1).csv"
OUT = BASE / "hospital_analysis_outputs"
OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
df = pd.read_csv(CSV)
df.columns = df.columns.str.strip()
df["Admission Date"] = pd.to_datetime(df["Admission Date"], errors="coerce", dayfirst=True)

print("Total patient records:", len(df))
print("Unique patients:", df["Patient ID"].nunique())
print("Departments:", df["Department"].nunique())
print("\nMissing values:\n", df.isnull().sum())

def count_plot(column, title, filename, pie=False):
    counts = df[column].fillna("Unknown").value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    if pie:
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
    else:
        ax.bar(counts.index.astype(str), counts.values)
        ax.set_xlabel(column)
        ax.set_ylabel("Number of patients")
        ax.tick_params(axis="x", rotation=25)
        for bars in ax.containers:
            ax.bar_label(bars, padding=3)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return counts

columns = [
    ("Age Group", "Age group distribution", "01_age_group.png", False),
    ("Gender", "Gender distribution", "02_gender.png", True),
    ("Blood Group", "Blood group distribution", "03_blood_group.png", False),
    ("Department", "Patients by department", "04_department.png", False),
    ("Admission Type", "Admission type distribution", "05_admission_type.png", True),
    ("Treatment", "Treatment distribution", "06_treatment.png", False),
    ("Outcome", "Patient outcome distribution", "07_outcome.png", True),
    ("Bed Type", "Bed type distribution", "08_bed_type.png", False),
]
counts_by_column = {}
for column, title, filename, pie in columns:
    counts_by_column[column] = count_plot(column, title, filename, pie)

# Admission trend
dates = df.dropna(subset=["Admission Date"]).copy()
if not dates.empty:
    daily = dates.groupby(dates["Admission Date"].dt.date).size().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(daily.index, daily.values, marker="o")
    ax.set(title="Hospital admissions over time", xlabel="Admission date", ylabel="Admissions")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUT / "09_admission_trend.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

# Combined dashboard with eight category charts and admission trend
fig, axes = plt.subplots(3, 3, figsize=(17, 13))
fig.suptitle("Hospital Patient Analysis Dashboard", fontsize=18, fontweight="bold")
for ax, (column, title, filename, pie) in zip(axes.flat[:8], columns):
    counts = df[column].fillna("Unknown").value_counts()
    if pie:
        ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90)
        ax.axis("equal")
    else:
        ax.bar(counts.index.astype(str), counts.values)
        ax.set_ylabel("Patients")
        ax.tick_params(axis="x", rotation=25)
    ax.set_title(title)
trend_ax = axes.flat[8]
if not dates.empty:
    daily = dates.groupby(dates["Admission Date"].dt.date).size().sort_index()
    trend_ax.plot(range(len(daily)), daily.values, marker="o")
    trend_ax.set_title("Admissions over time")
    trend_ax.set_ylabel("Admissions")
    trend_ax.set_xticks(range(len(daily)))
    trend_ax.set_xticklabels([str(x) for x in daily.index], rotation=45, ha="right", fontsize=7)
else:
    trend_ax.text(0.5, 0.5, "No valid admission dates", ha="center", va="center")
    trend_ax.set_axis_off()
plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(OUT / "hospital_analysis_dashboard.png", dpi=300, bbox_inches="tight")
plt.close(fig)

def top_value(series):
    return f"{series.idxmax()} ({series.max()} patients)" if not series.empty else "Not available"

findings = [
    "HOSPITAL PATIENT ANALYSIS - KEY FINDINGS",
    f"Total records: {len(df)}",
    f"Unique patients: {df['Patient ID'].nunique()}",
]
for column, _, _, _ in columns:
    findings.append(f"Most common {column}: {top_value(counts_by_column[column])}")
findings += [
    "Waiting-time analysis is not included because the supplied CSV has no waiting-time column."
]
(OUT / "key_findings.txt").write_text("\n".join(findings), encoding="utf-8")
print("\n".join(findings))
print("\nDone! Charts and findings saved in:", OUT)
