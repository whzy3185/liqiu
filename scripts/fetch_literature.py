"""Discover, deduplicate, enrich, and conservatively code scholarly records.

Crossref supplies publisher-deposited metadata. Semantic Scholar is used only to
detect abstract availability and to derive controlled component tags in memory;
abstract text is not redistributed in this repository.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
YEAR_FROM = 2019
YEAR_TO = 2026
DISCOVERY_QUERIES = [
    "granular-ball computing", "granular ball classifier",
    "granular ball generation", "granular ball clustering",
    "granular ball rough set", "granular ball neighborhood rough set",
    "granular ball feature selection", "granular ball three-way decision",
    "granular ball anomaly detection", "granular ball graph learning",
    "granular ball deep learning", "granular ball federated learning",
    "granular ball open set", "granular ball uncertainty",
    "granular ball calibration", "granular ball conformal prediction",
    "three-way decision", "sequential three-way decision",
    "three-way classification rough set", "three-way clustering",
    "neighborhood rough set", "multi-granularity learning rough set",
    "multigranulation rough set", "adaptive granulation rough set",
    "dynamic granulation rough set", "online granular computing",
    "incremental granular computing", "justifiable granularity",
    "shadowed set granular computing", "uncertainty granular computing",
    "three-way decision agent", "granular computing retrieval agent",
]
FOUNDATIONAL_QUERIES = [
    "granular computing", "rough sets Pawlak", "three-way decisions Yao",
    "justifiable granularity Pedrycz", "shadowed sets Pedrycz",
]
MUST_INCLUDE_DOIS = {
    "10.1016/j.ins.2019.01.010",   # Original GBC classifiers
    "10.1109/tnnls.2022.3203381", # Efficient/adaptive GB generation
    "10.1109/tetci.2024.3359091", # GBG++
    "10.1016/j.ins.2025.122295",  # Local-density GB generation
    "10.1109/tnnls.2023.3325199", # Unified GBRS
    "10.1109/tfuzz.2024.3397697", # 3WC-GBNRS++
    "10.1109/tfuzz.2025.3536564", # Fuzzy GBRS three-way decision
}

PAPER_FIELDS = [
    "paper_id", "title", "year", "venue", "doi", "openalex_id", "url",
    "primary_source_url", "authors", "citations_count", "concepts",
    "abstract_status", "code_url", "search_query", "retrieved_at",
    "verification_status", "notes",
]
COMPONENT_FIELDS = [
    "paper_id", "paper", "year", "venue", "task", "representation",
    "granulation", "split_criterion", "merge_criterion", "stop_criterion",
    "uncertainty", "decision", "downstream", "dataset", "noise", "baseline",
    "main_gain", "code", "author_weakness", "suspected_weakness",
    "evidence_level", "source_url", "notes",
]


def _curl_json(url: str, *, body: Mapping[str, Any] = None, attempts: int = 4) -> Mapping[str, Any]:
    command = [
        "curl", "-sS", "-L", "--connect-timeout", "10", "--max-time", "45",
        "-A", "granular-research-lab/0.1 (https://github.com/whzy3185/liqiu)",
        "-H", "Accept: application/json",
    ]
    if body is not None:
        command += ["-H", "Content-Type: application/json", "--data-binary", json.dumps(body)]
    command.append(url)
    last_error = ""
    for attempt in range(attempts):
        process = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            try:
                return json.loads(process.stdout)
            except json.JSONDecodeError as exc:
                last_error = f"invalid JSON: {exc}; prefix={process.stdout[:200]!r}"
        else:
            last_error = process.stderr.strip()
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {attempts} attempts: {url}: {last_error}")


def _clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def _normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _published_year(item: Mapping[str, Any]) -> int:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                pass
    return 0


def _authors(item: Mapping[str, Any]) -> List[str]:
    values = []
    for author in item.get("author", []):
        name = " ".join(part for part in (author.get("given", ""), author.get("family", "")) if part)
        if name:
            values.append(name)
    return values


def _crossref_query(query: str, *, foundational: bool = False, rows: int = 35) -> Tuple[int, List[Mapping[str, Any]]]:
    parameters = {
        "query.title": query,
        "rows": str(rows),
        "select": "DOI,title,author,published,container-title,URL,is-referenced-by-count,abstract,type",
    }
    if foundational:
        parameters["filter"] = "until-pub-date:2018-12-31"
    else:
        parameters["filter"] = f"from-pub-date:{YEAR_FROM}-01-01,until-pub-date:{YEAR_TO}-12-31"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(parameters)
    payload = _curl_json(url)
    message = payload["message"]
    if not isinstance(message, Mapping):
        raise RuntimeError(f"Crossref rejected query {query!r}: {message}")
    return int(message.get("total-results", 0)), list(message.get("items", []))


def _relevance_score(title: str, queries: Iterable[str], year: int) -> int:
    text = _normalized_title(title)
    score = 0
    weighted = [
        ("granular ball", 120), ("three way decision", 100),
        ("granular computing", 90), ("neighborhood rough set", 75),
        ("multigranulation rough set", 75), ("rough set", 55),
        ("three way", 45), ("multi granularity", 40),
        ("justifiable granularity", 60), ("shadowed set", 55),
        ("adaptive granulation", 45), ("dynamic granulation", 45),
    ]
    for phrase, weight in weighted:
        if phrase in text:
            score += weight
    for query in queries:
        query_tokens = set(_normalized_title(query).split())
        title_tokens = set(text.split())
        score += 4 * len(query_tokens.intersection(title_tokens))
    if YEAR_FROM <= year <= YEAR_TO:
        score += 12
    return score


def _discover(rows: int) -> Tuple[List[MutableMapping[str, Any]], List[Mapping[str, Any]]]:
    works: Dict[str, MutableMapping[str, Any]] = {}
    logs: List[Mapping[str, Any]] = []
    for foundational, queries in ((False, DISCOVERY_QUERIES), (True, FOUNDATIONAL_QUERIES)):
        for index, query in enumerate(queries, start=1):
            total, items = _crossref_query(query, foundational=foundational, rows=rows)
            accepted = 0
            for item in items:
                titles = item.get("title") or []
                if not titles:
                    continue
                title = _clean_text(titles[0])
                year = _published_year(item)
                doi = str(item.get("DOI", "")).lower().strip()
                key = f"doi:{doi}" if doi else f"title:{_normalized_title(title)}"
                current = works.get(key)
                if current is None:
                    current = dict(item)
                    current["_title"] = title
                    current["_year"] = year
                    current["_queries"] = []
                    works[key] = current
                if query not in current["_queries"]:
                    current["_queries"].append(query)
                accepted += 1
            logs.append({
                "query": query, "scope": "pre-2019" if foundational else "2019-2026",
                "source_total": total, "retrieved": len(items), "ingested": accepted,
                "ordinal": index,
            })
            print(f"Crossref {query!r}: {len(items)} retrieved, {len(works)} unique", flush=True)
    ranked = sorted(
        works.values(),
        key=lambda item: (
            _relevance_score(item["_title"], item["_queries"], item["_year"]),
            int(item.get("is-referenced-by-count", 0) or 0),
        ),
        reverse=True,
    )
    return ranked, logs


def _is_relevant(item: Mapping[str, Any]) -> bool:
    title = _normalized_title(item["_title"])
    core = (
        "granular ball", "granular computing", "three way decision",
        "three way classification", "three way clustering", "rough set",
        "multigranulation", "multi granularity", "justifiable granularity",
        "shadowed set", "adaptive granulation", "dynamic granulation",
    )
    return any(phrase in title for phrase in core)


def _semantic_scholar_enrich(items: Sequence[MutableMapping[str, Any]]) -> None:
    cache_path = ROOT / "work" / "semantic_scholar.json"
    cache: Dict[str, Mapping[str, Any]] = {}
    if cache_path.exists():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            cache = loaded

    def apply_result(item: MutableMapping[str, Any], result: Mapping[str, Any]) -> None:
        item["_s2"] = result
        semantic_abstract = _clean_text(result.get("abstract") or "")
        if semantic_abstract:
            item["_abstract"] = semantic_abstract

    def persist_cache() -> None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    doi_items = []
    for index, item in enumerate(items):
        doi = str(item.get("DOI", "")).lower()
        if not doi:
            continue
        if doi in cache:
            apply_result(item, cache[doi])
        else:
            doi_items.append((index, item))
    if cache:
        print(f"Applied {sum(1 for item in items if item.get('_s2'))} cached Semantic Scholar records.", flush=True)

    for start in range(0, len(doi_items), 80):
        batch = doi_items[start:start + 80]
        ids = [f"DOI:{item['DOI']}" for _, item in batch]
        url = (
            "https://api.semanticscholar.org/graph/v1/paper/batch?fields="
            "title,year,venue,abstract,authors,citationCount,openAccessPdf,url,externalIds"
        )
        try:
            results = _curl_json(url, body={"ids": ids})
        except RuntimeError as exc:
            print(f"Semantic Scholar batch skipped: {exc}", flush=True)
            continue
        if not isinstance(results, list):
            print(f"Semantic Scholar batch returned non-list payload; skipped: {results}", flush=True)
            continue
        for (index, item), result in zip(batch, results):
            if isinstance(result, Mapping):
                doi = str(item.get("DOI", "")).lower()
                cache[doi] = result
                apply_result(item, result)
        persist_cache()
        print(f"Semantic Scholar enriched {min(start + len(batch), len(doi_items))}/{len(doi_items)} DOI records", flush=True)
        time.sleep(1.0)

    remaining = [item for _, item in doi_items if not item.get("_s2")]
    consecutive_limits = 0
    for ordinal, item in enumerate(remaining, start=1):
        doi = str(item["DOI"]).lower()
        url = (
            "https://api.semanticscholar.org/graph/v1/paper/DOI:"
            + urllib.parse.quote(doi, safe="/.:()")
            + "?fields=title,year,venue,abstract,authors,citationCount,openAccessPdf,url,externalIds"
        )
        try:
            result = _curl_json(url, attempts=2)
        except RuntimeError as exc:
            print(f"Semantic Scholar single-record request failed for {doi}: {exc}", flush=True)
            continue
        if isinstance(result, Mapping) and not result.get("code") and result.get("paperId"):
            cache[doi] = result
            apply_result(item, result)
            persist_cache()
            consecutive_limits = 0
        else:
            print(f"Semantic Scholar single-record payload skipped for {doi}: {result}", flush=True)
            is_service_error = bool(result.get("code")) or "too many requests" in str(result).lower()
            consecutive_limits = consecutive_limits + 1 if is_service_error else 0
            if consecutive_limits >= 3:
                print("Stopping single-record enrichment after three consecutive service errors.", flush=True)
                break
        if ordinal % 20 == 0:
            print(f"Semantic Scholar single-record enrichment {ordinal}/{len(remaining)}", flush=True)
        time.sleep(0.35)


def _dedupe_versions(items: Sequence[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
    """Collapse exact-title preprint/published versions, preferring a named venue."""
    deduplicated: Dict[str, MutableMapping[str, Any]] = {}
    for item in items:
        key = _normalized_title(item["_title"])
        current = deduplicated.get(key)
        if current is None:
            deduplicated[key] = item
            continue
        current_venue = (current.get("container-title") or [""])[0]
        new_venue = (item.get("container-title") or [""])[0]
        current_is_preprint = "ssrn" in str(current.get("DOI", "")).lower() or not current_venue
        new_is_published = "ssrn" not in str(item.get("DOI", "")).lower() and bool(new_venue)
        chosen, other = (item, current) if current_is_preprint and new_is_published else (current, item)
        chosen["_queries"] = sorted(set(chosen.get("_queries", []) + other.get("_queries", [])))
        deduplicated[key] = chosen
    return list(deduplicated.values())


def _tag(text: str, mapping: Sequence[Tuple[str, Sequence[str]]], default: str = "not reported in metadata/abstract") -> str:
    found = [label for label, patterns in mapping if any(pattern in text for pattern in patterns)]
    return "; ".join(found) if found else default


def _component_row(item: Mapping[str, Any], paper_id: str, source_url: str) -> Dict[str, Any]:
    title = item["_title"]
    abstract = item.get("_abstract", "")
    text = _normalized_title(title + " " + abstract)
    abstract_available = bool(abstract)
    task = _tag(text, [
        ("classification", ("classification", "classifier")),
        ("clustering", ("clustering", "cluster analysis")),
        ("feature selection", ("feature selection", "attribute reduction")),
        ("anomaly/outlier detection", ("anomaly detection", "outlier detection")),
        ("regression", ("regression",)), ("recommendation", ("recommendation",)),
        ("stream/online learning", ("stream", "online learning", "incremental learning")),
        ("open-set/OOD", ("open set", "open world", "out of distribution")),
        ("graph learning", ("graph neural", "graph convolution", "graph learning")),
        ("uncertainty quantification", ("uncertainty quantification", "conformal", "calibration")),
        ("decision analysis", ("decision making", "decision analysis", "three way decision")),
    ])
    representation = _tag(text, [
        ("granular ball", ("granular ball",)),
        ("rough-set neighborhood", ("neighborhood rough",)),
        ("rough-set approximation", ("rough set",)),
        ("graph", (" graph ", "graph neural", "network data")),
        ("interval granule", ("interval granulation", "interval valued")),
        ("fuzzy granule", ("fuzzy granular", "fuzzy rough")),
        ("shadowed set", ("shadowed set",)),
    ], default="points/objects or not reported")
    granulation = _tag(text, [
        ("granular-ball generation", ("granular ball",)),
        ("local-density", ("local density", "density based")),
        ("adaptive/dynamic", ("adaptive granulation", "dynamic granulation", "adaptive granular")),
        ("multi-granulation", ("multigranulation", "multi granulation")),
        ("neighborhood", ("neighborhood rough", "neighborhood granulation")),
        ("hierarchical/multi-level", ("hierarchical granular", "multi level gran")),
        ("fuzzy", ("fuzzy gran", "fuzzy rough")),
    ])
    split = _tag(text, [
        ("purity", ("purity",)), ("local density", ("local density",)),
        ("entropy/information", ("entropy", "information gain")),
        ("radius/distance", ("radius", "distance based split")),
    ])
    merge = _tag(text, [
        ("overlap", ("overlap based merg",)), ("distance", ("distance based merg",)),
        ("density", ("density based merg",)),
    ])
    uncertainty = _tag(text, [
        ("three-way boundary/defer region", ("three way", "boundary region")),
        ("fuzzy membership", ("fuzzy membership", "fuzzy rough")),
        ("probabilistic", ("probabilistic", "probability")),
        ("entropy", ("entropy",)), ("purity proxy", ("purity",)),
        ("interval", ("interval uncertainty", "interval granulation")),
        ("conformal prediction", ("conformal",)),
    ])
    decision = _tag(text, [
        ("three-way accept/defer/reject", ("three way decision", "three way classification")),
        ("classification decision", ("classifier", "classification")),
        ("ranking/selection", ("feature selection", "attribute reduction")),
        ("cluster assignment", ("clustering",)),
    ])
    downstream = _tag(text, [
        ("SVM", ("support vector machine", " svm ")),
        ("kNN", ("nearest neighbor", " knn ")),
        ("neural network", ("neural network", "deep learning")),
        ("graph neural network", ("graph neural", "graph convolution")),
        ("rough-set reducer", ("attribute reduction", "feature selection")),
    ])
    noise = _tag(text, [
        ("label noise", ("label noise", "noisy label")),
        ("feature noise", ("feature noise",)), ("outliers", ("outlier",)),
        ("distribution shift", ("distribution shift", "concept drift", "covariate shift")),
        ("class imbalance", ("class imbalance", "imbalanced")),
    ], default="not reported in metadata/abstract")
    return {
        "paper_id": paper_id, "paper": title, "year": item["_year"],
        "venue": (item.get("container-title") or [""])[0], "task": task,
        "representation": representation, "granulation": granulation,
        "split_criterion": split, "merge_criterion": merge,
        "stop_criterion": "not reported in metadata/abstract",
        "uncertainty": uncertainty, "decision": decision, "downstream": downstream,
        "dataset": "requires full-text verification", "noise": noise,
        "baseline": "requires full-text verification",
        "main_gain": "requires full-text verification",
        "code": "unknown; repository search pending", "author_weakness": "requires full-text verification",
        "suspected_weakness": "not inferred before method/full-text review",
        "evidence_level": "abstract-coded" if abstract_available else "metadata-only",
        "source_url": source_url,
        "notes": "Controlled keyword coding; unknown fields are deliberate, not negative evidence.",
    }


def _write_outputs(items: Sequence[Mapping[str, Any]], logs: Sequence[Mapping[str, Any]]) -> None:
    literature = ROOT / "literature"
    taxonomy = ROOT / "taxonomy"
    reports = ROOT / "reports"
    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    paper_rows: List[Dict[str, Any]] = []
    json_rows: List[Dict[str, Any]] = []
    component_rows: List[Dict[str, Any]] = []

    for sequence, item in enumerate(items, start=1):
        doi = str(item.get("DOI", "")).lower().strip()
        paper_id = f"P{sequence:04d}"
        source_url = f"https://doi.org/{doi}" if doi else str(item.get("URL", ""))
        s2 = item.get("_s2", {}) or {}
        authors = _authors(item)
        queries = item.get("_queries", [])
        abstract_status = "available-and-coded-not-redistributed" if item.get("_abstract") else "not-available-from-enrichment"
        row = {
            "paper_id": paper_id, "title": item["_title"], "year": item["_year"],
            "venue": (item.get("container-title") or [""])[0], "doi": doi,
            "openalex_id": "", "url": s2.get("url") or item.get("URL", ""),
            "primary_source_url": source_url, "authors": "; ".join(authors),
            "citations_count": s2.get("citationCount", item.get("is-referenced-by-count", 0)),
            "concepts": "", "abstract_status": abstract_status,
            "code_url": "", "search_query": "; ".join(queries),
            "retrieved_at": retrieved_at,
            "verification_status": "publisher-metadata+abstract-coded" if item.get("_abstract") else "publisher-metadata-only",
            "notes": "Full-text/component verification pending unless upgraded in later commits.",
        }
        paper_rows.append(row)
        json_rows.append({
            **row, "authors_list": authors, "search_queries": queries,
            "crossref_type": item.get("type", ""),
            "semantic_scholar_paper_id": s2.get("paperId", ""),
            "open_access_pdf_status": (s2.get("openAccessPdf") or {}).get("status"),
            "title_sha256": hashlib.sha256(item["_title"].encode("utf-8")).hexdigest(),
        })
        component_rows.append(_component_row(item, paper_id, source_url))

    with (literature / "papers.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(paper_rows)
    with (literature / "papers.jsonl").open("w", encoding="utf-8") as handle:
        for row in json_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with (taxonomy / "component_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPONENT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(component_rows)

    years = collections.Counter(str(row["year"]) for row in paper_rows)
    venues = collections.Counter(row["venue"] or "Unknown" for row in paper_rows)
    evidence = collections.Counter(row["evidence_level"] for row in component_rows)
    query_lines = [
        "# Search queries and coverage log", "",
        f"Generated at `{retrieved_at}`. Discovery uses Crossref publisher-deposited metadata;",
        "Semantic Scholar enrichment is used for abstract availability and controlled in-memory",
        "coding. Abstract text is not redistributed. Search ranking is not treated as relevance",
        "proof, and full-text-dependent fields remain explicitly unverified.", "",
        "| Scope | Query | Source total | Retrieved | Ingested |", "|---|---|---:|---:|---:|",
    ]
    for log in logs:
        query_lines.append(
            f"| {log['scope']} | {log['query']} | {log['source_total']} | {log['retrieved']} | {log['ingested']} |"
        )
    query_lines += [
        "", "## Deduplication", "",
        "DOI is the primary key; normalized title is the fallback. The retained set is restricted",
        "to titles containing a core granular/rough-set/three-way concept, then ranked by concept",
        "match and citation metadata. This favors precision over exhaustive recall.", "",
        "## Known gaps", "",
        "IEEE/ACM/Springer/ScienceDirect full-text fields and GitHub code availability require",
        "separate verification. Chinese-only databases and records without Crossref deposits are",
        "under-covered. Agent/RAG intersections may be absent because title-level relevance filtering",
        "rejects generic retrieval papers; they will receive a dedicated collision search later.",
    ]
    (literature / "search_queries.md").write_text("\n".join(query_lines) + "\n", encoding="utf-8")

    report = [
        "# Literature report", "", "## First-pass structured corpus", "",
        f"- Retained records: **{len(paper_rows)}**",
        f"- 2019–2026 records: **{sum(1 for row in paper_rows if YEAR_FROM <= int(row['year'] or 0) <= YEAR_TO)}**",
        f"- Pre-2019 theory/method records: **{sum(1 for row in paper_rows if 0 < int(row['year'] or 0) < YEAR_FROM)}**",
        f"- Abstract-coded records: **{evidence['abstract-coded']}**",
        f"- Metadata-only records: **{evidence['metadata-only']}**", "",
        "This is a discovery corpus, not a claim that every paper has been read in full. The",
        "component matrix deliberately labels full-text-only fields as unverified. Those fields",
        "will be upgraded for representative and highly connected papers before mechanism-level",
        "claims or novelty decisions are made.", "", "## Year distribution", "",
        "| Year | Papers |", "|---:|---:|",
    ]
    report += [f"| {year} | {count} |" for year, count in sorted(years.items(), reverse=True)]
    report += ["", "## Most frequent venues", "", "| Venue | Papers |", "|---|---:|"]
    report += [f"| {venue.replace('|', '/')} | {count} |" for venue, count in venues.most_common(15)]
    report += [
        "", "## Evidence limitations", "",
        "- Search relevance was checked at title level; topic boundaries still require manual audit.",
        "- Keyword-coded components are candidates for review, not authoritative method descriptions.",
        "- Datasets, baselines, claimed gains, author limitations, and code links are not inferred",
        "  when unavailable from metadata/abstracts.",
        "- Citation counts are discovery aids and are not quality scores.", "",
        "## Next verification tranche", "",
        "Prioritize foundational GBC, GBG++, local-density GBG, granular-ball rough-set, and",
        "three-way granular-ball papers; then follow their references and public code repositories.",
    ]
    (reports / "literature_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows-per-query", type=int, default=35)
    parser.add_argument("--limit", type=int, default=160)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    cache = ROOT / "work" / "crossref_discovery.json"
    if cache.exists() and not args.refresh:
        cached = json.loads(cache.read_text(encoding="utf-8"))
        discovered, logs = cached["discovered"], cached["logs"]
        print(f"Loaded {len(discovered)} Crossref candidates from cache.", flush=True)
    else:
        discovered, logs = _discover(args.rows_per_query)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(
            json.dumps({"discovered": discovered, "logs": logs}, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Cached {len(discovered)} Crossref candidates.", flush=True)
    discovered = _dedupe_versions(discovered)
    relevant_all = [item for item in discovered if _is_relevant(item)]
    pinned = [item for item in relevant_all if str(item.get("DOI", "")).lower() in MUST_INCLUDE_DOIS]
    missing_pins = MUST_INCLUDE_DOIS.difference(str(item.get("DOI", "")).lower() for item in pinned)
    if missing_pins:
        raise SystemExit(f"core DOI records missing from discovery cache: {sorted(missing_pins)}")
    pinned_dois = {str(item.get("DOI", "")).lower() for item in pinned}
    relevant = pinned + [
        item for item in relevant_all if str(item.get("DOI", "")).lower() not in pinned_dois
    ][:max(0, args.limit - len(pinned))]
    if len(relevant) < 100:
        raise SystemExit(f"precision filter retained only {len(relevant)} records; need at least 100")
    for item in relevant:
        item["_abstract"] = _clean_text(str(item.get("abstract", "")))
    _semantic_scholar_enrich(relevant)
    _write_outputs(relevant, logs)
    print(f"Wrote {len(relevant)} deduplicated records and component rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
