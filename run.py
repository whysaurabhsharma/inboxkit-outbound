#!/usr/bin/env python3
"""inboxkit-outbound CLI. Writes CSVs. Never sends."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def cmd_run(args):
    import pipeline
    stats, rejects = pipeline.run(args.icp, limit=args.limit, offline=args.offline,
                                  source_name=args.source, record=args.record,
                                  enrich=args.enrich)
    print("Run complete ({0}).".format(stats["mode"]))
    for key in ("rows_in", "deduped", "suppressed", "off_icp", "accounts",
                "needs_contact", "invalid", "catch_all", "live", "seconds"):
        print("  {0:<14} {1}".format(key, stats[key]))
    reasons = {}
    for r in rejects:
        why = r.get("reason", "").split(":")[0]
        reasons[why] = reasons.get(why, 0) + 1
    if reasons:
        print("  rejected by reason: " + ", ".join(
            "{0} {1}".format(k, reasons[k]) for k in sorted(reasons)))
    print("")
    print("Wrote data/out/leads.csv, rejects.csv, suppressed.csv, held.csv, "
          "needs_contact.csv")
    return 0


def cmd_probe(args):
    import probe_boards
    values = [v.strip() for v in (args.names or "").split(",") if v.strip()]
    if args.file:
        values += [l.strip() for l in Path(args.file).read_text(
            encoding="utf-8-sig").splitlines() if l.strip() and not l.startswith("#")]
    if not values:
        print("Give --names or --file.")
        return 1
    found = probe_boards.probe(values)
    new = probe_boards.write(found)
    for r in found:
        print("  {0}:{1}  {2}  name_match={3}  jobs={4}".format(
            r["ats"], r["token"], r["board_name"], r["name_match"], r["open_jobs"]))
    print("{0} boards found, {1} new in config/boards_candidates.csv. "
          "Copy approved rows into config/boards.csv.".format(len(found), len(new)))
    return 0


def cmd_suppress(args):
    import suppress
    path = str(Path(__file__).resolve().parent / "config" / "suppression.csv")
    added = suppress.add(args.add, args.reason, path)
    if added:
        print("Suppressed {0} as {1}".format(args.add, args.reason))
    else:
        print("{0} was already suppressed".format(args.add))
    return 0


def cmd_first_lines(args):
    import first_line
    results = first_line.run(limit=args.limit)
    approved = sum(r["approved"] == "yes" for r in results)
    print("Wrote copy/first_lines.csv: {0} lines, {1} approved.".format(len(results), approved))
    return 0


def cmd_report(args):
    import report
    print(report.monday_review())
    return 0


def main():
    p = argparse.ArgumentParser(description="Turn one ICP into a lead list.")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="Run the pipeline")
    r.add_argument("--icp", default="config/icp.yaml")
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--live", dest="offline", action="store_false")
    r.add_argument("--source", choices=["boards", "apify"], default="boards",
                   help="live source; apify is off until config/apify.yaml names an actor")
    r.add_argument("--record", action="store_true",
                   help="save live responses to data/fixtures/live/<date>/")
    r.add_argument("--enrich", action="store_true",
                   help="find contacts with Prospeo; spends credits, needs --live")
    r.set_defaults(offline=True, func=cmd_run)

    s = sub.add_parser("suppress", help="Honour an opt-out")
    s.add_argument("--add", required=True)
    s.add_argument("--reason", default="opt_out")
    s.set_defaults(func=cmd_suppress)

    pr = sub.add_parser("probe", help="Find job boards for named agencies")
    pr.add_argument("--names", help="comma separated agency names or domains")
    pr.add_argument("--file", help="one agency name or domain per line")
    pr.set_defaults(func=cmd_probe)

    fl = sub.add_parser("first-lines", help="Run the first-line skill on leads.csv")
    fl.add_argument("--limit", type=int, default=10)
    fl.set_defaults(func=cmd_first_lines)

    rep = sub.add_parser("report", help="Print the Monday review")
    rep.set_defaults(func=cmd_report)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
