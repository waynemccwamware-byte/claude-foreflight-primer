#!/bin/bash
# Makes Claude's voice-over files for the Claude + ForeFlight Primer (voice: Reed) on a Mac.
# Run:  curl -fsSL https://raw.githubusercontent.com/waynemccwamware-byte/claude-foreflight-primer/main/tools/make-claude-vo.sh | bash
set -u
DIR="$HOME/Desktop/claude-vo"; mkdir -p "$DIR"; cd "$DIR" || exit 1
V="Reed (English (US))"
if ! say -v "$V" -o /tmp/vtest.aiff "test" </dev/null 2>/dev/null; then V="Reed"; fi
echo "Voice: $V"
make() {
  say -v "$V" -o "$1.aiff" "$2" </dev/null && afconvert -f m4af -d aac "$1.aiff" "$1.m4a" </dev/null && rm -f "$1.aiff" && echo "made  $1.m4a" || echo "FAILED $1"
}
make claude-ch3-5 "The ForeFlight connection is live. You have forty-four saved aircraft, and November two one one whiskey papa, your Diamond D A forty, is the primary. One thing to look at: November four five one romeo kilo appears twice, with different settings."
make claude-ch4-1 "Here's your logbook by year. Three thousand two hundred fifty hours since twenty thirteen, with seven hundred twenty-two approaches."
make claude-ch5-2 "Here are six airports along the Oregon coast, with runway lengths, one hundred low led prices, and notes from other pilots. Thursday and Friday morning look best. Strattus moves in Friday afternoon, ceilings near three hundred feet, and rain arrives Sunday night."
make claude-ch5-3a "If you'd like, I can save the Friday zero niner hundred, Sunday zero eight hundred pair as a Plane W X trip, or draft the flight in ForeFlight with a fuel stop. Redding would be the natural midpoint."
make claude-ch5-3b "Both are set up. Four flights are now in ForeFlight, in November two one one whiskey papa, with your weight and balance profile."
make claude-ch5-4 "Three places to stay in Nye Beach, five places to eat, and five things to see. Save the aquarium for a foggy morning, and the headlands for when it clears."
make claude-ch5-5 "Two things to look at. The sources disagree on Thursday's ceiling at Newport. And with the fuel stop at Redding, you'd arrive just as the strattus moves in. I can move both Friday legs earlier."
echo "Done: $(ls "$DIR"/*.m4a | wc -l | tr -d " ") files in $DIR"
open "$DIR"
