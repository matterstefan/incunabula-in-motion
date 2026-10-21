"""Retrieve current Zurich holdings; preserve complete MEI records."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
from mei_client import request_page, fetch_complete_query, RateLimiter, atomic_write_json, now_iso

INSTITUTION = "ZurichZB"
QUERY = "data.holdingInstitutionId:ZurichZB"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "retrieved"

def validate_records(records):
    if not records:
        raise ValueError("No records returned. Verify the institution query before proceeding.")
    if any(r.get("holdingInstitutionId") != INSTITUTION for r in records):
        raise ValueError("Query returned another holding institution; review required.")

def terms(value):
    if isinstance(value, str):
        return [v.strip() for v in value.split(";") if v.strip()]
    if isinstance(value, list):
        return [term for v in value for term in terms(v)]
    return []

def summarise(records):
    by_term = defaultdict(lambda: {"copies": set(), "editions": set(), "fields": set()})
    tagged = set()
    for r in records:
        host = r.get("hostItem") or {}
        for field in ("subject", "keywords"):
            for term in terms(host.get(field)):
                entry = by_term[term]
                entry["copies"].add(r["id"])
                if r.get("hostItemId"):
                    entry["editions"].add(r["hostItemId"])
                entry["fields"].add(field)
                tagged.add(r["id"])
    return by_term, {
        "copies": len(records),
        "editions_with_istc_id": len({r["hostItemId"] for r in records if r.get("hostItemId")}),
        "copies_with_subject_or_keywords": len(tagged),
        "copies_without_subject_or_keywords": len(records)-len(tagged),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["test","full"], default="test")
    args = parser.parse_args()
    limiter = RateLimiter(2)
    if args.mode == "test":
        response = request_page(QUERY, 0, 5, limiter)
        records = response.get("rows", [])
        validate_records(records)
        output = {"retrieved_at": now_iso(), "query": QUERY, "complete": False,
                  "reported_hits": response.get("hits"), "records": records}
    else:
        response = fetch_complete_query(QUERY, limiter)
        records = response["rows"]
        validate_records(records)
        output = {**{k:v for k,v in response.items() if k != "rows"},
                  "complete": True, "records": records}
    atomic_write_json(OUT / ("zurich-" + args.mode + ".json"), output)
    vocabulary, counts = summarise(records)
    atomic_write_json(OUT / "summary.json", {
        "mode": args.mode, "query": QUERY, "institution_id": INSTITUTION,
        "reported_hits": output["reported_hits"], **counts})
    with (OUT / "subjects.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term","source_fields","copies","editions"])
        for term, entry in sorted(vocabulary.items()):
            writer.writerow([term," | ".join(sorted(entry["fields"])),
                             len(entry["copies"]),len(entry["editions"])])
    print({"mode": args.mode, **counts})

if __name__ == "__main__":
    main()
