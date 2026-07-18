import urllib.request
import urllib.parse
import json
import re
import os

CV_DATA_URL = "https://raw.githubusercontent.com/iabdul-aal/iabdul-aal.github.io/main/cv_data.json"
PUBLICATIONS_URL = "https://raw.githubusercontent.com/iabdul-aal/iabdul-aal.github.io/main/publications.json"
ACADEMIC_CONTENT_URL = "https://raw.githubusercontent.com/iabdul-aal/iabdul-aal.github.io/main/lib/academic-content.ts"
GITHUB_USERNAME = "iabdul-aal"

# Repos to always exclude from the featured section
EXCLUDED_REPOS = {"iabdul-aal", "iabdul_aal_bot", "iabdul-aal.github.io"}

# Hardcoded fallback repo list used when the API is unavailable
FALLBACK_REPOS = [
    {
        "name": "PD-design-kit",
        "html_url": "https://github.com/iabdul-aal/PD-design-kit",
        "description": None,
        "stargazers_count": 0,
        "forks_count": 0,
        "updated_at": "2026-01-01",
    }
]


def fetch_raw_text(url, token=None):
    try:
        headers = {"User-Agent": "readme-updater/1.0"}
        if token:
            headers["Authorization"] = f"token {token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"  Warning: could not fetch {url}: {e}")
        return None


def fetch_json(url, token=None):
    text = fetch_raw_text(url, token)
    if text:
        try:
            return json.loads(text)
        except Exception as e:
            print(f"  Warning: could not parse JSON from {url}: {e}")
    return None


def format_authors(authors_list):
    """Format an author list with Oxford comma and 'and' connective."""
    if not authors_list:
        return ""
    if len(authors_list) == 1:
        return authors_list[0]
    if len(authors_list) == 2:
        return f"{authors_list[0]} and {authors_list[1]}"
    return ", ".join(authors_list[:-1]) + ", and " + authors_list[-1]


def sanitize(text):
    """Enforce writing-style rules: no em-dash, no bare ampersand."""
    if not text:
        return text
    return text.replace("\u2014", ", ").replace("&", "and")


