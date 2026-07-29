# MAKERTON · LIVE RELAY

### https://brightwindow.github.io/makerton-live-relay/

A phone camera on a laptop screen, live. **WebRTC peer-to-peer** — the video is
never stored on a server, and there is no backend to run.

```
index.html   the whole thing: viewer (big screen) and caster (phone) in one page
serve.py     local HTTPS server, only needed for the no-internet fallback
start.bat    double-click launcher for serve.py
cert.pem     self-signed certificate (generated on demand — delete to regenerate)
key.pem
```

---

## Use it

Nothing to install, no hotspot, no certificate warning. **Open the link.**

**1 · Open the link on whatever drives the big screen**
https://brightwindow.github.io/makerton-live-relay/
A ROOM code and a QR appear on the right. Press `F` for fullscreen.

**2 · Get the link onto the device that will film**
Scan the QR with the phone's camera, or press `Copy` and send the address by
message. Whoever opens that link becomes the caster.

**3 · Allow the camera → press `방송 시작` (Start)**
Video appears on the big screen and the tally lamp turns red.

The two devices **do not need to be on the same network.** Phone on cellular and
laptop on venue Wi-Fi is fine. Both just need internet.

> Any device can be the viewer. A tablet as the big screen with a laptop webcam
> as the caster works identically.

### Fresh room every time

Opening the page issues a new 6-character ROOM code, drawn with
`crypto.getRandomValues` from a 32-letter alphabet with the confusable
characters (`0/O`, `1/I`) removed. Several teams can rehearse simultaneously
without coordinating anything. If a code is already taken, the page reissues.

`New Session` gives you a new one on demand.

### Viewer keys

| Key | Action |
|---|---|
| `F` | Fullscreen the monitor |
| `M` | Mute / unmute |
| `S` | Save the current frame as PNG |

### If the venue has no internet at all

The original setup still works: turn on the phone's hotspot, join the laptop to
it, double-click `start.bat`, click through the `Your connection is not private`
warning (Advanced → Continue), then scan the QR. Use `start.bat 9000` to change
the port.

Note that this is **not** a fully offline mode — signalling and STUN still reach
external servers, so the phone needs data even in this configuration.

### When it does not work

| Symptom | Fix |
|---|---|
| Camera never turns on | Check the address is `https://`. Over `http://` it fails silently |
| `PC 화면을 찾을 수 없습니다` | Keep the viewer tab open, then press Start again on the phone |
| Picture frozen | `New Session` on the viewer, then reopen the link on the phone |
| Fails only on corporate/campus Wi-Fi | The firewall blocks UDP. Switch the phone to cellular |
| (local server) the QR link will not open | Run the `python serve.py 8443 <other-ip>` line printed in the console |

---

## Getting your team ready

**Nothing to install. No account. Just the link.**

**A 30-second rehearsal, alone**

1. Open the link on your laptop — ROOM code and QR on the right
2. Scan the QR with your phone → allow the camera → Start
3. Your phone's camera appears on the laptop. Press `F` to check it fullscreen

**Two minutes before you present**

1. Open the link on the machine wired to the projector, press `F`
2. Scan the QR to connect your phone
3. Turn off the phone's auto-lock; mute the viewer with `M` to avoid feedback

**To have someone else film** — press `Copy` and send them the address. They open
it and become the caster. No app.

**If it gets tangled** — `New Session` on the viewer. New room, start over.

> Only people **changing** the code need the repository. After a change,
> `/deploy` in Claude Code ships it to the live URL. Presenters never touch it.

---

## Pre-presentation checklist

- [ ] Confirm the venue has **Wi-Fi or cellular**. That is now the only requirement
- [ ] Open the link on the phone once and **allow the camera in advance** — doing
      it on stage costs a minute you do not have
- [ ] **Save the link on the phone** in case the QR will not scan on the day
- [ ] **Turn off auto-lock** and charge the phone
- [ ] If the venue speakers are live, **mute the viewer** — otherwise it howls
- [ ] Connect once **on the actual venue network**. A UDP-blocking firewall looks
      exactly like everything working until the moment it does not
- [ ] (local-server fallback only) **Unplug the laptop's ethernet.** With both a
      wired link and a hotspot connected, the machine can advertise the wrong
      address in the QR

---

## Design notes

**Transport** — with no backend, WebRTC is the only practical way to move live
video from a phone to a laptop. Signalling goes through the public PeerJS
server; the video itself travels directly between the two devices.

**Why HTTPS is mandatory** — `getUserMedia` only runs in a secure context. Open
the page over `http://192.168.x.x` and the camera fails silently. That is why
this is on GitHub Pages: already-trusted HTTPS, no certificate warning, and no
reason for the two devices to share a network. The self-signed certificate in
`serve.py` is kept only as the no-internet contingency.

**Connecting across networks** — STUN alone cannot always punch through both
NATs (corporate Wi-Fi, symmetric NAT), so a public TURN relay sits at the end of
the candidate list. Direct connections stay direct; TURN is used only when
nothing else works. It is a free shared relay with no bandwidth guarantee — the
trade deliberately favours connecting at all over connecting fast.

**Design** — the subject is *taking a signal and putting it on a large screen*,
so the visual language is a broadcast control room. Ink-slate ground, brass as
the identity accent, and **tally red reserved strictly for the ON AIR state**.
The standby screen is a desaturated SMPTE colour bar. The metrics panel
(resolution, framerate, bitrate, RTT, link quality) reads real values from
`RTCPeerConnection.getStats()`, and the timecode follows broadcast notation
(`HH:MM:SS:FF`).

Dark single theme on purpose — this is a video monitoring surface. Bahnschrift
for display and Cascadia Mono for figures, both shipped with Windows, so there
is no font-fallback surprise at the venue.

---

## Related

[brightwindow/makerton-skills](https://github.com/brightwindow/makerton-skills) —
a Claude Code plugin that walks people through using this, diagnoses failed
connections, and forks this page into their own account.

```bash
claude plugin marketplace add brightwindow/makerton-skills
claude plugin install makerton@makerton-skills
```
