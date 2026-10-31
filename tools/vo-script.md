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

# Claude's lines (voice: Reed, pitch 1.0, speed 1.0; pilot phraseology)

Saved as `site/media/vo/<name>.m4a`; each plays after the narration on its panel. Tail numbers in the phonetic alphabet, digits one at a time with "niner", times as zero-nine-hundred, matching the Clearance Delivery Trainer.

## claude-ch3-5 — ch3-5 · Connect, Test
The ForeFlight connection is live. You have forty-four saved aircraft, and November two one one whiskey papa, your Diamond D A forty, is the primary. One thing to look at: November four five one romeo kilo appears twice, with different settings.

## claude-ch4-1 — ch4-1 · Logbook, Totals
Here's your logbook by year. Three thousand two hundred fifty hours since twenty thirteen, with seven hundred twenty-two approaches.

## claude-ch5-2 — ch5-2 · One trip, Research
Here are six airports along the Oregon coast, with runway lengths, one hundred low led prices (spelled "led" so Reed says it like the metal), and notes from other pilots. Thursday and Friday morning look best. Strattus (spelled so Reed uses a short "a") moves in Friday afternoon, ceilings near three hundred feet, and rain arrives Sunday night.

## claude-ch5-3a — ch5-3 · One trip, Plan
If you'd like, I can save the Friday zero niner hundred, Sunday zero eight hundred pair as a Plane W X trip, or draft the flight in ForeFlight with a fuel stop. Redding would be the natural midpoint.

## claude-ch5-3b — ch5-3 · One trip, Plan (after "Yes, pls.")
Both are set up. Four flights are now in ForeFlight, in November two one one whiskey papa, with your weight and balance profile.

## claude-ch5-4 — ch5-4 · One trip, Stay & eat
Three places to stay in Nye Beach, five places to eat, and five things to see. Save the aquarium for a foggy morning, and the headlands for when it clears.

## claude-ch5-5 — ch5-5 · One trip, Verify
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

## wayne-ch5-3 — One trip, Plan
Yes, pls.

## wayne-ch5-4 — One trip, Stay & eat
For the overnights in Newport, please find three possible Airbnbs, a couple of eateries for lunch and dinner, and maybe some sights to see or things to do.

---

# Order on each panel

- Connect, Test: narration, then your prompt, then Claude
- Logbook, Totals; One trip, Research; One trip, Stay & eat: your prompt, Claude, narration
- One trip, Check: your prompt, narration
- One trip, Plan: Claude's offer, your "Yes, pls.", Claude's "Both are set up", narration
- One trip, Verify: Claude, narration
- Every other panel: narration only

Raw recordings go in `tools/vo-raw/`; `python3 tools/build_vo.py` builds `site/media/vo/` and the file list.
