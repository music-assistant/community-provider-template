# Music Assistant community provider template

A provider adds something to [Music Assistant](https://music-assistant.io): a music source, support
for a kind of player, a metadata source or a plugin. A **community provider** lives in its own
repository, like this one, with its own documentation, support and releases. Music Assistant
servers install it from the **community catalog**, a list the Music Assistant project keeps in the
[registry](https://github.com/music-assistant/community-catalog). Being listed means the provider
passed the checks and a person admitted what it does; it does not mean the project reviewed,
tested or supports it. Users install community providers at their own risk.

This template holds one small music source, `example_music`, that plays a few test tones without
an account or network. It comes with a test that runs it in a real server, a development container
and CI. Click **Use this template** on GitHub to start your own.

> **Not there yet.** Parts of the community catalog are still being built. Everything in this
> repository that depends on them is marked *Not final* where it appears:
> - no Music Assistant release has the community catalog: the server is pinned to a development
>   commit (see [Keep up with the server](#keep-up-with-the-server));
> - the test fixture in `tests/conftest.py` moves into the server package;
> - the registry does not take admissions, check releases or run its nightly test, and the
>   catalog checks that CI calls (`catalog` in `.github/workflows/ci.yml`) fail until a nightly
>   build of the server has the community catalog.

## The rules

The catalog declines a provider at admission, and blocks it when it is found later, for:

- music the user has no right to: getting around an account, a subscription tier or a region, or
  a source that offers music without the permission of its rights holders;
- getting around copy protection;
- downloading or exporting music to keep it (a cache used for playback is fine);
- harmful behaviour: sending the user's data elsewhere, loading code from somewhere else while it
  runs, or doing things its description does not mention;
- a provider whose only job is to load other providers or lists of sources from third parties.

A small audience, an unofficial API used with the user's own account, reading a service's web
pages, and free public content in the quality a service offers without a subscription are all
fine, at the user's own risk.

A provider that talks to a music service also behaves as a good client of it: put a throttler in
front of its API, cache what repeats instead of asking again, back off when the service asks you
to wait, and never walk the service's catalogue for one user action (requests per album, track or
page of a whole discography). Paging through the user's own library is fine. The
[developer guide of the server](https://github.com/music-assistant/server/blob/dev/DEVELOPMENT.md)
explains these rules with the helpers that implement them.

What a release has to look like:

- the provider is in a folder named after its `domain`, the internal name in `manifest.json`;
  a domain the server already uses is refused;
- the release is a GitHub release whose tag is the version, such as `v1.2.0`;
- `requirements` in `manifest.json` are package names with version specifiers, such as
  `aiohttp-retry==2.9.1`: no URLs, markers or options;
- `manifest.json` is plain JSON: no `NaN` or `Infinity`, and no key twice;
- `icon.svg` is at most 5 KB and only draws (the
  [icon rules](https://github.com/music-assistant/community-catalog#the-icon)).

## From template to a running provider

You need [Docker](https://www.docker.com/products/docker-desktop/) and
[VS Code](https://code.visualstudio.com/) with the Dev Containers extension. Nothing else: no
Python, no ffmpeg, on Windows, macOS or Linux.

1. Click **Use this template**, create your repository and open it in VS Code.
2. Choose **Reopen in Container** when VS Code offers it. The first build downloads the server and
   takes a few minutes.
3. Give the provider its own domain, in the terminal of VS Code (lower case letters, digits and
   underscores):

       uv run python scripts/rename.py my_service

   This renames the folder and sets the domain in `manifest.json`, the tests and the CI. A test
   fails when these disagree, so a rename by hand is caught.
4. In `my_service/manifest.json` and `strings.json`, set the name and description, your GitHub
   handle in `codeowners` and the address of your documentation. Add `"support_url"` when you take
   questions somewhere else than the issues of your repository.
5. Run the task **Run Music Assistant** (Terminal > Run Task), or `scripts/run.sh` in the
   terminal. The server starts in dev mode and loads the provider from this repository. Press F5
   instead to run it in the debugger.
6. Open <http://localhost:8095>, create the first user, and add your provider under Settings >
   Music sources. Its tracks show up in the library; play one in the web player of the app.

Speakers in your network usually cannot reach a server inside the container; use the web player
there. After a change to the code, restart the server. Its settings and library stay in `.data/`;
delete that folder to start over.

Without the container, on macOS or Linux with [uv](https://docs.astral.sh/uv/) and ffmpeg 8 or
newer: `uv sync`, then `scripts/run.sh`.

## Write your provider

| Path | What it is |
|---|---|
| `example_music/__init__.py` | The provider: `setup()` and the provider class. |
| `example_music/manifest.json` | Its type, domain, name, maintainers and requirements. |
| `example_music/strings.json` | Its texts in English: the name, the description and the labels of its settings. Translations go in `translations/<language>.json` next to it. |
| `example_music/icon.svg` | Its icon. Optional: `icon_dark.svg` and `icon_monochrome.svg`. |
| `tests/` | The tests. |
| `scripts/run.sh` | Starts the server with the provider. |
| `.devcontainer/`, `.vscode/` | The development container, the task and the debugger. |

The comments in `example_music/__init__.py` show where the real work goes. The server has an
annotated template for each type of provider (`_demo_music_provider`, `_demo_player_provider`,
`_demo_plugin_provider` in
[`music_assistant/providers`](https://github.com/music-assistant/server/tree/dev/music_assistant/providers))
that lists every method you can implement, and the built-in providers there are full examples.
When the user has to enter something to set up the provider, such as a login, add a
`setup_flow.py`: see [provider setup flows](https://developers.music-assistant.io/setup-flows/).

## Where your code runs

Once installed, the provider runs inside the user's Music Assistant server, in the same process as
everything else. That has consequences:

- **Never write into the provider folder.** The server checks the folder against the content hash
  of the release and replaces it when it differs. Settings go through the server: options are
  config entries (`get_config_entries`), what the setup flow collects is stored for you, values
  that repeat go in the server's cache (`@use_cache`, `self.mass.cache`), and files go in a folder
  of your own under `self.mass.storage_path` or `self.mass.cache_path`.
- **Never block.** Music Assistant is async; wrap a blocking library call in `asyncio.to_thread`.
- **Your requirements are installed next to the server's own packages** and never replace one. A
  provider whose requirements clash with the server, or with another installed community
  provider, is not loaded. Use the versions the server already has where you can.
- **A server that cannot load your provider says why** in its settings, and keeps the settings of
  its users.

## Test

    uv run pytest

`tests/test_files.py` checks the manifest, the texts, the requirements and the icon without a
server. `tests/test_provider.py` boots a real server with this repository as its local provider
folder, adds the provider and asks it for a track. Add your own tests next to them; the `mass`
fixture gives a started server. Lint and type check run on every commit once
`uv run pre-commit install` has run (the container does that), and in CI.

*Not final:* the `mass` fixture in `tests/conftest.py` is going to ship with the server package;
this file then goes.

## Keep up with the server

The server version you develop against is set in **one place**: the `music-assistant` line in
`pyproject.toml`. *Not final:* until a release has the community catalog it points at a development
commit; it then points at a release tag, such as `@2.11.0`. To move to a newer server, change that
line and run `uv lock`. The three packages listed under it are needed by the server but not yet
listed by its package; they go once it lists them.

The registry tests the newest version of every listed provider against each supported server
line (the current stable release, the beta and the nightly) every night. When your provider stops
loading on one of them, servers of that line fall back to the last version that still passed, and
you get an issue on your repository with the output. With a beta of several weeks you usually know
well before a stable release.

## Release

Publish a GitHub release whose tag is the new version, such as `v1.2.0`. That is all: the registry
picks up new releases every night, runs its checks and offers the version to the servers it passed
for. When it fails a check, you get an issue with the reason. Pre-releases are ignored; to offer a
version to the nightly only, release it normally and it ends up where it passes.

## Join the catalog

*Not final:* the registry does not take admissions. Once it does, you open a pull request on the
registry that adds your provider; its README tells how. It needs a public repository with an open
source licence, a release that passes the checks, and a free domain. A person then decides once
about what the provider does, against the rules above. After that every release is checked and
offered without anyone looking at it.

## Licence

Apache-2.0, like Music Assistant. You may choose another open source licence for your provider.
