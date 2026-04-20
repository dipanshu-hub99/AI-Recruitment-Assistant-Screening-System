# 🤖 AI Recruitment Screener

> Enterprise-grade resume screening powered by Claude AI — runs entirely in your terminal.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Your API Key](#getting-your-api-key)
- [Usage](#usage)
- [Output Explained](#output-explained)
- [Example Output](#example-output)
- [Troubleshooting](#troubleshooting)
- [Cost](#cost)

---

## Overview

AI Recruitment Screener is a Python terminal application that uses the **Anthropic Claude API** to semantically analyze resumes against job descriptions. It goes beyond simple keyword matching — it understands context, evaluates relevance, detects bias, and produces a structured JSON report with a match score and hiring recommendation.

---

## Features

- ✅ Semantic matching — not just keyword search
- ✅ Extracts structured candidate profile automatically
- ✅ Identifies required vs preferred skills from job descriptions
- ✅ Generates match score (0–100) with justification
- ✅ Final decision: Strong Fit / Moderate Fit / Weak Fit
- ✅ Built-in bias detection report
- ✅ Color-coded terminal output
- ✅ Saves full results as JSON file
- ✅ Supports file input or manual paste
- ✅ Built-in demo mode for quick testing

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8 or higher |
| anthropic | latest |
| Anthropic API Key | required |
| Anthropic Credits | min $5 |

---

## Installation

**Step 1 — Download the script**

Save `recruitment_screener.py` to a folder on your computer, for example:
```
C:\Users\yourname\Desktop\MD\
```

**Step 2 — Install the dependency**

Open PowerShell and run:
```powershell
py -m pip install anthropic
```

**Step 3 — Fix deprecated model (run once)**
```powershell
(Get-Content recruitment_screener.py) -replace 'claude-sonnet-4-20250514', 'claude-sonnet-4-5' | Set-Content recruitment_screener.py
```

---

## Getting Your API Key

1. Go to → [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Click **Manage** → **API Keys**
4. Click **"Create Key"** and copy it immediately
5. Go to **Manage** → **Billing** and add at least **$5 credits**

> ⚠️ Never share your API key publicly or paste it in chat.

---

## Usage

### Set your API key (every new PowerShell session)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
```

### Navigate to the script folder

```powershell
cd "C:\Users\yourname\Desktop\MD"
```

### Run modes

#### 1. Demo mode — quickest way to test
```powershell
python recruitment_screener.py --demo
```

#### 2. Interactive mode — paste resume and JD manually
```powershell
python recruitment_screener.py
```
- Paste your resume text → press **Enter twice**
- Paste job description → press **Enter twice**
- Wait a few seconds for results

#### 3. File mode — point to .txt files
```powershell
python recruitment_screener.py --resume resume.txt --job job.txt
```

#### 4. Save output as JSON
```powershell
python recruitment_screener.py --resume resume.txt --job job.txt --output result.json
```

#### 5. Pass API key directly (without environment variable)
```powershell
python recruitment_screener.py --demo --key sk-ant-api03-your-key-here
```

### All available flags

| Flag | Description |
|------|-------------|
| `--demo` | Run with built-in sample data |
| `--resume` | Path to resume `.txt` file |
| `--job` | Path to job description `.txt` file |
| `--output` | Save JSON result to this file path |
| `--key` | Pass API key directly |

---

## Output Explained

### Match Score
A number from **0 to 100** indicating how well the candidate fits the role.

| Score | Meaning |
|-------|---------|
| 75–100 | Strong Fit ✅ |
| 50–74 | Moderate Fit ⚠️ |
| 0–49 | Weak Fit ❌ |

### Sections in the output

| Section | What it shows |
|---------|--------------|
| **Match Score** | 0–100 score with visual bar |
| **Final Decision** | Strong / Moderate / Weak Fit |
| **Bias Report** | Whether evaluation was fair |
| **Candidate Profile** | Name, skills, experience, education, certifications |
| **Job Requirements** | Extracted required & preferred skills |
| **Skill Match** | Matched ✅, Missing ❌, Partial ⚠️ skills |
| **Experience Alignment** | Required vs candidate experience |
| **Education Match** | Degree requirement vs candidate education |
| **Justification** | 2–4 sentence plain-English summary |
| **Raw JSON** | Full structured output (if saved with `--output`) |

### JSON output structure

```json
{
  "candidate_details": {
    "full_name": "...",
    "technical_skills": [],
    "soft_skills": [],
    "years_of_experience": "...",
    "education": "...",
    "certifications": [],
    "projects": [],
    "previous_job_roles": []
  },
  "extracted_job_requirements": {
    "job_role": "...",
    "required_skills": [],
    "preferred_skills": [],
    "experience_requirement": "...",
    "education_requirement": "..."
  },
  "match_score": 85,
  "skill_match_analysis": {
    "matched_skills": [],
    "missing_skills": [],
    "partial_matches": [],
    "skill_relevance_notes": "..."
  },
  "experience_match_analysis": {
    "required": "...",
    "candidate_has": "...",
    "alignment": "...",
    "notes": "..."
  },
  "education_match": {
    "required": "...",
    "candidate_has": "...",
    "match": "..."
  },
  "final_decision": "Strong Fit",
  "justification": "...",
  "bias_report": {
    "bias_detected": false,
    "reason": "...",
    "evaluation_is_fair": true
  }
}
```

---

## Example Output

```
  ╔══════════════════════════════════════════════╗
  ║      AI RECRUITMENT SCREENER — RESULTS       ║
  ╚══════════════════════════════════════════════╝

  Match Score
  ────────────────────────────────────────────────
  ████████████████████████████████░░░░░░░░  82/100
  Final Decision:  Strong Fit

  Bias Report
  ────────────────────────────────────────────────
  ✓  No bias detected — evaluation is fair

  Skill Match Analysis
  ────────────────────────────────────────────────
  Matched:  [Python]  [AWS]  [Docker]  [PostgreSQL]
  Missing:  [Kubernetes]  [CI/CD]
  Partial:  [FastAPI]
```

---

## Troubleshooting

### ❌ `CommandNotFoundException` when running python
**Fix:** Use `py` instead of `python`:
```powershell
py recruitment_screener.py --demo
```

### ❌ `credit balance is too low`
**Fix:** Add credits at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)

### ❌ `AuthenticationError` — invalid API key
**Fix:** Re-set your key:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-your-correct-key"
```

### ❌ `DeprecationWarning` about model name
**Fix:** Run this once to update the model:
```powershell
(Get-Content recruitment_screener.py) -replace 'claude-sonnet-4-20250514', 'claude-sonnet-4-5' | Set-Content recruitment_screener.py
```

### ❌ `ModuleNotFoundError: No module named 'anthropic'`
**Fix:**
```powershell
py -m pip install anthropic
```

---

## Cost

Each resume analysis costs approximately **$0.01 or less**.

| Credits | Approximate analyses |
|---------|---------------------|
| $1 | ~100 analyses |
| $5 | ~500 analyses |
| $10 | ~1000 analyses |

---

## Built With

- [Python 3.8+](https://python.org)
- [Anthropic Claude API](https://docs.anthropic.com)
- [anthropic Python SDK](https://github.com/anthropic/anthropic-sdk-python)

---

## License

For personal and educational use.
