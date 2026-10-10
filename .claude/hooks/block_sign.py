"""PreToolUse hook: refuse each shell command of an agent that sends the add-on to addons.mozilla.org.

A signature makes a lasting record in the account of the user, and a listed one makes a public page.
The user signs in a terminal outside Claude Code. Exit code 2 makes Claude Code refuse the tool call.
"""

import json
import re
import sys

# A program name counts only where a command starts, so a commit message that names a sign command passes.
COMMAND_START = r"(?:^|[;&|(]|\n)\s*(?:\w+=\S*\s+)*"
SIGN_COMMAND = re.compile(
    COMMAND_START
    + r"(?:"
    r"just\b[^;&|\n]*\bsign(?:-unlisted)?\b"  # just [options] sign | sign-unlisted
    r"|npm\b[^;&|\n]*\brun\s+sign(?::listed)?\b"  # npm [options] run sign | sign:listed
    r"|(?:npx|node)\b[^;&|\n]*\bweb-ext\S*\s[^;&|\n]*\bsign\b"  # npx web-ext@x sign, node .../web-ext.js sign
    r"|web-ext\b[^;&|\n]*\bsign\b"  # web-ext sign
    r")",
    re.IGNORECASE,
)


def main():
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    if SIGN_COMMAND.search(command):
        print(
            "Blocked: this command sends the add-on to addons.mozilla.org. "
            "Only the user runs it, in a terminal outside Claude Code, after the approval of each value. "
            "Read .claude/memory/amo-signing.md.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
