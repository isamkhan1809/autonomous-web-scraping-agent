<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=7c3aed&height=200&section=header&text=Autonomous%20Web%20Scraping%20Agent&fontSize=36&fontColor=ffffff&fontAlignY=38&desc=Natural%20Language%20Goals%20%7C%20Playwright%20%7C%20Claude%20Tool%20Use&descAlignY=55&descSize=16&animation=fadeIn" width="100%" />

<br/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=18&duration=3000&pause=800&color=A855F7&center=true&vCenter=true&multiline=true&repeat=true&width=620&height=100&lines=Autonomous+Web+Scraping+Agent;Claude+Tool+Use+%7C+Playwright+Browser;Natural+Language+%E2%86%92+Multi-Step+Execution;FastAPI+Backend+%7C+React+Step+Visualiser" alt="Typing SVG" />
</a>

<br/><br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61dafb?style=for-the-badge&logo=react&logoColor=black)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude_3.5-7c3aed?style=for-the-badge&logo=anthropic&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-1.48-2ead33?style=for-the-badge&logo=playwright&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-ec4899?style=for-the-badge)

</div>

---

## How It Works

```
  ┌──────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
  │   Goal   │────▶│   Plan   │────▶│  Browse    │────▶│ Extract  │────▶│  Result  │
  │   (NL)    │    │ (Claude) │     │(Playwright)│     │  (LLM)   │     │ (JSON)   │
  └──────────┘     └──────────┘     └────────────┘     └──────────┘     └──────────┘
        │                │                │                │                │
    User types       Claude plans     Headless          Structured       Displayed
    natural lang     & selects        Chromium          extraction       in React
    objective        browser tools    navigates         & summary        timeline
```

The agent runs a **Claude tool-use agentic loop**. At each step:
1. Claude receives the goal + browser state + conversation history
2. Claude selects a browser tool (`navigate`, `search_google`, `get_page_content`, `extract_data`, etc.)
3. The tool executes in a headless Playwright Chromium instance
4. The result is fed back to Claude
5. Repeat until Claude calls `finish` with the final answer

---

## Features

- **Natural Language Interface** — describe what you want to find in plain English
- **Autonomous Multi-Step Planning** — the agent decides which pages to visit and what to extract
- **Google Search Integration** — automatically searches for relevant URLs when needed
- **Step-by-Step Timeline** — every browser action is logged and displayed in the React UI
- **Screenshot Carousel** — captures browser screenshots at key steps for full transparency
- **Configurable Depth** — set max steps (5–20) to control how deep the agent searches
- **Example Goal Chips** — one-click presets to get started immediately
- **Dark Purple Theme** — sleek, developer-focused UI

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium    # Install headless browser
```

Create a `.env` file in the `backend/` directory:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Usage

1. Type a natural language goal into the text area, or click one of the example chips
2. Adjust the **Max Steps** slider (more steps = deeper search, longer runtime)
3. Click **Run Agent** (or press `Cmd/Ctrl + Enter`)
4. Watch the step-by-step execution timeline populate in real time
5. Read the final result in the highlighted result box
6. Browse screenshots from each browser navigation

### Example Goals

| Goal | What the Agent Does |
|------|---------------------|
| `Find the current Bitcoin price on CoinGecko` | Navigates directly to CoinGecko and extracts the BTC price |
| `Get today's top 5 HackerNews stories` | Opens news.ycombinator.com and reads the front page |
| `Find the weather forecast for London this week` | Searches Google Weather and extracts the 7-day forecast |
| `Find the cheapest iPhone 16 on Amazon UK` | Searches Amazon UK and compares listing prices |
| `Get the latest headlines from BBC News` | Navigates BBC News and extracts current top stories |

---

## API Reference

### `POST /run`

Run the scraping agent with a natural language goal.

**Request body:**
```json
{
  "goal": "Find the current Bitcoin price on CoinGecko",
  "max_steps": 10
}
```

**Response:**
```json
{
  "goal": "...",
  "steps": [
    {
      "step_num": 1,
      "tool": "navigate",
      "input": {"url": "https://www.coingecko.com"},
      "output": "...",
      "thought": "..."
    }
  ],
  "result": "Bitcoin is currently trading at $67,432 USD...",
  "success": true,
  "total_steps": 3,
  "screenshots": ["base64..."]
}
```

### `GET /health`

Returns `{"status": "ok"}`.

---

## Project Structure

```
autonomous-web-scraping-agent/
├── backend/
│   ├── main.py              # FastAPI app with /run and /health endpoints
│   ├── agent/
│   │   ├── browser.py       # Playwright BrowserController
│   │   ├── tools.py         # Claude tool schemas (BROWSER_TOOLS)
│   │   └── executor.py      # WebScrapingAgent agentic loop
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx          # Full React UI with timeline + screenshots
│       └── App.css          # Dark purple theme
└── README.md
```

---

## License

MIT

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=7c3aed&height=120&section=footer&animation=fadeIn" width="100%" />
</div>
