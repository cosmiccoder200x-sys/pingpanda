"""Tests for ordered URL input loading and checkpoint CLI options."""

from argparse import Namespace

from pingpanda.cli import load_urls, parse_arguments


def test_load_urls_preserves_file_order_and_duplicate_entries(tmp_path):
    list_file = tmp_path / "urls.txt"
    list_file.write_text(
        "https://second.test\n\nhttps://first.test\nhttps://second.test\n",
        encoding="utf-8",
    )

    urls = load_urls(Namespace(domain=None, list=str(list_file)))

    assert urls == [
        "https://second.test",
        "https://first.test",
        "https://second.test",
    ]


def test_checkpoint_options_have_safe_defaults():
    args = parse_arguments(["-d", "https://example.com"])

    assert args.checkpoint == ".pingpanda-checkpoint.json"
    assert args.resume is False


def test_resume_option_accepts_custom_checkpoint_path():
    args = parse_arguments(
        ["-l", "urls.txt", "--resume", "--checkpoint", "custom-state.json"]
    )

    assert args.resume is True
    assert args.checkpoint == "custom-state.json"
