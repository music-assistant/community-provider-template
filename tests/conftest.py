"""
A server to test the provider against.

NOT FINAL: the Music Assistant server package is going to ship this fixture itself; this file
then goes. Until then it holds the smallest fixture that boots a real server for a test.
"""

from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

from music_assistant.mass import MusicAssistant
from tests import REPOSITORY

LOOPBACK = "127.0.0.1"


@pytest.fixture
async def mass(tmp_path: Path) -> AsyncGenerator[MusicAssistant]:
    """Return a started server in dev mode, with this repository as its local provider folder."""
    (tmp_path / "data").mkdir()
    (tmp_path / "cache").mkdir()
    server = MusicAssistant(
        str(tmp_path / "data"), str(tmp_path / "cache"), dev_providers_path=str(REPOSITORY)
    )
    server.dev_mode = True
    zeroconf = MagicMock(spec=AsyncZeroconf)
    zeroconf.zeroconf = MagicMock()
    zeroconf.zeroconf.cache.cache = {}
    with (
        # free ports on loopback only, never the ports of a server that may run on this machine
        patch("music_assistant.controllers.webserver.controller.DEFAULT_SERVER_PORT", 0),
        patch("music_assistant.controllers.webserver.controller.DEFAULT_HOST", LOOPBACK),
        patch("music_assistant.controllers.webserver.controller.SENDSPIN_SERVER_PORT", 0),
        patch("music_assistant.controllers.streams.controller.DEFAULT_PORT", 0),
        patch("music_assistant.controllers.streams.controller.DEFAULT_HOST", LOOPBACK),
        patch("music_assistant.providers.sendspin.provider.SENDSPIN_SERVER_PORT", 0),
        # nothing announced on or discovered from the network
        patch(
            "music_assistant.controllers.discovery.controller.AsyncZeroconf", return_value=zeroconf
        ),
        patch("music_assistant.controllers.discovery.controller.AsyncServiceBrowser"),
        patch("aiosendspin.server.server.AsyncZeroconf", return_value=zeroconf),
        patch(
            "aiosendspin.server.server.AsyncServiceBrowser",
            return_value=MagicMock(spec=AsyncServiceBrowser),
        ),
        # a test needs no ffmpeg; playback through a player does
        patch("music_assistant.controllers.streams.controller.check_ffmpeg_version", AsyncMock()),
        # no players of this machine and no library sync in the middle of a test
        patch("music_assistant.mass.DEFAULT_PROVIDERS", ()),
        patch("music_assistant.controllers.music.controller.INITIAL_SYNC_DELAY", None),
    ):
        try:
            await server.start()
            # the server loads the providers of the local folder in a task of its own
            for task in list(server._tracked_tasks.values()):  # noqa: SLF001
                if task.get_name() == "community_catalog_start":
                    await task
            yield server
        finally:
            await server.stop()
