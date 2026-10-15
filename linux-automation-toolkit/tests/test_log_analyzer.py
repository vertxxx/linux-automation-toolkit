from scripts.log_analyzer import analyze_log


def test_analyzes_http_statuses_and_ip_addresses(tmp_path, capsys):
    log_file = tmp_path / "access.log"
    log_file.write_text(
        '192.168.1.10 - - [15/Oct/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100\n'
        '192.168.1.11 - - [15/Oct/2026:10:00:01 +0000] "GET /api HTTP/1.1" 204 120\n'
        '192.168.1.10 - - [15/Oct/2026:10:00:02 +0000] "POST /login HTTP/1.1" 500 80\n',
        encoding="utf-8",
    )

    result = analyze_log(log_file)
    output = capsys.readouterr().out

    assert result == 0
    assert "Total lines: 3" in output
    assert "Parsed requests: 3" in output
    assert "2xx: 2" in output
    assert "4xx: 0" in output
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
