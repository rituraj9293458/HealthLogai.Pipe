# Daily Health & Lifestyle Analysis Pipeline (LangGraph)
_________________________________________________________

This project is an automated pipeline, built with LangGraph, that takes a person's daily activity data — steps, screen time, and food intake — and turns it into a single, readable daily health report, delivered as a PDF.

The idea behind it is simple: most of us have this data scattered across different apps (a fitness tracker, a screen time app, a food delivery app), but nobody ever looks at it together. A step count on its own doesn't mean much. Neither does a screen time report. But steps, screen time, and food intake looked at *together*, on the same day, start to tell an actual story — whether someone had a sedentary day fueled by heavy snacking and long social media sessions, or an active day with balanced meals and productive screen use. That's the gap this project is trying to close: correlating everyday behavioral data into something that actually reads like a report a person could reflect on.

## Why this is useful

Health tracking apps are good at showing you numbers, but bad at showing you relationships between numbers. This pipeline is an attempt to build that missing layer — a system that pulls data from multiple sources, understands each one individually, and then reasons across all of them to find patterns a person wouldn't easily see on their own (for example, noticing that low step counts tend to coincide with late-night screen time and heavier snack consumption).

It's also built with cost and speed in mind from the start, since a system like this is meant to run every single day. Running everything through a single large hosted model would get expensive fast, so the architecture deliberately splits the work between local and cloud models (more on that below).

## How the test apps simulate real data

Right now, the pipeline doesn't pull data from real fitness trackers, screen time tools, or food delivery services — because building integrations with those is a separate problem, and I wanted to validate the analysis and reporting logic first. So instead, I built three small local test APIs that mimic what those real integrations would eventually return:

- A steps API (`http://127.0.0.1:8000/steps`) that returns a total step count and a distribution of steps across the day.
- A screen time API (`http://127.0.0.1:8001/screen-time`) that returns total screen time along with a breakdown by application.
- A food orders API (`http://127.0.0.1:8002/food`) that returns a list of food orders tagged by meal period (breakfast, snacks, lunch, dinner).

These test apps stand in for the real data sources. The LangGraph nodes don't know or care that the data is simulated — they just make an HTTP request and process whatever comes back. That's intentional: it means the moment real data sources are wired up, the analysis pipeline itself doesn't need to change at all, only the source of the data does.

## Where this is headed

The test APIs are a stand-in, not the end goal. The plan is to gradually replace each one with a real data source:

- Steps and activity data pulled from an actual fitness tracker or phone sensor API (Google Fit, Apple Health, or a wearable's API).
- Screen time pulled from the device's actual usage tracking (Android's UsageStatsManager, iOS Screen Time API, or a desktop activity tracker).
- Food data pulled either from a real food delivery integration or from a food logging feature built directly into the app, instead of relying on order history.

Once real data sources are in place, the next step is to wrap this whole pipeline into an actual app with a proper interface, rather than something that just runs from the command line and drops a PDF into a folder. The backend logic — the graph, the nodes, the database layer, the report generation — is largely already reusable as-is; what's missing is the front-end and the real data plumbing, along with things like user accounts, scheduling the pipeline to run automatically once a day, and storing historical reports so trends over time become visible, not just single-day snapshots.

## How the LangGraph workflow is structured

The pipeline is a single LangGraph graph with a fan-out, fan-in, then linear structure:

```
                 ┌─────────┐
        ┌───────▶│  steps  │───┐
        │        └─────────┘   │
START ──┼───────▶┌─────────┐   │
        │        │ screen  │───┼──▶ dbsave ──▶ final ──▶ pdf ──▶ END
        │        └─────────┘   │
        └───────▶┌─────────┐   │
                 │  food   │───┘
                 └─────────┘
```

