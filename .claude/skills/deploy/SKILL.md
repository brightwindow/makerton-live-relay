---
name: deploy
description: Publish MAKERTON LIVE RELAY to its live GitHub Pages URL. Use when asked to deploy, publish, ship, push live, or update the hosted page — "배포", "올려", "반영", "라이브 반영". Commits the working tree, pushes to brightwindow/makerton-live-relay, waits for the Pages build, and verifies the change is actually live.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
---

# Deploy MAKERTON LIVE RELAY

Live URL: **https://brightwindow.github.io/makerton-live-relay/**
Repo: `brightwindow/makerton-live-relay` (public, Pages from `main` branch root)

The site is plain static files on GitHub Pages. Deploying means: commit → push →
wait for the Pages build → confirm the live URL actually serves the change.

## Never deploy these

`.gitignore` already excludes them. **Do not add them back, do not `git add -f`
them, and do not mention them in commit messages.**

| File | Why |
|---|---|
| `how-it-works.html` | 내부 이해용 문서. 배포 대상이 아니다. |
| `how-it-works.pdf` | 같음 |
| `MAKERTON_원리설명서.pdf` | 같음 — 위 HTML 을 인쇄한 것. 이름이 바뀌어도 이 문서 계열은 전부 제외한다. |
| `cert.pem`, `key.pem` | 로컬 자체 서명 인증서. 공개 저장소에 개인 키를 올리지 않는다. |

The rule is the document, not the filename. If a new PDF or HTML rendering of
the 원리설명서 shows up under any name, add it to `.gitignore` and keep it out.

Before committing, run `git status --short` and confirm none of these appear as
staged. If one does, unstage it (`git rm --cached <file>`) rather than committing
"just this once".

## Steps

**1 · Check what is actually changing**

```bash
git status --short
git diff --stat
```

If nothing is modified, say so and stop — there is nothing to deploy.

**2 · Commit**

Use a heredoc, not `-m` with a PowerShell-style `@'...'@` (this repo's shell is
Git Bash; the PowerShell here-string syntax gets taken literally).

```bash
git -c user.name="brightwindow" -c user.email="changhui8220@gmail.com" commit -F - <<'MSG'
<subject line: what changed, imperative mood>

<body: why, if it isn't obvious from the subject>

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

**3 · Push**

```bash
git push origin main
```

**4 · Wait for the Pages build**

A push does not mean the page is live — the build takes 20–60 seconds. Poll
until `built`, then check the URL:

```bash
for i in $(seq 1 12); do
  s=$(gh api repos/brightwindow/makerton-live-relay/pages --jq .status 2>/dev/null)
  echo "$i: $s"
  [ "$s" = "built" ] && break
  sleep 10
done
curl -s -o /dev/null -w "HTTP %{http_code}\n" https://brightwindow.github.io/makerton-live-relay/
```

**5 · Verify the change is really live**

Do not stop at HTTP 200 — that only proves *a* page is there. Grep the deployed
file for something specific to this change:

```bash
curl -s https://brightwindow.github.io/makerton-live-relay/ | grep -c '<distinctive string from the edit>'
```

Also confirm the excluded doc is not reachable:

```bash
curl -s -o /dev/null -w "how-it-works: HTTP %{http_code}\n" \
  https://brightwindow.github.io/makerton-live-relay/how-it-works.html
```

Expect `404`. A `200` means it got committed by mistake — remove it from the
repo and history before continuing.

## Report back

State the live URL, what changed, and what was verified. Be explicit that a real
phone-to-PC connection was **not** tested unless it actually was — a served page
is not a working WebRTC session.

## Notes

- GitHub Pages serves from `main` root, so `index.html` is the site root. The
  caster link the viewer generates is `location.origin + location.pathname`, so
  it inherits the deployed URL automatically — no hardcoded address to update.
- Pages responses are CDN-cached. If a verified-correct deploy still looks stale
  in a browser, hard-reload; `curl` is the source of truth.
- `serve.py` / `start.bat` are the offline fallback path, not part of the hosted
  site. They ship in the repo for people cloning it, and changing them does not
  require a deploy verification pass.
