
import argparse
import re
import sys
from collections import Counter
from pathlib import Path


LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+.*?"\s+'
    r'(?P<status>\d{3})\s+'
)


def analyze_log(log_path: Path) -> int:
    if not log_path.is_file():
        print(f"Error: file not found: {log_path}", file=sys.stderr)
        return 1

    status_codes = Counter()
    ip_addresses = Counter()
    malformed_lines = 0
    total_lines = 0

    with log_path.open("r", encoding="utf-8", errors="replace") as log_file:
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

    print(f"Log file: {log_path}")
    print(f"Total lines: {total_lines}")
    print(f"Parsed requests: {sum(status_codes.values())}")
    print(f"Malformed lines: {malformed_lines}")

    print("\nHTTP status classes:")
    for status_class in (2, 3, 4, 5):
        count = sum(
            amount
            for code, amount in status_codes.items()
            if code // 100 == status_class
        )
        print(f"{status_class}xx: {count}")

    print("\nTop 5 IP addresses:")
    for ip, count in ip_addresses.most_common(5):
        print(f"{ip}: {count} requests")

    print("\nHTTP status codes:")
    for code, count in sorted(status_codes.items()):
        print(f"{code}: {count}")

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
    args = parser.parse_args()

    return analyze_log(args.logfile)


if __name__ == "__main__":
    sys.exit(main())
