# Development bootstrap

Foundation versions are pinned in [`toolchain.toml`](./toolchain.toml). The Python
and Portal manifests and generated lockfiles are committed; a clean checkout is
bootstrapped as follows.

## Python workspace

The reproducible bootstrap target is Linux x86-64. Download the exact official
uv release artifact and its publisher-provided checksum into a temporary
directory, verify it, and install it into the checkout-local `.tools` directory:

```sh
mkdir -p .tools/downloads .tools/uv-0.12.19
curl --fail --location --proto '=https' --tlsv1.2 \
  --output .tools/downloads/uv.tar.gz \
  https://github.com/astral-sh/uv/releases/download/0.12.19/uv-x86_64-unknown-linux-gnu.tar.gz
curl --fail --location --proto '=https' --tlsv1.2 \
  --output .tools/downloads/uv.tar.gz.sha256 \
  https://github.com/astral-sh/uv/releases/download/0.12.19/uv-x86_64-unknown-linux-gnu.tar.gz.sha256
(cd .tools/downloads && sed 's/  uv-x86_64-unknown-linux-gnu.tar.gz$/  uv.tar.gz/' uv.tar.gz.sha256 | sha256sum --check -)
tar --extract --gzip --file .tools/downloads/uv.tar.gz \
  --directory .tools/uv-0.12.19 --strip-components=1
export PATH="$PWD/.tools/uv-0.12.19:$PATH"
uv --version                 # must report uv 0.12.19
uv python install 3.14.7
uv sync --frozen --all-packages
```

`uv sync --frozen --all-packages` consumes the checked-in `uv.lock`; it must not resolve or modify dependencies in CI or deployment. The checkout-local Python workspace commands are:

```sh
make python_workspace_smoke
make format-check
make lint
make type-check
make unit-test
```

## Portal workspace

For Linux x86-64, download the exact Node.js archive and the release checksum
manifest, verify the selected line, and unpack it into `.tools`:

```sh
mkdir -p .tools/downloads .tools/node-v24.21.0
curl --fail --location --proto '=https' --tlsv1.2 \
  --output .tools/downloads/node.tar.xz \
  https://nodejs.org/dist/v24.21.0/node-v24.21.0-linux-x64.tar.xz
curl --fail --location --proto '=https' --tlsv1.2 \
  --output .tools/downloads/node-SHASUMS256.txt \
  https://nodejs.org/dist/v24.21.0/SHASUMS256.txt
(cd .tools/downloads && grep '  node-v24.21.0-linux-x64.tar.xz$' node-SHASUMS256.txt | sed 's/  node-v24.21.0-linux-x64.tar.xz$/  node.tar.xz/' | sha256sum --check -)
tar --extract --file .tools/downloads/node.tar.xz \
  --directory .tools/node-v24.21.0 --strip-components=1
export PATH="$PWD/.tools/node-v24.21.0/bin:$PATH"
node --version               # must report v24.21.0
corepack enable
corepack prepare pnpm@12.5.1 --activate
pnpm --version               # must report 12.5.1
pnpm install --frozen-lockfile
```

`pnpm install --frozen-lockfile` must consume the checked-in `pnpm-lock.yaml`. Dependency updates are explicit reviewable changes to a manifest and lockfile, never an implicit bootstrap side effect.

Other CPU architectures require the matching official artifact and checksum and
are not yet a supported bootstrap target. Future separately verified platform
recipes must not change the pinned runtime versions.

## Canonical checks

F02 binds the Python operations below as Make targets. F03 exposes the Portal
operations as root package scripts without changing these names or meanings:

```text
format-check
lint
type-check
unit-test
portal-test
portal-build
```

The Portal commands are exposed as root package scripts. TypeScript 7.0.2 is the
application compiler. Because typescript-eslint does not yet consume the
TypeScript 7 compiler API, the isolated `tools/portal-lint` workspace supplies
TypeScript 6.0.3 only to ESLint; it does not compile Portal source or relax the
pinned application toolchain.
