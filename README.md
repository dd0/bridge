# bridge

Markdown extension for texts related to contract bridge and
some half-finished system and convention descriptions.

# Syntax

The script does some preprocessing and passes the output to Markdown,
so full Markdown syntax is supported. Apart from that, there are several additions:

## Symbols

Suit symbols can be written as `!C`, `!D`, `!H` and `!S` (as in BBO
chat). These get converted to appropriate Unicode suit symbols and
coloured. For consistency, `!N` is also provided and is converted to
`N`.

Also, an en-dash can be written as `--`.

## Footnotes

Footnotes are expressed by placing the text where their number should
appear, wrapped in curly braces. For example:

    This is some text {Footnote goes here.} with a footnote.

Space between the previous word the opening curly brace is optional
and ignored. Full Markdown syntax is supported inside footnotes
(except nested footnotes).

# Usage

The `render.sh` script takes one argument, the (extended) Markdown
input file. It writes its output to stdout. Example usage:

    ./render.sh docs/system.md > docs/system.html