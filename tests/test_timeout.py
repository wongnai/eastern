import asyncio
import subprocess

import pytest
from eastern.timeout import ProcessTimeout


def test_passed():
    assert ProcessTimeout(0.01, "echo").run_sync() == 0


def test_timeout_repeated_output():
    with pytest.raises(subprocess.TimeoutExpired):
        ProcessTimeout(0.01, "yes").run_sync()


def test_timeout():
    with pytest.raises(subprocess.TimeoutExpired):
        ProcessTimeout(0.01, "sleep", "10").run_sync()


@pytest.mark.asyncio
async def test_never_timeout(event_loop):
    process = ProcessTimeout(0.2, "cat", "/dev/urandom")
    process_status = asyncio.ensure_future(process.run(event_loop))
    await asyncio.sleep(0.01)
    assert not process_status.done(), "Process should be running, but got " + repr(
        process_status.result()
    )
    process_status.cancel()
