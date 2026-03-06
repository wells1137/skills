#!/usr/bin/env python3
"""Fetch all Langfuse trace metadata (core+metrics) and build a local index.

Requires env vars: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
"""

import argparse
import subprocess
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def check_credentials():
    missing = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST") if not os.environ.get(k)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def fetch_page(page: int, limit: int) -> dict:
    result = subprocess.run(
        [
            "npx", "langfuse-cli", "api", "traces", "list",
            "--fields", "core,metrics",
            "--limit", str(limit),
            "--page", str(page),
            "--order-by", "timestamp.desc",
            "--json",
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr.strip()}")
    return json.loads(result.stdout)


def save_page(pages_dir: str, page: int, data: dict):
    os.makedirs(pages_dir, exist_ok=True)
    with open(os.path.join(pages_dir, f"page-{page}.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False)


def build_index(pages_dir: str, total_pages: int, index_path: str):
    all_traces = []
    for p in range(1, total_pages + 1):
        path = os.path.join(pages_dir, f"page-{p}.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for t in data.get("body", {}).get("data", []):
            all_traces.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "timestamp": t.get("timestamp"),
                "environment": t.get("environment"),
                "userId": t.get("userId"),
                "sessionId": t.get("sessionId"),
                "tags": t.get("tags", []),
                "bookmarked": t.get("bookmarked", False),
                "latency": t.get("latency"),
                "totalCost": t.get("totalCost"),
                "htmlPath": t.get("htmlPath"),
            })

    with open(index_path, "w") as f:
        json.dump({"total": len(all_traces), "traces": all_traces}, f, indent=2, ensure_ascii=False)

    return all_traces


def print_stats(traces):
    envs, names = {}, {}
    for t in traces:
        envs[t["environment"]] = envs.get(t["environment"], 0) + 1
        prefix = t["name"].split(":")[0] if t["name"] else "unknown"
        names[prefix] = names.get(prefix, 0) + 1

    print(f"\nEnvironment distribution:")
    for e, c in sorted(envs.items(), key=lambda x: -x[1]):
        print(f"  {e}: {c}")

    sessions = {t["sessionId"] for t in traces if t["sessionId"]}
    users = {t["userId"] for t in traces if t["userId"]}
    print(f"\nUnique sessions: {len(sessions)}")
    print(f"Unique users: {len(users)}")

    lats = [t["latency"] for t in traces if t.get("latency")]
    if lats:
        lats_sorted = sorted(lats)
        print(f"\nLatency: min={min(lats):.1f}s  max={max(lats):.1f}s  "
              f"avg={sum(lats)/len(lats):.1f}s  median={lats_sorted[len(lats)//2]:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Fetch all Langfuse traces and build index")
    parser.add_argument("--output-dir", required=True, help="Directory for pages/ and trace-index.json")
    parser.add_argument("--workers", type=int, default=5, help="Parallel fetch threads (default: 5)")
    parser.add_argument("--limit", type=int, default=100, help="Traces per page (default: 100)")
    args = parser.parse_args()

    check_credentials()

    pages_dir = os.path.join(args.output_dir, "pages")
    index_path = os.path.join(args.output_dir, "trace-index.json")

    print("Fetching page 1...")
    page1 = fetch_page(1, args.limit)
    save_page(pages_dir, 1, page1)

    meta = page1["body"]["meta"]
    total_items = meta["totalItems"]
    total_pages = meta["totalPages"]
    print(f"Total: {total_items} traces, {total_pages} pages")

    remaining = list(range(2, total_pages + 1))
    completed = 1
    errors = []

    print(f"Fetching remaining {len(remaining)} pages ({args.workers} workers)...")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_page, p, args.limit): p for p in remaining}
        for future in as_completed(futures):
            page = futures[future]
            try:
                data = future.result()
                save_page(pages_dir, page, data)
                completed += 1
                if completed % 25 == 0 or completed == total_pages:
                    print(f"  {completed}/{total_pages} pages done")
            except Exception as e:
                errors.append((page, str(e)))
                print(f"  ERROR page {page}: {e}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} pages failed: {[p for p, _ in errors]}")

    print("\nBuilding index...")
    all_traces = build_index(pages_dir, total_pages, index_path)
    print(f"Index: {len(all_traces)} traces -> {index_path}")

    print_stats(all_traces)


if __name__ == "__main__":
    main()