**1. Three parallel data + analysis nodes.** From `START`, the graph branches into three independent nodes that run at the same time: `steps`, `screen`, and `food`. Each one fetches raw data from its respective test API and then runs it through a locally hosted model (via Ollama) to turn raw numbers into a written analysis. For example, the steps node doesn't just report "8,400 steps" — it interprets what the step count and its distribution across the day might reasonably suggest about activity level and sedentary periods.

**2. A database save node.** All three branches feed into a single `dbsave` node, which is where the fan-in happens — LangGraph waits for all three parallel branches to finish before continuing. This node takes the three individual write-ups (steps, screen, food) and saves them as one document into MongoDB, timestamped by date. This also means every day's data is kept as a permanent record, which is what will eventually let the app show trends over time rather than just a single report.

**3. A final synthesis node.** The saved document is pulled back and handed to a single call to a hosted model (Gemini), whose entire job is to look at the three analyses *together* and find the relationships between them — things like whether screen time patterns line up with sedentary stretches, or whether food intake looks proportionate to activity level. This is the step that turns three separate write-ups into one coherent report, and it's deliberately the only point in the whole pipeline that calls a paid, hosted API.

**4. A PDF generation node.** The final report text is formatted and rendered into a clean PDF using ReportLab, with proper headings, section breaks, and bullet formatting, and saved into a local `reports/` folder with a timestamped filename.

## Local models + Gemini: keeping it cheap and fast

The main design decision in this project is *where* each piece of reasoning happens, and it comes down to splitting work between local models and a single hosted model rather than routing everything through one expensive API.

- The three per-domain analyses (steps, screen time, food) each run on a **local model through Ollama** — different small models suited to each task (a lightweight general model for step data, another for screen time interpretation, and a health/food-oriented model for nutrition analysis). These run on the machine itself, so they cost nothing per call and can run in parallel since none of them depend on each other.
- Only the **final synthesis step calls Gemini**, the one hosted API call in the entire pipeline, and only after all the local analyses are already done and condensed. Gemini isn't being asked to process raw data — it's being handed three already-summarized write-ups and asked to find the relationships between them, which is a much smaller and cheaper prompt than if it had to do everything from scratch.

The result is a kind of multilevel distribution: local, parallel, low-cost models handle the first layer of interpretation for each data domain independently and simultaneously, and the cloud model is reserved for the one task it's actually best suited for — synthesizing across domains — while being called exactly once per run. As more data sources get added later (sleep, heart rate, workouts, and so on), this same pattern holds: each new source gets its own local analysis node, and the final Gemini call stays a single call regardless of how many sources feed into it. That's what keeps the system affordable to run daily instead of scaling API costs linearly with every new data type.

## Project structure

```
langgraphai/
├── main.py              # entry point, runs the graph and prints the result
├── state.py              # shared state definition passed between nodes
├── nodesnedges.py         # graph definition: nodes, edges, compilation
├── stepcountnode.py       # fetches step data, analyzes with a local model
├── screentimenode.py      # fetches screen time data, analyzes with a local model
├── foodorder.py           # fetches food order data, analyzes with a local model
├── database.py            # saves the combined daily record to MongoDB
├── finalanalyse.py        # cross-domain synthesis using Gemini
├── pdfnode.py              # renders the final report as a PDF
├── reports/                # generated PDF reports land here
└── requirements.txt
```

## Running it

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Have Ollama running locally with the required models pulled (used for the steps, screen time, and food nodes).
3. Set up a `.env` file with your MongoDB connection string and Gemini API key:
   ```
   MONGO_URI=your_mongo_connection_string
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Start the three test data APIs (steps, screen time, food) on ports 8000, 8001, and 8002.
5. Run the pipeline:
   ```
   python main.py
   ```

The report will print to the console and a PDF version will be saved in the `reports/` folder.

## Current status

This is a working prototype. The graph logic, local/cloud model split, database storage, and PDF generation are all functional end to end, but the data sources are currently simulated test APIs rather than real integrations, and there's no user-facing app yet — just a script you run from the command line. Both of those are the next things being worked on.
