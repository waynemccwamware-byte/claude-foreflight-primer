# Claude + ForeFlight Primer — voice-over script

One mp3 per panel. Save each as the file name shown, then they go in `site/media/vo/`. The page plays a file when "Read aloud" is on and falls back to the browser voice for any panel without one.

## ch0.mp3 — Start

Your ForeFlight account already holds years of flying: your logbook, your aircraft, your saved flights. Connect ForeFlight to Claude, and you can ask Claude about all of that in plain English, and have Claude build flights right back into ForeFlight.

## ch1.mp3 — Why

Three reasons to connect. See everywhere your logbook has taken you. Research a trip in one conversation. And when you like the plan, have Claude put the flights straight into ForeFlight.

## ch2.mp3 — Before you start

You'll need an individual ForeFlight plan, Starter, Essential or Premium, and a Claude account on any plan. ForeFlight calls the connector a preview, so expect ForeFlight to add and change features.

## ch3-1.mp3 — Connect, 1 · Find ForeFlight

In any Claude chat, tap plus, then Connectors, then Manage connectors. Open the Discover tab, search for ForeFlight, and select ForeFlight Mobile.

## ch3-2.mp3 — Connect, 2 · Connect

Selecting ForeFlight Mobile opens its page in Claude. Click Connect, and Claude hands you over to ForeFlight to sign in.

## ch3-3.mp3 — Connect, 3 · Sign in to ForeFlight

ForeFlight asks you to sign in with your ForeFlight account, if you aren't already signed in, and to approve access for Claude.

## ch3-4.mp3 — Connect, 4 · Switch on

In a chat, tap plus, then Connectors, and check that ForeFlight Mobile's switch is on. If it's off, Claude can't see your ForeFlight data in that chat.

## ch3-5.mp3 — Connect, 5 · Test

Ask Claude to try the connection. Claude should come back with your aircraft from ForeFlight. If Claude does, you're connected.

## ch4-1.mp3 — Logbook, A · Totals

Fourteen years of logbook, summarized by Claude from one question.

## ch4-2.mp3 — Logbook, B · Map

I asked Claude for every airport in my ForeFlight logbook, departures, destinations and route waypoints, and Claude built this map. Here it zooms to Newport, Oregon, then to San Pedro de la Cueva in Sonora, Mexico.

## ch5-1.mp3 — One trip, 1 · Check

First, a quick check. Claude found my 44 saved aircraft, and flagged an airplane that appears twice. That's a cleanup I'd never have spotted.

## ch5-2.mp3 — One trip, 2 · Research

Claude pulled runway, fuel price and pilot notes for six coast airports, then the forecast trend. Good Thursday and Friday morning, stratus Friday afternoon, and rain by Sunday night.

## ch5-3.mp3 — One trip, 3 · Plan

I also had Claude score departure windows with another connector, PlaneWX. Friday morning won. Then I said yes, please, and four flights showed up in ForeFlight, in my airplane, with my weight and balance profile.

## ch5-4.mp3 — One trip, 4 · Stay & eat

Then the fun part. One more sentence, and Claude came back with three places to stay, five places to eat, and five things to see in Newport, arranged around the forecast.

## ch5-5.mp3 — One trip, 5 · Verify

The best part: Claude told me where its sources disagreed, and that my Friday arrival was cutting things close. Claude is a research partner, not a briefing. I'm still pilot in command.

## ch6.mp3 — Good habits

Use Claude like a sharp copilot doing the research. Claude is fast, and usually right. But Claude isn't a briefing, and Claude doesn't sign your logbook. You do.

## ch7.mp3 — Wrap-up

That's the whole trip: four prompts, about sixty words from me, and Claude did the legwork across ForeFlight and PlaneWX. The value? Your time.

---

# Claude's lines (voice: Reed; pilot phraseology)

Claude's voice speaks only what appears in a Claude chat bubble on screen. Saved as `tools/vo-raw/<name>.m4a`; `tools/build_vo.py` adds the ding, bubble voice and send.

## claude-ch5-1 — One trip, Check (end)
Want to try a real one, such as a currency check, or the Santa Barbara mee-tar and taff?

## claude-ch5-2 — One trip, Research (end)
Want me to run Plane W X departure windows for Santa Barbara to Newport on Thursday and Friday, with a Sunday return?

## claude-ch5-3a — One trip, Plan
If you'd like, I can save the Friday zero niner hundred, Sunday zero eight hundred pair as a Plane W X trip, or draft the flight in ForeFlight with a fuel stop. Redding would be the natural midpoint.

## claude-ch5-5 — One trip, Verify (end)
Moving leg one to zero seven hundred gets you there around thirteen hundred. I can shift both Friday legs if you want.

---

# Wayne's typed prompts (spoken as chat bubbles)

Record these like the narration, as you'd type them to Claude. Name each file as shown (.m4a or .mp3) and send them; they get the ding, bubble voice and send sound when committed, and play before Claude answers.

## wayne-ch3-5 — Connect, Test
Let's try the connection to ForeFlight.

## wayne-ch4-1 — Logbook, Totals
Summarize my logbook by year: total hours, cross-country, and approaches.

## wayne-ch5-1 — One trip, Check
Let's try the connection to ForeFlight.

## wayne-ch5-2 — One trip, Research
I'm thinking about a weekend trip to the Pacific coast of Oregon sometime in the next few weeks. What do things look like in terms of airports and possible weather?

## wayne-ch5-2b — One trip, Research (answering Claude's question)
Sure.

## wayne-ch5-3 — One trip, Plan
Yes, pls.

## wayne-ch5-4 — One trip, Stay & eat
For the overnights in Newport, please find three possible Airbnbs, a couple of eateries for lunch and dinner, and maybe some sights to see or things to do.

---

# Order on each panel

- Connect, Test: narration, your prompt
- Logbook, Totals; One trip, Stay & eat: your prompt, narration
- One trip, Check: your prompt, Claude's question, narration
- One trip, Research: your prompt, Claude's question, your "Sure.", narration
- One trip, Plan: Claude's offer, your "Yes, pls.", narration
- One trip, Verify: Claude's offer, narration
- Every other panel: narration only

Raw recordings go in `tools/vo-raw/`; `python3 tools/build_vo.py` builds `site/media/vo/` and the file list.
