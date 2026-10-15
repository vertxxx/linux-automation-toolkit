#!/usr/bin/env bash

set -Eeuo pipefail

usage() {
    echo "Usage: $0 <source_directory> <backup_directory>" >&2
    exit 2
}

if [[ $# -ne 2 ]]; then
    usage
fi

source_dir="$1"
backup_dir="$2"

if [[ ! -d "$source_dir" ]]; then
    echo "Error: source directory does not exist: $source_dir" >&2
    exit 1
fi

source_dir="$(realpath "$source_dir")"

mkdir -p "$backup_dir"
backup_dir="$(realpath "$backup_dir")"

if [[ "$backup_dir" == "$source_dir" || "$backup_dir" == "$source_dir/"* ]]; then
    echo "Error: backup directory must be outside the source directory" >&2
    exit 1
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
source_name="$(basename "$source_dir")"
archive_name="${source_name}_${timestamp}.tar.gz"
archive_path="$backup_dir/$archive_name"

if tar -czf "$archive_path" -C "$(dirname "$source_dir")" "$source_name"; then
    echo "Backup completed successfully"
    echo "Archive: $archive_path"
else
    echo "Error: backup failed" >&2
    rm -f "$archive_path"
    exit 1
fi