def parse_research_themes(ts_text):
    """Dynamically parse researchThemes array from academic-content.ts."""
    if not ts_text:
        return []
    match = re.search(r'export const researchThemes\s*=\s*\[(.*?)\]\s*as const', ts_text, re.DOTALL)
    if not match:
        return []
    
    array_content = match.group(1)
    objects = re.findall(r'\{(.*?)\}', array_content, re.DOTALL)
    
    themes = []
    for obj in objects:
        title_m = re.search(r'title:\s*"(.*?)"', obj)
        # Match multiline problem value inside quotes
        problem_m = re.search(r'problem:\s*\n?\s*"(.*?)"', obj, re.DOTALL)
        
        if title_m and problem_m:
            title = title_m.group(1).strip()
            problem = problem_m.group(1)
            problem = re.sub(r'\s+', ' ', problem).strip()
            themes.append((title, problem))
            
    return themes


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        print("GitHub token found — using authenticated API calls.")
    else:
        print("No GitHub token — using unauthenticated API (rate-limited).")

    print("Fetching CV data...")
    cv_data = fetch_json(CV_DATA_URL)
    if not cv_data:
        print("Fatal: could not load cv_data.json. Aborting.")
        return

    print("Fetching publications...")
    pubs = fetch_json(PUBLICATIONS_URL) or []

    print("Fetching academic content configurations (for research themes)...")
    academic_ts = fetch_raw_text(ACADEMIC_CONTENT_URL)
    themes = parse_research_themes(academic_ts)

    print("Fetching GitHub repositories...")
    repos_raw = fetch_json(
        f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&type=public",
        token=token,
    )

    if repos_raw:
        repos = [r for r in repos_raw if r.get("name", "").lower() not in EXCLUDED_REPOS]
    else:
        repos = []

    if not repos:
        print("  API returned no usable repos — using hardcoded fallback list.")
        repos = FALLBACK_REPOS

    repos.sort(
        key=lambda r: (r.get("stargazers_count", 0), r.get("updated_at", "")),
        reverse=True,
    )

    # ── Contact fields ────────────────────────────────────────────────────────
    p_info = cv_data.get("personalInfo", {})
    email   = p_info.get("email",   "contact@iabdul-aal.me")
    orcid   = p_info.get("orcid",   "0009-0004-9300-3936")
    linkedin = p_info.get("linkedin", "iabdul-aal")

    enc_email    = urllib.parse.quote(email)
    enc_linkedin = urllib.parse.quote(linkedin)
    enc_orcid    = urllib.parse.quote(orcid)

    # ── Research Focus ────────────────────────────────────────────────────────
    if themes:
        print(f"Dynamically parsed {len(themes)} research themes from website.")
        focus_lines = []
        for t, p in themes:
            focus_lines.append(f"* **{sanitize(t)}**: {sanitize(p)}")
        research_focus_md = "\n".join(focus_lines)
    else:
        print("Warning: Falling back to default research themes.")
        research_focus_md = (
            "* **Integrated Nanophotonics**: Wave interactions in reconfigurable photonic "
            "crystal cavities and bound-states-in-the-continuum (BIC) structures on "
            "emerging material platforms.\n"
            "* **Quantum Photonics**: Waveguide-based nonlinear photon-pair sources, "
            "coherent phase-shifter networks, and nanophotonic routing circuits.\n"
            "* **Intelligent Photonics**: Accelerating waveguide design by bridging wave "
            "equations with deep learning and optimization methods, while developing "
            "all-optical neuromorphic processing hardware."
        )

    # ── Technical Skills ──────────────────────────────────────────────────────
    skills_md = ""
    for skill in cv_data.get("technicalSkills", []):
        cat = sanitize(skill.get("category", ""))
        items = sanitize(skill.get("items", ""))
        
        if "simulation" in cat.lower() or "design" in cat.lower():
            badge_list = []
            for item in items.split(","):
                item_clean = item.strip().title()
                # Clean up specific terms
                if "Fdtd/Fem" in item_clean:
                    item_clean = "FDTD / FEM Solvers"
                elif "Drift-Diffusion" in item_clean:
                    item_clean = "Drift-Diffusion Transport"
                elif "Coupled-Mode" in item_clean:
                    item_clean = "Coupled-Mode Theory"
                elif "Transfer-Matrix" in item_clean:
                    item_clean = "Transfer-Matrix Method"
                elif "Waveguide Dispersion" in item_clean:
                    item_clean = "Waveguide Dispersion"
                
                item_clean = item_clean.rstrip(".")
                encoded = urllib.parse.quote(item_clean.replace("-", "--"))
                badge_list.append(f'<img src="https://img.shields.io/badge/{encoded}-0A1723?style=flat-square" alt="{item_clean}" />')
            
            skills_md += "<strong>Simulation and Design:</strong><br/>\n"
            skills_md += '<p align="left">\n'
            skills_md += "\n".join(f"  {b}" for b in badge_list) + "\n"
            skills_md += "</p>\n\n"
            
        elif "programming" in cat.lower():
            skills_md += "<strong>Programming and Tools:</strong><br/>\n"
            skills_md += (
                '<p align="left">\n'
                '  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />\n'
                '  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch" />\n'
                '  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white" alt="TensorFlow" />\n'
                '  <img src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white" alt="NumPy" />\n'
                '  <img src="https://img.shields.io/badge/SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white" alt="SciPy" />\n'
                '  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat-square" alt="Matplotlib" />\n'
                '  <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white" alt="Git" />\n'
                '  <img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black" alt="Linux" />\n'
                '  <img src="https://img.shields.io/badge/LaTeX-008080?style=flat-square&logo=latex&logoColor=white" alt="LaTeX" />\n'
                '</p>'
            )

    # ── Publications ──────────────────────────────────────────────────────────
    pub_lines = []
    for pub in pubs:
        title       = sanitize(pub.get("title", ""))
        venue       = sanitize(pub.get("venue", ""))
        year        = pub.get("year", "")
        url         = pub.get("url", "")
        authors_str = sanitize(format_authors(pub.get("authors", [])))
        arxiv       = pub.get("arxiv")
        doi         = pub.get("doi")

        if arxiv:
            link = f"[arXiv:{arxiv}]({url})"
        elif doi:
            link = f"[DOI: {doi}]({url})"
        else:
            link = f"[Link]({url})"

        pub_lines.append(
            f"* **{title}**\n"
            f"  *{authors_str}*\n"
            f"  *{venue}* ({year}) | {link}"
        )
    pubs_md = "\n\n".join(pub_lines) if pub_lines else "*No publications listed.*"

    # ── Research Software ─────────────────────────────────────────────────────
    repo_blocks = []
    tools_by_repo = {}
    for tool in cv_data.get("tools", []):
        for lnk in tool.get("links", []):
            href = lnk.get("href", "").rstrip("/").lower()
            tools_by_repo[href] = tool

    for repo in repos:
        repo_url = repo.get("html_url", "")
        matched  = tools_by_repo.get(repo_url.rstrip("/").lower())

        if matched:
            title   = sanitize(matched.get("title") or repo["name"])
            desc    = sanitize(matched.get("objective") or repo.get("description") or "")
            methods = sanitize(matched.get("methods", ""))
            doi_url = next(
                (l["href"] for l in matched.get("links", [])
                 if "doi" in l.get("href", "").lower()),
                None,
            )
        else:
            title   = sanitize(repo["name"].replace("-", " ").replace("_", " ").title())
            desc    = sanitize(repo.get("description") or "")
            methods = ""
            doi_url = None

        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        # Type badges derived from content keywords
        badges = []
        search = f"{repo.get('name','')} {repo.get('description','')} {methods}".lower()
        if "pinn" in search or "physics-informed" in search:
            badges.append(
                '<img src="https://img.shields.io/badge/Physics--Informed-PINN-B68C61?style=flat-square" alt="PINN" />'
            )
        if "simulation" in search or "fdtd" in search or "pipeline" in search:
            badges.append(
                '<img src="https://img.shields.io/badge/Simulation-Pipeline-0A1723?style=flat-square" alt="Simulation Pipeline" />'
            )

        block = f"### [{title}]({repo_url})\n"
        if desc:
            block += f"> {desc}\n\n"
        if methods:
            block += f"**Methods:** {methods}\n\n"

        badge_parts = [
            f'<a href="{repo_url}"><img src="https://img.shields.io/badge/Repository-GitHub-B68C61?style=flat-square&logo=github" alt="Repository" /></a>'
        ]
        if doi_url:
            doi_suffix = doi_url.split("doi.org/")[-1]
            enc_doi = urllib.parse.quote(doi_suffix, safe="")
            badge_parts.append(
                f'<a href="{doi_url}"><img src="https://img.shields.io/static/v1?label=DOI&message={enc_doi}&color=0A1723&style=flat-square" alt="DOI" /></a>'
            )
        badge_parts.extend(badges)

        block += "<p>\n"
        block += "\n".join(f"  {b}" for b in badge_parts) + "\n"
        if stars > 0 or forks > 0:
            metrics = " | ".join(filter(None, [
                f"\u2b50 {stars}" if stars else "",
                f"\U0001f374 {forks}" if forks else "",
            ]))
            block += f"  <br/><small>{metrics}</small>\n"
        block += "</p>"

        repo_blocks.append(block)

    repos_md = "\n\n".join(repo_blocks) if repo_blocks else "*No public repositories listed.*"

    # ── Assemble README ───────────────────────────────────────────────────────
    readme = f"""\
<div align="center">
  <img src="https://readme-typing-svg.demolab.com/?font=Fira+Code&duration=3800&pause=900&color=B68C61&width=820&lines=Integrated+Photonics+Research;Physics-Informed+Neural+Networks+(PINNs);Simulation+Pipelines+and+Adjoint+Optimization;Nonlinear+and+Quantum+Photonics&center=true" alt="Research interests" />
</div>

<div align="center">

[![Website](https://img.shields.io/static/v1?label=Website&message=iabdul-aal.me&color=B68C61&style=flat-square&logo=googlechrome&logoColor=CDCDCD&labelColor=0A1723)](https://iabdul-aal.me)&ensp;[![CV](https://img.shields.io/static/v1?label=CV&message=cv.pdf&color=B68C61&style=flat-square&logo=adobeacrobatreader&logoColor=CDCDCD&labelColor=0A1723)](https://iabdul-aal.me/cv.pdf)&ensp;[![Email](https://img.shields.io/static/v1?label=Email&message={enc_email}&color=B68C61&style=flat-square&logo=gmail&logoColor=CDCDCD&labelColor=0A1723)](mailto:{email})&ensp;[![LinkedIn](https://img.shields.io/static/v1?label=LinkedIn&message={enc_linkedin}&color=B68C61&style=flat-square&logo=linkedin&logoColor=CDCDCD&labelColor=0A1723)](https://linkedin.com/in/{linkedin})&ensp;[![ORCID](https://img.shields.io/static/v1?label=ORCID&message={enc_orcid}&color=B68C61&style=flat-square&logo=orcid&logoColor=CDCDCD&labelColor=0A1723)](https://orcid.org/{orcid})

</div>

<div align="center">
  <img src="https://komarev.com/ghpvc/?username={GITHUB_USERNAME}&color=B68C61&style=flat-square&label=PROFILE+VIEWS" alt="Profile Views" />
</div>

---

## \U0001f52c Research Focus

{research_focus_md}

---

## \U0001f6e0\ufe0f Technical Skills

{skills_md}

---

## \U0001f4c4 Publications

{pubs_md}

---

## \U0001f4bb Research Software

{repos_md}

---

## \U0001f4ca GitHub Activity

<div align="center">
  <img width="49%" src="https://github-readme-stats.anuraghazra1.vercel.app/api?username={GITHUB_USERNAME}&show_icons=true&title_color=B68C61&icon_color=B68C61&text_color=CDCDCD&bg_color=0A1723&hide_border=true&rank_icon=github" alt="GitHub Stats" />
  <img width="49%" src="https://streak-stats.demolab.com?user={GITHUB_USERNAME}&currStreakNum=B68C61&sideNums=B68C61&sideLabels=CDCDCD&dates=CDCDCD&ring=B68C61&fire=B68C61&background=0A1723&stroke=0A1723&hide_border=true" alt="Contribution Streak" />
</div>
<div align="center">
  <img width="98%" src="https://github-readme-activity-graph.vercel.app/graph?username={GITHUB_USERNAME}&bg_color=0A1723&color=B68C61&line=B68C61&point=CDCDCD&area=true&hide_border=true&custom_title=Contribution+Activity" alt="Contribution Activity Graph" />
</div>

---

## \u2709\ufe0f Collaboration

Open to research collaborations and invited technical talks in integrated, nonlinear, and computational photonics. Reach out via [email](mailto:{email}).
"""

    print("Writing README.md ...")
    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)
    print("Done.")


if __name__ == "__main__":
    main()
