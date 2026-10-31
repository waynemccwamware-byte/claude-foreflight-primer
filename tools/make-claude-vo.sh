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
make claude-ch5-1 "Want to try a real one, such as a currency check, or the Santa Barbara mee-tar and taff?"
make claude-ch5-2 "Want me to run Plane W X departure windows for Santa Barbara to Newport on Thursday and Friday, with a Sunday return?"
make claude-ch5-3a "If you'd like, I can save the Friday zero niner hundred, Sunday zero eight hundred pair as a Plane W X trip, or draft the flight in ForeFlight with a fuel stop. Redding would be the natural midpoint."
make claude-ch5-5 "Moving leg one to zero seven hundred gets you there around thirteen hundred. I can shift both Friday legs if you want."
echo "Done: $(ls "$DIR"/*.m4a | wc -l | tr -d " ") files in $DIR"
open "$DIR"
