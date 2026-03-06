---
name: langfuse-fetcher
description: Fetch and index Langfuse trace data for analysis. Use when needing to pull all traces to build a local index, fetch specific session/case traces for QA review, or search the local trace index for sessions matching criteria.
---

# Langfuse Trace Fetcher

Fetches Langfuse trace data via `langfuse-cli` and builds a local searchable index.

## Prerequisites

- Node.js (for `npx langfuse-cli`)
- Python 3
- Langfuse API credentials as environment variables:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

If credentials are not set, ask the user for them.

## Workflow

### 1. Build Full Trace Index

Fetches all trace metadata (core + metrics) via paginated API calls and builds a local JSON index.

```bash
python3 scripts/fetch-traces.py --output-dir <dir>
```

Output structure:
```
<dir>/
├── pages/           # Raw paginated API responses
│   ├── page-1.json
│   └── ...
└── trace-index.json # Consolidated index with key fields per trace
```

Index entry fields: `id`, `name`, `timestamp`, `environment`, `userId`, `sessionId`, `tags`, `bookmarked`, `latency`, `totalCost`, `htmlPath`

The script prints summary stats on completion (environment distribution, unique sessions/users, latency stats).

Options:
- `--output-dir` (required): Directory to store pages and index
- `--workers N`: Parallel fetch threads (default: 5)
- `--limit N`: Traces per page (default: 100)

### 2. Fetch Case Traces

Fetches all traces for a specific conversation/case by session ID or conversation ID, including full trace details (input/output/observations).

```bash
python3 scripts/fetch-case.py --conversation-id <id> --output-dir <dir>
```

This will:
1. Look up all traces matching `pexo:<conversation_id>` in the local index (or query the API directly)
2. Fetch each trace's full details via `langfuse-cli api traces get`
3. Save to `<dir>/cases/<conversation_id>/trace-N-<short_id>.json`

Options:
- `--conversation-id` (required): The conversation ID (e.g., `10037737676`)
- `--output-dir` (required): Base data directory (must contain `trace-index.json` or will query API)
- `--session-id`: Use a full session ID instead of conversation ID

### 3. Search the Index

The index at `trace-index.json` can be searched with standard tools:

```bash
# Find all traces for a conversation
python3 -c "
import json
with open('<dir>/trace-index.json') as f:
    idx = json.load(f)
matches = [t for t in idx['traces'] if '<conv_id>' in (t.get('name') or '')]
for t in matches:
    print(f\"{t['timestamp']}  {t['id'][:12]}  {t['name']}  latency={t.get('latency','?')}s\")
"
```

## Typical QA Analysis Workflow

1. Run `fetch-traces.py` to build/refresh the full index
2. Identify interesting sessions from the index (by name pattern, high latency, bookmarked, etc.)
3. Run `fetch-case.py` for each session to get full trace details
4. Analyze the traces — review input/output, tool calls, timing, and write QA reports
