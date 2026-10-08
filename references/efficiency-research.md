# Token efficiency and capability: research and measurements (webgrab, 2026-10-08)

Sources were read with webgrab: arXiv abstracts and Anthropic engineering posts. Each finding below
is a paraphrase of its source, not a quote.

## What the sources say

| Source | Finding | What it means for agent-board |
|---|---|---|
| Anthropic, "How we built our multi-agent research system" | Multi-agent runs use about 15x the tokens of a chat. Token usage alone explains about 80% of performance variance. Subagents should **store outputs in external systems and pass lightweight references**, which avoids the "game of telephone". | The board's value is cross-process durability. Post paths and commit hashes, never pasted artifacts. Inside one session, use SendMessage. |
| Anthropic, "Effective context engineering for AI agents" | "Just in time" context: keep lightweight identifiers and load data on demand. Subagents explore with tens of thousands of tokens but return a 1,000-2,000-token distillate. Structured note-taking is one of three core techniques. | Read the current state plus deltas, and fetch full text by number. Results are distilled records. |
| Anthropic, "Equipping agents with Agent Skills" | Progressive disclosure: name and description always loaded, SKILL.md on use, references only when needed. Scripts **run without being loaded into context**, and code is deterministic. | Keep SKILL.md lean and push detail into references/. All logic stays in scripts. |
| Blackboard MAS for information discovery (arXiv 2510.01285) | A central agent posts requests to a shared blackboard and capable agents **volunteer**. That gives 13-57% end-to-end gains, and the coordinator doesn't need to know each agent's expertise. | Add a request/volunteer flow (see the to-do list): requests become claimable work items. |
| LbMAS (arXiv 2507.01701) | Agents act on the blackboard's **current content** until consensus. It is competitive with state-of-the-art MAS and uses **fewer tokens**. | Read the state, not the log (`view.py digest`). |
| AgentPrune (arXiv 2410.02506) | Communication redundancy is real: pruning messages gives a 28-72% token reduction at equal quality, and the cost of comparable results fell from $43.7 to $5.6. | Per-agent filters (`--to-me`), incremental reads, and no broadcast chatter. |
| PACT (arXiv 2606.05304) | Free-form inter-agent text inflates tokens. Projecting each output into a **compact action-state record** before it enters shared history improves the cost/performance trade-off. Applied to coding harnesses: OpenHands resolves more at about 10% fewer tokens per resolve, and SWE-agent is neutral while halving input tokens. | Results and statuses as short action-state lines: what changed, commit, check, next. One line, with details behind a reference. |
| Optima (arXiv 2410.08115) | Training for efficiency reaches up to 2.8x performance with under 10% of the tokens, on tasks with heavy information exchange. | Training is out of scope here, but it confirms that brevity and effectiveness are compatible. |
| "The Cost of Consensus" (arXiv 2605.00914) | Homogeneous, unguided debate: majority adoption up to 85.5%, correct answers destabilized up to 70%, consensus discarding correct answers (up to 32 points). It costs 2.1-3.4x the tokens of isolated self-correction for equal or lower accuracy. | **Blind review** (`next` hides prior reviews), evidence-cited verdicts instead of votes, bounded rounds, and a lead who decides deadlocks. |
| M3MAD-Bench (arXiv 2601.02854) | Debate isn't uniformly effective. Collaborative methods are more robust than adversarial ones but cost more. | Reserve challenges for evidence (a failing input or file:line). `agree` is cheap and also cited. |

## Measured on a live production board (a 131-message copy, 2026-10-08)

| Read | Tokens (approx., chars/4) |
|---|---|
| `board.py read`, the full log, re-sent on every read | 6,940 |
| `view.py brief --all`, one line per message | 3,940 |
| `view.py digest`, the current state | **431** (16x less than a full read) |
| `view.py brief`, after one new message | **27** |

## Applied 2026-10-08

1. `view.py`: `digest`, `brief` with a per-agent cursor, and `show N`. Read-only, and outside the hash chain.
2. `review.py`: blind `next`, plus the regression review's seven fixes (authority re-checked in
   `_state`, untagged results counted, a required task-open, recorded overrules that `check` reds,
   min ≥ 1, no spin on an undeletable lock, no KINDS leak).
3. SKILL.md points every read at `view.py`.

## To do (ranked; items 1 and 4 change board.py or score.py, so land them only when no task is open)

1. **Action-state result schema** (PACT): `post --kind result` gains `--changed --commit --check --next`
   slots, and `view.py` prints them as one line. Gain: compact, comparable records.
2. **Request/volunteer flow** (blackboard): `view.py`/`review.py`-style `take N` on `request` messages,
   with O_EXCL like claims. Gain: no central assignment, and agents pick work by capability.
3. **SKILL.md diet:** move section 4 (scoring) and the review rules into references/, and keep a
   short SKILL.md with the command table. Gain: about 40-50% fewer tokens per agent load, paid by
   every teammate every session.
4. **Make `board.py read` incremental by default**, using the same cursor as `brief`. Gain: safety
   against agents that ignore SKILL.md.
5. **Heterogeneous challengers:** route challenges on hot files to a different model (Codex vs
   Claude). Homogeneous teams were where debate failed.
