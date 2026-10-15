from unittest.mock import patch
from urllib.error import URLError

from scripts.health_check import check_url, main


def test_check_url_success():
    with patch("scripts.health_check.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.status = 200

        result = check_url("https://example.com", timeout=5)

    assert result["status"] == "OK"
    assert result["http_status"] == 200
    assert result["response_time_ms"] is not None
    assert result["error"] is None


def test_check_url_http_error():
    with patch("scripts.health_check.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = URLError("Connection failed")

        result = check_url("https://example.com", timeout=5)

    assert result["status"] == "FAIL"
    assert result["http_status"] is None
    assert result["error"] is not None


def test_main_rejects_invalid_url():
    with patch("sys.argv", ["health_check.py", "not-a-url"]):
        exit_code = main()

    assert exit_code == 1


def test_main_rejects_non_positive_timeout():
    with patch(
        "sys.argv",
        ["health_check.py", "https://example.com", "--timeout", "0"],
    ):
        try:
            main()
        except SystemExit as error:
            assert error.code == 2
        else:
            raise AssertionError("Expected argparse to reject timeout")
