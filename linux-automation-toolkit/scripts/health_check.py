import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def check_url(url: str, timeout: float) -> dict:
    """Check whether an HTTP/HTTPS service responds."""
    result = {
        "url": url,
        "status": "FAIL",
        "http_status": None,
        "response_time_ms": None,
        "error": None,
    }

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DevOpsHealthCheck/1.0"},
        method="GET",
    )

    start_time = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result["http_status"] = response.status
            result["status"] = (
                "OK" if 200 <= response.status < 400 else "FAIL"
            )

    except urllib.error.HTTPError as error:
        result["http_status"] = error.code
        result["status"] = (
            "OK" if 200 <= error.code < 400 else "FAIL"
        )
        result["error"] = f"HTTP error: {error.code}"

    except (urllib.error.URLError, TimeoutError, OSError) as error:
        result["error"] = str(error)

    finally:
        result["response_time_ms"] = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check availability of HTTP/HTTPS services."
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more HTTP/HTTPS URLs to check",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        dest="json_path",
        help="Optional path to save results as JSON",
    )
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    results = []
    for url in args.urls:
        if not url.startswith(("http://", "https://")):
            result = {
                "url": url,
                "status": "FAIL",
                "http_status": None,
                "response_time_ms": 0,
                "error": "URL must start with http:// or https://",
            }
        else:
            result = check_url(url, args.timeout)

        results.append(result)

        print(
            f"[{result['status']}] {result['url']} "
            f"| HTTP: {result['http_status']} "
            f"| Time: {result['response_time_ms']} ms"
        )
        if result["error"]:
            print(f"  Error: {result['error']}")

    if args.json_path is not None:
        report = {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "total": len(results),
            "ok": sum(item["status"] == "OK" for item in results),
            "failed": sum(item["status"] == "FAIL" for item in results),
            "results": results,
        }

        try:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            with args.json_path.open("w", encoding="utf-8") as file:
                json.dump(report, file, ensure_ascii=False, indent=4)
                file.write("\n")
        except OSError as error:
            print(f"Error: cannot write JSON report: {error}")
            return 1

        print(f"\nJSON report saved to: {args.json_path}")

    return 0 if all(item["status"] == "OK" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())