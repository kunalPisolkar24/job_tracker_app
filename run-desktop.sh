#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

if ! command -v make >/dev/null 2>&1; then
    printf 'Error: make is not installed or not available in PATH.\n' >&2
    exit 1
fi

if [[ ! -f "$PROJECT_ROOT/makefile" && ! -f "$PROJECT_ROOT/Makefile" ]]; then
    printf 'Error: makefile not found in %s.\n' "$PROJECT_ROOT" >&2
    exit 1
fi

run_make_target() {
    local target="$1"
    if ! make -C "$PROJECT_ROOT" "$target"; then
        printf 'Error: make %s failed.\n' "$target" >&2
        exit 1
    fi
}

linux_artifact="$PROJECT_ROOT/dist/JobTrackerExec"
windows_artifact="$PROJECT_ROOT/dist/JobTrackerExec.exe"

if [[ ! -f "$linux_artifact" && ! -f "$windows_artifact" ]]; then
    run_make_target build-desktop
fi

run_make_target run-desktop
