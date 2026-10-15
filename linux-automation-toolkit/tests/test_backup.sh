#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$PROJECT_DIR/scripts/backup.sh"
TEST_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Test 1: successful backup
mkdir -p "$TEST_DIR/source"
echo "test data" > "$TEST_DIR/source/example.txt"

"$SCRIPT" "$TEST_DIR/source" "$TEST_DIR/backups"

archive="$(find "$TEST_DIR/backups" -name '*.tar.gz' -type f | head -n 1)"

if [[ -z "$archive" ]]; then
    echo "FAIL: archive was not created"
    exit 1
fi

if ! tar -tzf "$archive" | grep -q 'source/example.txt'; then
    echo "FAIL: expected file is missing from archive"
    exit 1
fi

echo "PASS: backup creates a valid archive"

# Test 2: missing source directory
if "$SCRIPT" "$TEST_DIR/does-not-exist" "$TEST_DIR/backups"; then
    echo "FAIL: missing source should return an error"
    exit 1
fi

echo "PASS: missing source is rejected"

# Test 3: backup directory inside source
if "$SCRIPT" "$TEST_DIR/source" "$TEST_DIR/source/backups"; then
    echo "FAIL: backup directory inside source should be rejected"
    exit 1
fi

echo "PASS: backup inside source is rejected"
