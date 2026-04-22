# Git Conventions

## Commits

- Always use atomic commits
- Author: kyu-dev `100522666+kyu-dev@users.noreply.github.com`
- Co-Author: kyudev-bot `278458691+kyudev-bot@users.noreply.github.com`

Always include in every commit message:

```
Co-Authored-By: kyudev-bot <278458691+kyudev-bot@users.noreply.github.com>
```

Commit format:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <imperative summary>

Co-Authored-By: kyudev-bot <278458691+kyudev-bot@users.noreply.github.com>
EOF
)"
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
**Scopes:** `agent`, `pipeline`, `graph`, `eval`, `ci`

## GitHub Operations

- Always use `gh` CLI for remote GitHub operations: create PRs, list issues, add comments, reviews, etc.
- Use `git` CLI only for local operations (`commit`, `push`, `diff`, `log`, `status`)

## Pull Requests

- Author: `kyudev-bot` — Reviewer: `kyu-dev` (always assign)
- Never develop on `main` — always create a feature branch first
- PR title follows the same `<type>(<scope>): <summary>` convention