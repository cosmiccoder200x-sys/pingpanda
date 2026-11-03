"""Command-line interface for PingPanda."""

from __future__ import annotations

import argparse
import sys

from pingpanda.checkpoint import CheckpointError, load_checkpoint, save_checkpoint
from pingpanda.constants import BANNER
from pingpanda.network import check_all
from pingpanda.report import classify_results, render_report, save_report

DEFAULT_CHECKPOINT = ".pingpanda-checkpoint.json"


def make_output_safe():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="replace")
        except (ValueError, OSError):
            pass


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description="URL Status Checker")
    parser.add_argument("-d", "--domain", help="Single domain/URL to check")
    parser.add_argument("-l", "--list", help="File containing list of domains/URLs to check")
    parser.add_argument("-o", "--output", help="File to save the output")
    parser.add_argument(
        "--checkpoint",
        default=DEFAULT_CHECKPOINT,
        metavar="PATH",
        help=f"Checkpoint file (default: {DEFAULT_CHECKPOINT})",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume unfinished URLs from the checkpoint file",
    )
    parser.add_argument("-v", "--version", action="store_true", help="Display version information")
    parser.add_argument("-update", action="store_true", help="Update the tool")
    return parser.parse_args(argv)


def load_urls(args):
    if args.domain:
        url = args.domain.strip()
        return [url] if url else []

    if args.list:
        with open(args.list, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]

    return None


async def main(argv=None):
    make_output_safe()
    args = parse_arguments(argv)

    if args.version:
        print("StatusChecker.py version 1.0")
        return

    if args.update:
        print("Checking for updates...")
        return

    print(BANNER)

    urls = load_urls(args)
    if not urls:
        print("No input provided. Use -d or -l option.")
        return

    initial_results = {}
    if args.resume:
        try:
            initial_results = load_checkpoint(args.checkpoint, urls)
        except CheckpointError as exc:
            print(f"Checkpoint error: {exc}", file=sys.stderr)
            return
        print(f"Resuming scan: {len(initial_results)} of {len(urls)} URLs already completed.")

    def persist_progress(completed_results):
        save_checkpoint(args.checkpoint, urls, completed_results)

    try:
        results = await check_all(
            urls,
            initial_results=initial_results,
            on_result=persist_progress,
        )
        # Also create a checkpoint for an empty or already-complete resumed scan.
        save_checkpoint(args.checkpoint, urls, results)
    except CheckpointError as exc:
        print(f"Checkpoint error: {exc}", file=sys.stderr)
        return

    status_codes = classify_results(results)
    render_report(status_codes)

    if args.output:
        save_report(status_codes, args.output)
