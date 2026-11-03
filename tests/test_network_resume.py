"""Tests for resuming scans without repeating completed requests."""

import httpx

from pingpanda.checkpoint import save_checkpoint


async def test_check_all_skips_completed_ids_and_preserves_input_order(
    checker, mock_transport, fake_dns, make_result
):
    urls = [
        "https://already.test/",
        "https://pending-a.test/",
        "https://pending-b.test/",
    ]
    requested = []
    persisted_snapshots = []

    def handler(request):
        requested.append(str(request.url))
        return httpx.Response(200)

    mock_transport(handler)
    initial = {0: make_result(url=urls[0], url_id=0, status=204)}

    results = await checker.check_all(
        urls,
        initial_results=initial,
        on_result=persisted_snapshots.append,
    )

    assert list(results) == [0, 1, 2]
    assert requested == ["https://pending-a.test/", "https://pending-b.test/"]
    assert [result.status for result in results.values()] == [204, 200, 200]
    assert len(persisted_snapshots) == 2
    assert all(0 in snapshot for snapshot in persisted_snapshots)


async def test_check_all_does_not_make_requests_when_checkpoint_is_complete(
    checker, mock_transport, make_result
):
    def unexpected_request(request):
        raise AssertionError("A completed URL must not be requested again.")

    mock_transport(unexpected_request)
    urls = ["https://done.test/"]
    initial = {0: make_result(url=urls[0], url_id=0)}

    results = await checker.check_all(urls, initial_results=initial)

    assert results == initial


async def test_cli_resumes_from_checkpoint(
    checker, mock_transport, fake_dns, make_result, tmp_path, capsys
):
    urls = ["https://done.test/", "https://pending.test/"]
    list_file = tmp_path / "urls.txt"
    list_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    checkpoint = tmp_path / "scan.json"
    save_checkpoint(
        checkpoint,
        urls,
        {0: make_result(url=urls[0], url_id=0, status=200)},
    )
    requested = []

    def handler(request):
        requested.append(str(request.url))
        return httpx.Response(200)

    mock_transport(handler)
    await checker.main(
        [
            "-l",
            str(list_file),
            "--resume",
            "--checkpoint",
            str(checkpoint),
        ]
    )

    output = capsys.readouterr().out
    assert requested == ["https://pending.test/"]
    assert "Resuming scan: 1 of 2 URLs already completed." in output
    assert "https://done.test/" in output
    assert "https://pending.test/" in output
