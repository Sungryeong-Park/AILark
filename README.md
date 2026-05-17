# AILark

## Overview
AILark is an automated daily briefing system designed exclusively for macOS. It collects the latest artificial intelligence news, trending open-source projects, and research papers, analyzes the raw data using the Gemini 2.5 Flash model, and generates a structured, highly technical Markdown report every morning.

## Features
- Automated Data Collection: Scrapes global AI news, trending GitHub repositories, and arXiv research papers (cs.AI / cs.CL).
- AI-Powered Analysis: Utilizes Gemini 2.5 Flash to filter out non-technical noise, summarize key architectural changes, and provide practical insights for developers.
- Native macOS Automation: Integrates directly with `launchd` to run seamlessly in the background at 08:00 AM, Monday through Friday. If the Mac is asleep, the task executes immediately upon waking.
- Structured Output: Automatically organizes generated Markdown reports into weekly directories for efficient file management.

## Project Structure
```text
AILark/
├── src/
│   ├── main.py
│   ├── github_scraper.py
│   ├── news_scraper.py
│   └── paper_scraper.py
├── scripts/
│   ├── setup.sh
│   └── run_ailark.sh
├── reports/
├── .env
├── .gitignore
└── requirements.txt
```

## Requirements
- macOS (required for launchd automation)
- Python 3.x
- Google Gemini API Key

## Installation
Clone the repository and run the setup script. The setup script will automatically handle the creation of the virtual environment, package installation, .env file generation (via API key input), and launchd registration.

```bash
git clone {Repository URL}
cd AILark
bash scripts/setup.sh
```

## How It Works
1. The macOS launchd daemon triggers `scripts/run_ailark.sh` automatically at 08:00 AM on weekdays.
2. The shell script activates the Python virtual environment and executes `src/main.py`.
3. `main.py` coordinates the execution of the three scrapers to gather raw data from predefined sources.
4. The collected data is compiled and sent to the Gemini API for technical analysis and formatting.
5. The final output is saved as a Markdown file on the local disk.

## Output
Generated reports are saved in the `reports/` directory, organized by weekly subfolders.

File Path Format:
```
reports/{MMDD-MMDD}/YYYY-MM-DD_AILark_Brief.md
```
