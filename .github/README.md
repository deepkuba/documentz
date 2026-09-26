# Foundation CI

`workflows/foundation.yml` runs on every pull request and push to `main`. It uses
the exact runtime and package-manager versions from `toolchain.toml`, verifies
publisher checksums before unpacking downloaded tools, consumes both committed
lockfiles in frozen mode, and gives GitHub's token read-only repository access.

The workflow fails on Python or Portal formatting, linting, typing, tests, build,
dependency audit, secret scan, or either live PostgreSQL/pgvector migration
smoke. Database passwords are generated for the job, never printed, stored only
in `/tmp`, and removed with all Compose resources in an `always()` cleanup step.

An application image-build gate is intentionally absent. The repository does
not yet contain API, worker, or Portal runtime Dockerfiles, so a passing image
job would be a placeholder rather than supply-chain evidence. R01 introduces
the pinned non-root production images and their build/security gates; F05 should
not claim that later work early.
