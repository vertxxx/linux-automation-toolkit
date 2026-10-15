from scripts.log_analyzer import analyze_log
import json


def test_analyzes_http_statuses_and_ip_addresses(tmp_path, capsys):
    log_file = tmp_path / "access.log"
    log_file.write_text(
        '192.168.1.10 - - [15/Oct/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100\n'
        '192.168.1.11 - - [15/Oct/2026:10:00:01 +0000] "GET /api HTTP/1.1" 404 120\n'
        '192.168.1.10 - - [15/Oct/2026:10:00:02 +0000] "POST /login HTTP/1.1" 500 80\n',
        encoding="utf-8",
    )

    result = analyze_log(log_file)
    output = capsys.readouterr().out

    assert result == 0
    assert "Total lines: 3" in output
    assert "Parsed requests: 3" in output
    assert "2xx: 1" in output
    assert "4xx: 1" in output
    assert "5xx: 1" in output
    assert "192.168.1.10: 2 requests" in output


def test_handles_utf8_bom(tmp_path, capsys):
    log_file = tmp_path / "bom.log"
    log_file.write_text(
        '192.168.1.10 - - [15/Oct/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100\n'
        '192.168.1.10 - - [15/Oct/2026:10:00:01 +0000] "GET /api HTTP/1.1" 200 120\n',
        encoding="utf-8-sig",
    )

    result = analyze_log(log_file)
    output = capsys.readouterr().out

    assert result == 0
    assert "Malformed lines: 0" in output
    assert "192.168.1.10: 2 requests" in output
    assert "\ufeff192.168.1.10" not in output


def test_returns_error_for_missing_file(tmp_path, capsys):
    log_file = tmp_path / "missing.log"

    result = analyze_log(log_file)
    output = capsys.readouterr().err

    assert result == 1
    assert "file not found" in output.lower()
    
# тест сохранения json 
def test_saves_json_report(tmp_path):
    log_file = tmp_path / "access.log"
    json_file = tmp_path / "report.json"

    log_file.write_text(
        '192.168.1.10 - - [15/Oct/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100\n'
        '192.168.1.11 - - [15/Oct/2026:10:00:01 +0000] "GET /api HTTP/1.1" 404 120\n',
        encoding="utf-8",
    )

    result = analyze_log(log_file, json_file)
    report = json.loads(json_file.read_text(encoding="utf-8"))

    assert result == 0
    assert report["total_lines"] == 2
    assert report["parsed_requests"] == 2
    assert report["status_classes"]["2xx"] == 1
    assert report["status_classes"]["4xx"] == 1
    assert report["top_ips"][0] == {
        "ip": "192.168.1.10",
        "requests": 1,
    }

# тест неправильного json
def test_reports_error_when_json_path_is_invalid(tmp_path, capsys):
    log_file = tmp_path / "access.log"
    log_file.write_text(
        '192.168.1.10 - - [15/Oct/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100\n',
        encoding="utf-8",
    )

    invalid_json_path = tmp_path / "missing" / "report.json"

    result = analyze_log(log_file, invalid_json_path)
    error_output = capsys.readouterr().err

    assert result == 1
    assert "cannot write JSON report" in error_output
