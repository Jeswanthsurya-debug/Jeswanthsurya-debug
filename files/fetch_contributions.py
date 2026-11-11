#!/usr/bin/env python3
"""Write data/contributions.json from GitHub's GraphQL API (last 12 months)."""
import json, os, urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "Jeswanthsurya-debug")
TOKEN = os.environ["GITHUB_TOKEN"]
QUERY = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
weeks{contributionDays{date contributionCount}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
res = json.load(urllib.request.urlopen(req))
weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
out = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"days": days}))
print(f"{len(days)} days written")
