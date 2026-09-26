# Development bootstrap

Foundation versions are pinned in [`toolchain.toml`](./toolchain.toml). F02 and F03 will add the Python and Portal manifests and their generated lockfiles; once those files exist, a clean checkout is bootstrapped as follows.

## Python workspace

Install uv 0.12.19 using a [verified official method](https://docs.astral.sh/uv/getting-started/installation/). Confirm the binary before allowing it to create or alter the environment, then run:

```sh
uv --version                 # must report uv 0.12.19
uv python install 3.14.7
uv sync --frozen
```

`uv sync --frozen` must consume the checked-in `uv.lock`; it must not resolve or modify dependencies in CI or deployment.

## Portal workspace

Install Node.js 24.21.0 from an [official signed distribution](https://nodejs.org/en/download/archive/v24), verify its published checksum/signature, enable Corepack, and activate the pinned package manager:

```sh
node --version               # must report v24.21.0
corepack enable
corepack prepare pnpm@12.5.1 --activate
pnpm --version               # must report 12.5.1
pnpm install --frozen-lockfile
```

`pnpm install --frozen-lockfile` must consume the checked-in `pnpm-lock.yaml`. Dependency updates are explicit reviewable changes to a manifest and lockfile, never an implicit bootstrap side effect.

## Canonical checks

F02 and F03 will bind these stable repository operations to executable commands without changing their names or meanings:

```text
format-check
lint
type-check
unit-test
portal-test
```
