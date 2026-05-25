# FreeMIDIChords — Competitions & Awards

Track of submissions, drafts, and materials for each competition or award.

---

## 2026 MIDI Innovation Awards

**Organizer:** MIDI Association — [midi.org/innovation-awards](https://midi.org/innovation-awards)
**Status:** In progress

### Entrant's name
Antonio Ortega

### MIDI 2.0 / MIDI-CI support
No. The app uses MIDI 1.0 via `mido` 1.3.2 and `python-rtmidi` 1.5.8.

### Word product pitch *(25 words max)*
Free, open-source music theory suite. Connect any MIDI keyboard to detect chords, visualize intervals, and explore the circle of fifths — web, mobile, and desktop.

### Short description
FreeMIDIChords is a free, open-source music theory tool suite that works with any MIDI keyboard. Connect a controller and the app detects chords and intervals in real time, displaying them on staff notation, a piano keyboard, and an interactive circle of fifths. It also generates chords on demand, plays them back through MIDI or built-in audio, and includes scales, a metronome, and a tuner. Available as a web app (with Web MIDI API support), iOS/Android app, and desktop app for Mac and Windows — with no subscriptions, no accounts, and no paywalls.

### How is it innovative
FreeMIDIChords innovates by making MIDI-powered music theory accessible without cost or setup barriers. Most theory tools are either expensive, require software installation, or lack MIDI integration. FreeMIDIChords combines real-time MIDI input detection, chord generation with MIDI output, and rich visualization — staff notation, piano keyboard, and circle of fifths — in a single free tool that runs in the browser via the Web MIDI API, requiring no installation.

Its bidirectional MIDI approach is distinctive: the same app listens to what you play and identifies it, or takes a chord you select and performs it — turning a MIDI keyboard into both input and output for music theory exploration.

The cross-platform reach (web, iOS, Android, desktop) through a unified feature set also sets it apart, ensuring musicians can learn and practice on any device, with or without a MIDI controller.

### Most inspiring use
A self-taught musician sits at a secondhand keyboard with no music teacher and no budget for software. They play a chord they heard in a song — and FreeMIDIChords instantly names it, shows it on the staff, and places it on the circle of fifths. They move to the next chord, and the next, and slowly the song they've been trying to learn reveals its harmonic structure.

This is the use case FreeMIDIChords was built for: removing the wall between curiosity and understanding. Music theory has historically been taught in classrooms or through expensive software. FreeMIDIChords puts that knowledge directly in the hands of anyone with a MIDI keyboard and a browser — no teacher, no subscription, no barrier.

### How does it connect with other MIDI devices or software
FreeMIDIChords connects with MIDI devices and software through two layers:

**Hardware input:** Any class-compliant MIDI keyboard or controller can be connected. On the web app, the browser's Web MIDI API detects available MIDI ports and listens for incoming note and velocity data in real time. On the desktop app, connection is handled via python-rtmidi, which interfaces with the system's MIDI drivers on both Mac and Windows.

**Audio output:** The desktop app can send generated chords back out through a MIDI output port, allowing FreeMIDIChords to trigger sounds on an external synthesizer, sound module, or DAW instrument — using the connected device not just as input but as a voice.

No pairing, configuration, or driver installation is required beyond what the OS already provides. Plug in a controller, open the app, and it appears in the device list automatically.

### Commercialization plans
FreeMIDIChords will remain completely free and open source. The project sustains itself through voluntary donations from users who find value in the tool. No subscription tiers, no premium features, and no advertising are planned.

Growth will focus on expanding platform reach and deepening MIDI integration, funded by community support rather than commercialization.

### Expansion plans
**Deeper MIDI integration:** The next major milestone is adopting MIDI 2.0, including Universal MIDI Packets (UMP) and higher-resolution velocity and pitch data. This would allow FreeMIDIChords to reflect nuanced playing dynamics more accurately in both chord detection and audio playback, and position the tool to work natively with the growing ecosystem of MIDI 2.0 compatible controllers and DAWs.

**Platform expansion:** The mobile app (iOS and Android) currently has a subset of the web and desktop features. Planned work brings full parity — MIDI input via Bluetooth LE MIDI, complete circle of fifths, and interval tools.

**Educational layer:** Guided exercises where the user is prompted to play specific chords or intervals and receives real-time feedback through MIDI input, turning the tool into an interactive practice environment.

---

---

## Product Hunt

**URL:** [producthunt.com](https://www.producthunt.com)
**Status:** Programado — lanzamiento el 2026-05-22

### Name
FreeMIDIChords

### Tagline
Free music theory tools for any MIDI keyboard — web & mobile

### Tags
Music · Education · Open Source

### Description
**FreeMIDIChords** is a free, open-source music theory tool suite that works with any MIDI keyboard — no installation required for the web version, no subscriptions, no paywalls.

I'm a computer science teacher and lifelong music hobbyist. I built this because I couldn't find a single free tool that let students plug in a MIDI keyboard and immediately start understanding what they were playing. So I made one.

**What it does:**
- Plug in any MIDI keyboard and it detects chords and intervals in real time
- Visualizes them on staff notation, a piano keyboard, and an interactive circle of fifths
- Works in reverse too — pick a chord and hear it played back through MIDI or built-in audio
- Includes scales and metronome

**Available everywhere:**
- Web app (Web MIDI API — no install)
- iOS & Android
- Desktop for Mac and Windows

The goal is simple: music theory should be accessible to anyone with a keyboard and a browser. No teacher required, no software to buy.

### First comment
Hey Product Hunt! 👋

I'm Antonio, a CS teacher and music hobbyist from Spain. I built FreeMIDIChords because I wanted my students to be able to plug in a MIDI keyboard and instantly understand what they were playing — no expensive software, no signup, no friction.

What started as a classroom tool grew into a full music theory suite: chord and interval detection, circle of fifths, chord generation with MIDI output, scales, metronome — available on the web, iOS, Android, and desktop.

The web app uses the Web MIDI API, so it works directly in the browser with any class-compliant MIDI controller. No install needed.

Everything is completely free and open source. Always will be.

I'd love to hear from musicians, teachers, or anyone learning music theory — what features would make this more useful for you?

### Shoutouts
- **Cloudflare** — Workers for the web backend. Free tier, zero cold starts, static site + API in one place.
- **Flutter** — single codebase for iOS and Android with native performance.
- **GitHub** — where open-source lives. Issues, CI/CD, and community in one place.

### Other fields
- **Funding:** Bootstrapped
- **Why this idea:** Built the tools I needed to study music myself, then made them free for everyone.
- **Why the right founder:** CS teacher + musician. Understands both how people learn and how to build cross-platform tools.

---

---

## Global Tech Awards — Music Technology

**URL:** [globaltechaward.com](https://www.globaltechaward.com/category/music-technology-musictech-awards)
**Status:** En progreso

### Short Description *(250 chars)*
Free, open-source music theory suite for any MIDI keyboard. Detect chords and intervals in real time, explore the circle of fifths, generate chords with MIDI output, and practice scales — on web, iOS, Android, and desktop. No subscription, always free.

### Entry Detail
FreeMIDIChords is a free, open-source music theory tool suite built around MIDI connectivity. Any class-compliant MIDI keyboard becomes an interactive learning instrument: play a chord and the app identifies it instantly, displaying it on staff notation, a piano keyboard, and an interactive circle of fifths. The flow works in reverse too — select a chord and the app generates and plays it back through MIDI output or built-in audio.

The tool covers the full spectrum of music theory fundamentals: chord and interval detection, chord generation, circle of fifths navigation, scale exploration, and metronome. It runs as a web app (via the Web MIDI API, no installation required), an iOS and Android app, and a native desktop app for Mac and Windows — all free, with no accounts, no subscriptions, and no paywalls.

FreeMIDIChords deserves recognition in the Music Technology category because it solves a real access problem: quality MIDI-integrated music theory tools have historically required expensive software or hardware ecosystems. This project removes that barrier entirely. It was built by a computer science teacher who needed it for the classroom, grew into a full cross-platform suite, and was released as open source so anyone — student, hobbyist, or professional — can use, inspect, and contribute to it.

The combination of genuine MIDI integration, cross-platform reach, and a strict commitment to remaining free makes FreeMIDIChords a distinctive entry in the music technology space.

---

## Other competitions (pending)

<!-- Add future competition entries below following the same structure -->
