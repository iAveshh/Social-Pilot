---
name: save-to-icloud
description: Copy a finished reel's video and cover images from projects/<slug>/renders into iCloud Drive so they are on the user's phone for posting. Verifies each copy by hash and reports whether the iCloud client is actually running. Triggers include "save to icloud", "put the video on my phone", "sync the reel to icloud", "send the final to icloud".
---

# Save to iCloud

Move a finished reel and its covers off this machine and onto the user's phone,
where posting actually happens.

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File \
  .claude/skills/save-to-icloud/reference/publish-to-icloud.ps1 -Slug <slug>
```

Add `-Caption "<text>"` to drop the caption and hashtags in beside the video —
useful, because the caption is needed on the phone at the moment of posting and
retyping it from a laptop screen is the annoying part.

## What it ships

From `projects/<slug>/renders/` into
`~/iCloudDrive/optimalgradient/reels/<slug>/` — the account folder, then one
subfolder per project, named for the project itself:

| Source | Lands as | Required |
|---|---|---|
| `final.mp4` | `<slug>.mp4` | yes |
| `thumbnail.png` | `<slug>-cover.png` | yes |
| `thumbnail.4x5.png` | `<slug>-cover-4x5.png` | no |
| `thumbnail.1x1.png` | `<slug>-cover-1x1.png` | no |
| `-Caption` text | `<slug>-caption.txt` | no |

A missing cover is a **hard stop**, not a warning. Shipping a reel without one
is exactly what the cover step exists to prevent.

## Rules

**Write only into `optimalgradient/reels/<slug>/`.** iCloud Drive is the user's personal
document store — it holds ID scans, bank statements, employment paperwork. Never
enumerate it, never read from it, never write outside our own subfolder. If the
user asks for a different destination, take the path from them rather than going
looking for one.

**Copying into the folder is not the same as reaching iCloud.** The sync client
has to be running to upload. The script reports what it actually observed:

| `sync_state` | What to tell the user |
|---|---|
| `EXCLUDED_will_not_upload` | **Broken — see below.** Re-run after clearing the files |
| `client_running_upload_expected` | iCloud is running, upload should follow — worth confirming on the device |
| `staged_locally_client_not_running` | **Files are on disk but nothing has uploaded.** They need to start iCloud for Windows |
| `staged_locally_client_not_installed` | Staged at that path only |

Report the state you got. Do not say "saved to iCloud" when the client was not
running — say the files are staged and what has to happen next.

### The silent-exclusion trap (this has already bitten once)

**Files copied into a folder iCloud has not yet claimed are marked "Excluded
(not synced)" and never upload.** Nothing looks wrong: right size, matching
SHA-256, no error, client running, `sync_state: client_running_upload_expected`.
The files simply sit on disk forever while the phone shows an empty folder.

The tell is Explorer's **Availability status** column (shell detail index 312):

| Value | Meaning |
|---|---|
| `Excluded (not synced)` | **Broken.** Will never upload |
| `Syncing` | Uploading now |
| `Sync pending` | Queued — but if it never leaves this state, check the parents |
| `Available when online` / `Available on this device` | Synced |

**Check the whole parent chain, not just the files.** Exclusion is inherited: an
excluded intermediate folder silently condemns everything beneath it, and the
files inside will sit at `Sync pending` forever while looking individually fine.
That is exactly how this was first missed — the files were re-copied twice, and
went to `Sync pending` both times, because the `reels/` folder between them and
the claimed root was the excluded one. Read the availability of **every** level
before concluding anything.

Recovering an excluded folder means **deleting and recreating the folder
itself** — its exclusion does not clear on its own. Delete it, wait for iCloud
to claim the recreated one (it becomes `Available when online` within seconds),
then write into it.

Attributes corroborate it: a claimed file has `ReparsePoint` set (`0x420`); an
excluded one does not (`0x180020`).

The script now handles both halves — it waits for a newly created folder to be
claimed before writing into it, and it reads the availability of every file
afterwards, reporting `sync_state: EXCLUDED_will_not_upload` if any came back
excluded. **If you see that state, delete the files but keep the folders**
(iCloud will have claimed those by then) and re-run; copying into an
already-claimed folder is what fixes it.

**Windows cloud-file attributes alone cannot confirm an upload.** A freshly written
file in the iCloud folder reads `0x180020` (Archive + both PINNED and UNPINNED,
which together mean "not explicitly set"), and `OFFLINE`/`RECALL_ON_DATA_ACCESS`
stay clear because the bytes *are* local. That is true whether or not the file
has reached Apple's servers. There is no attribute to read for "uploaded", so do
not infer one — the strongest honest claim is "client running, upload expected,
confirm on the device".

**Every copy is hash-verified.** A truncated write into a cloud-backed folder is
silent, and the point of this step is that the file actually left the machine. A
hash mismatch throws rather than reporting success.

**Re-running is safe.** Same slug overwrites the same filenames in the same
folder, so a re-render republishes cleanly instead of piling up `-2` copies.

## This machine

- iCloud Drive: `C:\Users\avesh\iCloudDrive` (a cloud-files reparse point)
- Target: `iCloudDrive\optimalgradient\reels\<project>\`
- Client: iCloud for Windows `15.9.60.0`, installed as an Appx package
- **The client is not always running.** Check `sync_state` on every run rather
  than assuming — it has been observed both ways on this machine, and a copy
  made while it is stopped has not uploaded.

`iCloud Photos` is *not* configured as a synced folder here — there is only an
`iCloud Photos Archive` in the home directory, which is a leftover, not a live
sync target. Putting the video in Photos would be more convenient for posting,
so if the user wants that, they need to enable Photos sync in iCloud for
Windows first; then pass `-Root "$env:USERPROFILE\Pictures\iCloud Photos"`.

## Where it fits

Last step, after `ai-news-reel` or `paper-brief-reel` has delivered. Those
skills produce `renders/final.mp4` and `renders/thumbnail.png`; this one gets
them onto the phone. Posting to Instagram happens outside this repo either way.
