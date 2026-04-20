
import os
import sys
import json
import argparse
import textwrap

try:
    import anthropic
except ImportError:
    print("\n[ERROR] 'anthropic' package not found.")
    print("Install it with:  pip install anthropic\n")
    sys.exit(1)


class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    BG_DARK = "\033[40m"


DEMO_RESUME = """
Priya Mehta
Email: priya.m@example.com | LinkedIn: linkedin.com/in/priyamehta

Summary:
Results-driven Software Engineer with 6 years of experience building scalable
backend systems and cloud-native applications. Proven track record in Python,
AWS, and microservices architecture.

Technical Skills:
Languages: Python, JavaScript, TypeScript, SQL, Bash
Frameworks: FastAPI, Django, React, Node.js
Cloud: AWS (EC2, Lambda, S3, RDS, EKS), Docker, Kubernetes
Tools: Git, Jenkins, GitHub Actions, Terraform, Datadog
Databases: PostgreSQL, MongoDB, Redis

Soft Skills: Team leadership, agile collaboration, technical mentoring,
stakeholder communication

Experience:
Senior Software Engineer — FinEdge Technologies (2021–2024, 3 years)
- Led backend migration of payment processing system to microservices
  (Python/FastAPI on AWS EKS)
- Reduced API latency by 40% through query optimization and Redis caching
- Mentored team of 4 junior engineers

Software Engineer — DataStream Inc. (2018–2021, 3 years)
- Built ETL pipelines handling 2M+ records/day using Python and PostgreSQL
- Implemented CI/CD pipelines with Jenkins and GitHub Actions

Education:
B.S. Computer Science — Indian Institute of Technology, Delhi (2018)

Certifications:
- AWS Certified Solutions Architect – Associate (2022)
- Google Cloud Professional Data Engineer (2023)

Projects:
- OpenBanking SDK: Open-source Python library for PSD2 compliant banking
  APIs (800+ GitHub stars)
- SmartLedger: Distributed ledger prototype using Python + Kafka + PostgreSQL
"""

DEMO_JD = """
Senior Software Engineer – FinTech Platform
Company: NovaPay Technologies

About the Role:
We are seeking an experienced Software Engineer to join our backend platform
team building next-generation payment infrastructure.

Required Skills:
- 5+ years of software engineering experience
- Strong proficiency in Python (FastAPI or Django preferred)
- Hands-on experience with AWS services (EC2, Lambda, EKS, S3)
- Containerization: Docker and Kubernetes
- Relational databases: PostgreSQL or MySQL
- Strong communication and collaboration skills
- CI/CD pipeline experience

Preferred Skills:
- TypeScript or Node.js experience
- Familiarity with Redis, Kafka, or other messaging systems
- Open-source contributions
- FinTech or payments domain knowledge

Education:
Bachelor's degree in Computer Science, Engineering, or related field required.
Master's degree preferred.

Job Role: Senior Software Engineer
"""


# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an enterprise AI recruitment assistant. Analyze the provided resume and job description and return ONLY a valid JSON object — no markdown, no preamble, no explanation outside the JSON.

The JSON must include these exact top-level keys:
- candidate_details: { full_name, technical_skills (array), soft_skills (array), years_of_experience, education, certifications (array), projects (array), previous_job_roles (array) }
- extracted_job_requirements: { job_role, required_skills (array), preferred_skills (array), experience_requirement, education_requirement }
- match_score: integer 0–100
- skill_match_analysis: { matched_skills (array), missing_skills (array), partial_matches (array), skill_relevance_notes }
- experience_match_analysis: { required, candidate_has, alignment, notes }
- education_match: { required, candidate_has, match }
- final_decision: one of "Strong Fit", "Moderate Fit", or "Weak Fit"
- justification: 2–4 sentence summary of the overall evaluation
- bias_report: { bias_detected (boolean), reason, evaluation_is_fair (boolean) }

