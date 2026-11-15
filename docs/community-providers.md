Building a provider
==================================

A provider adds something to Music Assistant: a music source, support for a kind of player, a
metadata source or a plugin. A provider can live in two places, and what each asks of you differs.

## Two places

### In the server repository: a built-in provider

A built-in provider ships with every Music Assistant server, and the team keeps it working through
every change to the server. Because the team supports it for years, the server repository asks:

- demand you can show: users who want it, beyond yourself;
- a pull request on the user documentation that describes it;
- code that follows the code standards of the server, with tests;
- a named maintainer (you) who follows up on issues and on changes to the server.

You work in a fork of the server, and a maintainer reviews the new provider against the
[usage policy](https://github.com/music-assistant/.github/blob/main/USAGE_POLICY.md). After that,
you merge changes to your own provider yourself through the review bot. A built-in provider that
has had no active maintainer for a long time may be moved to the community catalog. The
[developer guide of the server](https://github.com/music-assistant/server/blob/dev/DEVELOPMENT.md)
has the details.

### In your own repository: a community provider

A community provider lives in your own repository, with your own documentation, support and
releases. Servers install it from the community catalog, a list the project keeps in the
[registry](https://github.com/music-assistant/community-catalog). Users see the community catalog
only after an administrator enables it and accepts that everything in it is used at their own
risk.

The catalog asks less than the server repository, and the project supports nothing in it:

- a public repository with an open source licence;
- releases that pass the automated checks;
- a domain that no built-in provider uses;
- a provider that crosses none of the red lines below.

A person decides once, at admission, about what the provider does. The code is not reviewed, and
every later release reaches users without anyone looking at it.

## The red lines

The catalog declines a provider at admission, and blocks it when it is found later, for:

- music the user has no right to: getting around an account, a subscription tier or a region, or
  a source that offers music without the permission of its rights holders;
- getting around copy protection;
- downloading or exporting music to keep it (a cache used for playback is fine);
- harmful behaviour: sending the user's data elsewhere, loading code from somewhere else while it
  runs, or doing things its description does not mention;
- a provider whose only job is to load other providers or lists of sources from third parties.

Allowed, at the user's own risk: a small audience, an unofficial API used with the user's own
account, reading a service's web pages, free public content in the quality a service offers
without a subscription, and code that would not pass a review for the server.

A blocked provider is not loaded by any server; its users keep their settings and library. A
blocked version is skipped the same way.

## The template

The [community provider template](https://github.com/music-assistant/community-provider-template)
is where a community provider starts. It holds one small music source, a test that runs it in a
real server, a development container and CI. Its README takes you from **Use this template** to a
provider running in a server in a few minutes, with Docker as the only requirement, on Windows,
macOS or Linux.

The template pins the server version you develop against, at a release tag or a commit, and
installs it from its source, which gives you type checking, completion in your editor and the test
fixture.

What a release has to look like:

- the provider is in a folder named after its domain;
- the release is a GitHub release whose tag is the version, such as `v1.2.0`;
- the requirements are package names with version specifiers: no URLs, markers or options;
- the manifest is plain JSON;
- the icon is an SVG of at most 5 KB that only draws.

Once installed, a provider runs inside the user's server. It never writes into its own folder:
the server checks that folder against the release and replaces it when it differs. Settings,
cached values and files go through the server. Its requirements are installed next to the
server's own packages and never replace one; a provider whose requirements clash is not loaded.

## Testing

### In your repository

`uv run pytest` runs the tests of the template: quick checks of the manifest, the texts, the
requirements and the icon, and a test that boots a real server with your repository as its local
provider folder in dev mode. The fixture comes with the server:
`pytest_plugins = ["music_assistant.testing"]` in `tests/conftest.py` gives a fixture `mass`, a
started server in dev mode with your repository as its local provider folder, kept off the
network. It needs pytest-asyncio with `asyncio_mode = "auto"`, and next to the server the
requirements of its Sendspin provider (`aiosendspin[server]` and `av`, at the versions in the
server's `music_assistant/providers/sendspin/manifest.json`), which the server starts at every
boot. The template has all of this in place.

`scripts/run.sh`, or the **Run Music Assistant** task in VS Code, starts a server in dev mode that
loads your provider, so you can try it in the app. Outside the container this is:

    PYTHONDEVMODE=1 python -m music_assistant --dev-providers-dir /path/to/your/repository

Only a server in dev mode loads providers from a local folder.

### On your pull requests

CI runs the lint, the type check and your tests, and calls a workflow of the registry that runs the
same checks the catalog runs on a release: the manifest, the requirements against a server line,
and loading the provider in the server image of that line.

## What the nightly test reports

The registry checks every new release, and every night it tests the newest version of each listed
provider again against the current server of every supported server line: the stable release, the
beta and the nightly.

- A version that passes for a line is offered to the servers of that line.
- A version that fails, or that stops loading on a line, is not offered there. Servers of that line
  fall back to the newest earlier version that still passes, or no longer offer the provider.
- You get an issue on your repository with the reason and the output of the failing check, or on
  the registry when your repository has no issues.

With a beta that runs for several weeks, you usually know about a problem well before a stable
release reaches your users. To support the stable release and follow the nightly at the same time,
release two versions; each one is offered where it passes.
