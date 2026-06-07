import os
import re
import requests

GITHUB_USERNAME = "iampryce"
FEATURED_TOPIC = "portfolio"

CATEGORY_TOPICS = {
    "cloud-security": "Cloud Security & DevSecOps",
    "devsecops": "Cloud Security & DevSecOps",
    "security": "Cloud Security & DevSecOps",
    "platform-engineering": "Platform Engineering & Automation",
    "devops": "Platform Engineering & Automation",
    "infrastructure": "Platform Engineering & Automation",
    "automation": "Platform Engineering & Automation",
    "terraform": "Platform Engineering & Automation",
    "kubernetes": "Platform Engineering & Automation",
    "ai": "AI & Cloud Applications",
    "machine-learning": "AI & Cloud Applications",
    "serverless": "AI & Cloud Applications",
    "generative-ai": "AI & Cloud Applications",
}

CATEGORY_ORDER = [
    "Cloud Security & DevSecOps",
    "Platform Engineering & Automation",
    "AI & Cloud Applications",
    "Other Projects",
]


def get_featured_repos():
    url = f"https://api.github.com/search/repositories?q=user:{GITHUB_USERNAME}+topic:{FEATURED_TOPIC}&sort=updated&per_page=30"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["items"]


def categorize(repo):
    topics = repo.get("topics", [])
    for topic in topics:
        if topic in CATEGORY_TOPICS:
            return CATEGORY_TOPICS[topic]
    return "Other Projects"


def build_section(repos):
    categories = {cat: [] for cat in CATEGORY_ORDER}
    for repo in repos:
        categories[categorize(repo)].append(repo)

    lines = ["\n"]
    for cat in CATEGORY_ORDER:
        cat_repos = categories[cat]
        if not cat_repos:
            continue
        lines.append(f"### {cat}\n\n")
        lines.append('<p align="left">\n')
        for i, repo in enumerate(cat_repos):
            lines.append(f'<a href="{repo["html_url"]}">\n')
            lines.append(
                f'  <img src="https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USERNAME}&repo={repo["name"]}" width="49%" />\n'
            )
            lines.append("</a>\n")
            if i % 2 == 1:
                lines.append("\n")
        lines.append("</p>\n\n---\n\n")

    return "".join(lines)


def update_readme(section_content):
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!--START_SECTION:projects-->.*?<!--END_SECTION:projects-->"
    replacement = f"<!--START_SECTION:projects-->{section_content}<!--END_SECTION:projects-->"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    repos = get_featured_repos()
    print(f"Found {len(repos)} repos with topic '{FEATURED_TOPIC}'")
    section = build_section(repos)
    update_readme(section)
    print("README updated successfully")
