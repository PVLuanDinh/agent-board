# Contributing

1. Fork, branch, make your change.
2. Run the self-check and confirm the last line starts with `ALL GREEN`:

   ```bash
   python scripts/selfcheck.py
   ```
3. Open a PR describing what changed and why.

Rules:

- **Stdlib only.** Python 3.10+, no third-party dependencies.
- **Every new guard or gate ships with a reachable red case in `scripts/selfcheck.py`**: a case that triggers the guard and is shown to fail the score or be refused. A guard nobody has seen fire is not evidence.
- Changes to `scripts/board.py` or `scripts/score.py` invalidate the self-hash pinned by any already-open scoring task. Mention this in the PR. Prefer a new script (as `view.py` and `review.py` are) when you can.
- Keep the README "Limits" section honest: do not claim prevention where the scripts only detect.

## Reporting issues

Use the issue templates. Include OS, Python version, the command you ran, and the output.

## Using Claude Code

`CLAUDE.md` has the commands and architecture. Run `claude` in the repo root.
