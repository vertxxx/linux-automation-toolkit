import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+.*?"\s+'
    r'(?P<status>\d{3})\s+'
)


def analyze_log(log_path: Path, json_path: Path | None = None) -> int:
    if not log_path.is_file():
        print(f"Error: file not found: {log_path}", file=sys.stderr)
        return 1

    status_codes = Counter()
    ip_addresses = Counter()
    malformed_lines = 0
    total_lines = 0

    with log_path.open("r", encoding="utf-8-sig", errors="replace") as log_file:
        for line in log_file:
            total_lines += 1
            match = LOG_PATTERN.search(line)

            if not match:
                malformed_lines += 1
                continue

            ip = match.group("ip")
            status = int(match.group("status"))

            status_codes[status] += 1
            ip_addresses[ip] += 1

    status_classes = {}
    for status_class in (2, 3, 4, 5):
        status_classes[f"{status_class}xx"] = sum(
            amount
            for code, amount in status_codes.items()
            if code // 100 == status_class
        )

    report = {
        "log_file": str(log_path),
        "total_lines": total_lines,
        "parsed_requests": sum(status_codes.values()),
        "malformed_lines": malformed_lines,
        "status_classes": status_classes,
        "top_ips": [
            {"ip": ip, "requests": count}
            for ip, count in ip_addresses.most_common(5)
        ],
        "status_codes": {
            str(code): count
            for code, count in sorted(status_codes.items())
        },
    }

    print(f"Log file: {log_path}")
    print(f"Total lines: {total_lines}")
    print(f"Parsed requests: {report['parsed_requests']}")
    print(f"Malformed lines: {malformed_lines}")

    print("\nHTTP status classes:")
    for status_class, count in status_classes.items():
        print(f"{status_class}: {count}")

    print("\nTop 5 IP addresses:")
    for item in report["top_ips"]:
        print(f"{item['ip']}: {item['requests']} requests")

    print("\nHTTP status codes:")
    for code, count in report["status_codes"].items():
        print(f"{code}: {count}")

    if json_path is not None:
        try:
            with json_path.open("w", encoding="utf-8") as report_file:
                json.dump(report, report_file, ensure_ascii=False, indent=4)
                report_file.write("\n")
        except OSError as error:
            print(f"Error: cannot write JSON report: {error}", file=sys.stderr)
            return 1

        print(f"\nJSON report saved to: {json_path}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze HTTP access logs."
    )
    parser.add_argument(
        "logfile",
        type=Path,
        help="Path to the access log file",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="Optional path to save the report as JSON",
    )
    args = parser.parse_args()

    return analyze_log(args.logfile, args.json_path)


if __name__ == "__main__":
    sys.exit(main())