Rules:
1. Evaluate semantically — do not rely purely on keyword matching.
2. Ignore personal attributes: name, gender, age, ethnicity, nationality.
3. If any required info is missing, use "Not Found".
4. Bias report must assess whether evaluation considered only qualifications.
5. Be concise and structured. Return ONLY valid JSON."""


# ─── Display Helpers ─────────────────────────────────────────────────────────

def divider(char="─", width=65):
    print(C.DIM + char * width + C.RESET)

def header(text):
    print()
    print(C.BOLD + C.CYAN + f"  {text}" + C.RESET)
    divider()

def label(key, value, indent=4):
    pad = " " * indent
    key_str  = C.DIM + f"{key}:" + C.RESET
    if isinstance(value, list):
        val_str = ", ".join(value) if value else "None"
    else:
        val_str = str(value) if value else "Not Found"
    # Wrap long values
    wrapped = textwrap.fill(val_str, width=55, subsequent_indent=" " * (indent + len(key) + 2))
    print(f"{pad}{key_str} {C.WHITE}{wrapped}{C.RESET}")

def score_bar(score, width=40):
    filled = int((score / 100) * width)
    empty  = width - filled
    if score >= 75:
        color = C.GREEN
    elif score >= 50:
        color = C.YELLOW
    else:
        color = C.RED
    bar = color + "█" * filled + C.DIM + "░" * empty + C.RESET
    return bar

def chips(items, color):
    if not items:
        return C.DIM + "  none" + C.RESET
    return "  " + "  ".join(f"{color}[{i}]{C.RESET}" for i in items)

def decision_color(decision):
    d = decision.lower()
    if "strong" in d:
        return C.GREEN + C.BOLD + decision + C.RESET
    elif "moderate" in d:
        return C.YELLOW + C.BOLD + decision + C.RESET
    else:
        return C.RED + C.BOLD + decision + C.RESET


# ─── Core Screener ───────────────────────────────────────────────────────────

def analyze(resume_text: str, jd_text: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    user_content = f"RESUME:\n{resume_text.strip()}\n\nJOB DESCRIPTION:\n{jd_text.strip()}"

    print(f"\n  {C.DIM}Sending to Claude API…{C.RESET}")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}]
    )

    raw = "".join(b.text for b in message.content if hasattr(b, "text"))
    clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(clean)


def display_results(data: dict, save_path: str = None):
    score   = data.get("match_score", 0)
    decision = data.get("final_decision", "Unknown")

    # ── Header ──
    print()
    print(C.BOLD + C.BG_DARK + C.WHITE +
          "  ╔══════════════════════════════════════════════╗  " + C.RESET)
    print(C.BOLD + C.BG_DARK + C.WHITE +
          "  ║      AI RECRUITMENT SCREENER — RESULTS       ║  " + C.RESET)
    print(C.BOLD + C.BG_DARK + C.WHITE +
          "  ╚══════════════════════════════════════════════╝  " + C.RESET)

    # ── Score ──
    header("Match Score")
    bar = score_bar(score)
    score_color = C.GREEN if score >= 75 else (C.YELLOW if score >= 50 else C.RED)
    print(f"    {bar}  {score_color}{C.BOLD}{score}/100{C.RESET}")
    print()
    print(f"    Final Decision:  {decision_color(decision)}")

    # ── Bias Report ──
    bias = data.get("bias_report", {})
    detected = bias.get("bias_detected", False)
    fair     = bias.get("evaluation_is_fair", True)
    reason   = bias.get("reason", "—")
    header("Bias Report")
    if detected:
        print(f"    {C.YELLOW}⚠  Bias possibly detected{C.RESET}")
    else:
        print(f"    {C.GREEN}✓  No bias detected — evaluation is fair{C.RESET}")
    print(f"    {C.DIM}Fair:{C.RESET} {C.WHITE}{fair}{C.RESET}")
    print(f"    {C.DIM}Reason:{C.RESET} {C.WHITE}{reason}{C.RESET}")

    # ── Candidate Profile ──
    c = data.get("candidate_details", {})
    header("Candidate Profile")
    label("Name",           c.get("full_name"))
    label("Experience",     c.get("years_of_experience"))
    label("Education",      c.get("education"))
    label("Technical skills", c.get("technical_skills", []))
    label("Soft skills",    c.get("soft_skills", []))
    label("Certifications", c.get("certifications", []))
    label("Previous roles", c.get("previous_job_roles", []))
    label("Projects",       c.get("projects", []))

    # ── Job Requirements ──
    j = data.get("extracted_job_requirements", {})
    header("Extracted Job Requirements")
    label("Job role",         j.get("job_role"))
    label("Required skills",  j.get("required_skills", []))
    label("Preferred skills", j.get("preferred_skills", []))
    label("Experience req.",  j.get("experience_requirement"))
    label("Education req.",   j.get("education_requirement"))

    # ── Skill Match ──
    sm = data.get("skill_match_analysis", {})
    header("Skill Match Analysis")
    print(f"  {C.BOLD}Matched:{C.RESET}")
    print(chips(sm.get("matched_skills", []), C.GREEN))
    print(f"  {C.BOLD}Missing:{C.RESET}")
    print(chips(sm.get("missing_skills", []), C.RED))
    print(f"  {C.BOLD}Partial:{C.RESET}")
    print(chips(sm.get("partial_matches", []), C.YELLOW))
    if sm.get("skill_relevance_notes"):
        print()
        wrapped = textwrap.fill(sm["skill_relevance_notes"], width=60,
                                initial_indent="    ", subsequent_indent="    ")
        print(C.DIM + wrapped + C.RESET)

    # ── Experience ──
    exp = data.get("experience_match_analysis", {})
    header("Experience Alignment")
    label("Required",      exp.get("required"))
    label("Candidate has", exp.get("candidate_has"))
    label("Alignment",     exp.get("alignment"))
    label("Notes",         exp.get("notes"))

    # ── Education ──
    edu = data.get("education_match", {})
    header("Education Match")
    label("Required",      edu.get("required"))
    label("Candidate has", edu.get("candidate_has"))
    label("Match",         edu.get("match"))

    # ── Justification ──
    header("Justification")
    justification = data.get("justification", "No justification provided.")
    wrapped = textwrap.fill(justification, width=60,
                            initial_indent="    ", subsequent_indent="    ")
    print(C.WHITE + wrapped + C.RESET)

    divider("═")
    print()

    # ── Save JSON ──
    if save_path:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  {C.GREEN}✓ JSON output saved to:{C.RESET} {save_path}\n")


# ─── Input Helpers ────────────────────────────────────────────────────────────

def multiline_input(prompt: str) -> str:
    print(f"\n{C.CYAN}{prompt}{C.RESET}")
    print(C.DIM + "  (Paste your text, then press Enter twice to finish)\n" + C.RESET)
    lines = []
    blank_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)
    return "\n".join(lines).strip()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Recruitment Screener — Terminal Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python recruitment_screener.py
              python recruitment_screener.py --demo
              python recruitment_screener.py --resume resume.txt --job job.txt
              python recruitment_screener.py --resume resume.txt --job job.txt --output result.json
        """)
    )
    parser.add_argument("--resume", help="Path to resume text file")
    parser.add_argument("--job",    help="Path to job description text file")
    parser.add_argument("--output", help="Save JSON result to this file path")
    parser.add_argument("--demo",   action="store_true", help="Run with built-in demo data")
    parser.add_argument("--key",    help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    args = parser.parse_args()

    # ── Banner ──
    print()
    print(C.BOLD + C.MAGENTA + "  ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██╗████████╗" + C.RESET)
    print(C.BOLD + C.CYAN    + "  ██╔══██╗██╔════╝██╔════╝██╔══██╗██║   ██║██║╚══██╔══╝" + C.RESET)
    print(C.BOLD + C.BLUE    + "  ██████╔╝█████╗  ██║     ██████╔╝██║   ██║██║   ██║   " + C.RESET)
    print(C.BOLD + C.CYAN    + "  ██╔══██╗██╔══╝  ██║     ██╔══██╗██║   ██║██║   ██║   " + C.RESET)
    print(C.BOLD + C.MAGENTA + "  ██║  ██║███████╗╚██████╗██║  ██║╚██████╔╝██║   ██║   " + C.RESET)
    print(C.DIM              + "  AI Recruitment Screener  |  Powered by Claude API      " + C.RESET)
    divider("═")

    # ── API Key ──
    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print()
        print(f"  {C.YELLOW}No API key found.{C.RESET}")
        print(f"  Set it via:  {C.DIM}export ANTHROPIC_API_KEY=your_key{C.RESET}")
        print(f"  Or enter it now:")
        api_key = input("  API Key: ").strip()
        if not api_key:
            print(f"\n  {C.RED}Error: API key is required.{C.RESET}\n")
            sys.exit(1)

    # ── Load Input ──
    if args.demo:
        print(f"\n  {C.GREEN}Running with demo data…{C.RESET}")
        resume_text = DEMO_RESUME
        jd_text     = DEMO_JD
    else:
        if args.resume:
            with open(args.resume, "r") as f:
                resume_text = f.read()
            print(f"\n  {C.GREEN}✓ Resume loaded from:{C.RESET} {args.resume}")
        else:
            resume_text = multiline_input("  Paste RESUME text below:")

        if args.job:
            with open(args.job, "r") as f:
                jd_text = f.read()
            print(f"  {C.GREEN}✓ Job description loaded from:{C.RESET} {args.job}")
        else:
            jd_text = multiline_input("  Paste JOB DESCRIPTION text below:")

    if not resume_text.strip() or not jd_text.strip():
        print(f"\n  {C.RED}Error: Resume and job description cannot be empty.{C.RESET}\n")
        sys.exit(1)

    # ── Analyze ──
    try:
        result = analyze(resume_text, jd_text, api_key)
    except json.JSONDecodeError as e:
        print(f"\n  {C.RED}Error: Could not parse API response as JSON.{C.RESET}")
        print(f"  {C.DIM}{e}{C.RESET}\n")
        sys.exit(1)
    except anthropic.AuthenticationError:
        print(f"\n  {C.RED}Error: Invalid API key.{C.RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  {C.RED}Error: {e}{C.RESET}\n")
        sys.exit(1)

    # ── Display ──
    display_results(result, save_path=args.output)


if __name__ == "__main__":
    main()