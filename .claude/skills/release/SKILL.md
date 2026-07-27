---
name: release
description: Cut a GitHub release for root-law-scraper, including the point-form "What to change for existing setups" list that tells knowledge-base users which files to re-upload. Use this whenever the user asks to release, tag, ship, publish, or cut a version of this repo, or asks what changed for existing setups — and also right after merging a PR that touches uploaded-files/, since those changes are what releases exist to communicate.
---

# Cutting a release

Consumers of this repo upload `uploaded-files/*` into a Claude.ai Project as knowledge. They cannot diff a tag. The release notes are the only way they learn which files to replace, so the notes are the deliverable — the tag is just the anchor.

## 1. Establish what actually changed

```bash
git fetch -q origin --tags
LAST=$(git describe --tags --abbrev=0 origin/main)
git log --oneline $LAST..origin/main
git diff --stat $LAST..origin/main -- uploaded-files/
```

Work from this diff, not from memory of the session. A release often covers earlier merges that were never shipped, and those need to appear in the notes too.

## 2. Decide whether to release at all

Release when `uploaded-files/` gained or changed content a consumer would act on.

Do not release for whitespace, formatting, or wording-only edits. Let them ride along with the next content release — the user has explicitly declined releases for these. Never move or re-cut an existing tag to pick up cosmetic drift; publish forward instead.

Version bump: new content (a table, a field, more nodes) is a minor bump. Corrections to existing content are a patch bump.

## 3. Write the notes

Lead with what was added or fixed and why it wasn't there before. Then the section below, which is the part consumers actually act on.

Keep prose plain and unwrapped — one line per paragraph, no hard wrapping at ~80 columns, no bold/emoji emphasis, and don't restate in prose what a table already shows.

### The "What to change for existing setups" section

Always include it, always in point form, always with one bullet per file in `uploaded-files/` so a reader can see at a glance that a file was considered and needs nothing. Derive it from the step 1 diff — never assume a file changed.

Use this shape:

```markdown
## What to change for existing setups

- **Re-upload `root_law_schema.md`** — delete the old copy from your Project knowledge first, then upload the new one
- **Leave `root_law.jsonl` alone** — unchanged
- **Leave `root_cards.json` alone** — unchanged
- **Leave `root_cards_schema.md` alone** — unchanged
- **Queries and greps** — nothing breaks; no IDs, field names, or values changed
- **Re-scraping** — not needed; `scrape_law.py` and `build_cards.py` are unchanged
```

The last two bullets matter as much as the file list. Telling people their existing greps still work, and that they do not need to re-run a scraper, is what stops a docs-only release from being treated as a data migration.

Adjust honestly when the data did change: name the changed IDs or fields, say plainly that queries touching them need updating, and say whether re-scraping reproduces the release or not.

State the unchanged files positively rather than silently omitting them. A consumer deciding what to re-upload reads absence as ambiguity and re-uploads everything, which costs them a knowledge refresh for nothing.

Close with the compare link:

```markdown
**Full changelog:** https://github.com/theepicflyer/claude-root-project/compare/<prev>...<new>
```

## 4. Publish

```bash
gh release create vX.Y.Z --target main --title "vX.Y.Z — <short summary>" --notes-file <path>
```

Write the notes to a scratch file outside the repo and pass `--notes-file`; release notes are not committed. Pass `--target main`, not a short SHA — GitHub rejects abbreviated commitish values with a confusing "tag_name is not a valid tag" error.

## 5. Verify before reporting success

```bash
gh release view vX.Y.Z --json tagName,isDraft,targetCommitish
git fetch -q --tags origin && git rev-list -n1 vX.Y.Z   # must equal origin/main head
```

Confirm it is not a draft and the tag resolves to the current `main` head. Report the URL and what you verified.

## Merging

Merging is the user's call. Open the PR and wait for them to say so — do not merge as part of cutting a release.
