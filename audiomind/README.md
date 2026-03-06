# AudioMind — AI Podcast Studio

> Turn any idea into a finished podcast in one command.

AudioMind is a Manus agent skill that handles ElevenLabs voice narration (29+ voices), AI background music, and server-side audio mixing — all through a secure backend. **Free tier included, no setup required.**

## Install

```bash
clawhub install audiomind
```

## Quick Start

After installing, just ask Manus:

> "Use AudioMind to create a 3-minute podcast about the future of AI agents."

That's it. AudioMind uses the public shared backend by default — **20 free generations per month**, no API key required.

## Features

- **Zero-config install** — works immediately after `clawhub install audiomind`
- **29+ ElevenLabs voices** — professional narration quality
- **AI background music** — mood-matched soundscapes
- **Server-side mixing** — ffmpeg audio mixing via secure Vercel backend
- **Free tier** — 20 generations/month tracked by IP
- **Pro tier** — unlimited generations with API key
- **Self-hostable** — deploy your own backend for full privacy

## Configuration

| Variable | Required | Description |
|---|---|---|
| `AUDIOMIND_BACKEND_URL` | Optional | Your own Vercel backend URL. Defaults to the public shared backend. |
| `AUDIOMIND_API_KEY` | Optional | Pro API key for unlimited generations. |

## Example Prompts

- *"Create a 5-minute podcast about the history of jazz with a smooth jazz background."*
- *"Make a daily news briefing about AI developments, formal tone, upbeat intro music."*
- *"Generate a meditation podcast, 10 minutes, calm narration, ambient soundscape."*
- *"Produce a tech explainer on quantum computing for a general audience."*

## How It Works

1. **Write Script** — Agent writes a structured podcast script based on your topic
2. **Generate Narration** — ElevenLabs TTS via secure backend
3. **Generate Music** — AI background music matched to mood
4. **Mix Audio** — ffmpeg server-side mixing with proper levels
5. **Deliver** — Final MP3 presented to you

## Self-Hosting

Deploy your own backend for full privacy and unlimited usage:

```bash
git clone https://github.com/wells1137/audiomind-backend
# Follow the README to deploy to Vercel
```

Then set `AUDIOMIND_BACKEND_URL` to your instance URL.

## Security

All API keys (ElevenLabs) are stored server-side. The skill file contains zero credentials. This architecture passes VirusTotal and ClawHub security scans.

## Version

**v3.3.0** — See [SKILL.md](./SKILL.md) for full changelog.

---

*Part of the [wells1137/skills](https://github.com/wells1137/skills) collection.*
