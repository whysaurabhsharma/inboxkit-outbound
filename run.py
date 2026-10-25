#!/usr/bin/env python3
"""inboxkit-outbound CLI. Writes CSVs. Never sends."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def cmd_run(args):
    import pipeline
    stats = pipeline.run(args.icp, limit=args.limit, offline=args.offline)
    print("Run complete.")
    for key in ("rows_in", "deduped", "suppressed", "invalid",
                "catch_all", "live", "seconds"):
        print("  {0:<12} {1}".format(key, stats[key]))
    print("")
    print("Wrote data/out/leads.csv, rejects.csv, suppressed.csv, held.csv")
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
    r.set_defaults(offline=True, func=cmd_run)

    s = sub.add_parser("suppress", help="Honour an opt-out")
    s.add_argument("--add", required=True)
    s.add_argument("--reason", default="opt_out")
    s.set_defaults(func=cmd_suppress)

    rep = sub.add_parser("report", help="Print the Monday review")
    rep.set_defaults(func=cmd_report)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
