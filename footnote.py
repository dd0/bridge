# Parse an .md file and convert footnotes to the correct form
# (superscript index with hover-text and footer).

import sys
import re

last_index = 0
notes = []


def make_footnote(match):
    global last_index, notes
    last_index += 1
    notes.append(match.group(1))

    res = '<a class="footnote" name="footnote%d">' \
          '<sup>%d</sup><span>%s</span></a>'

    return res % (last_index, last_index, match.group(1))


def main():
    text = ''.join(sys.stdin.readlines())
    res = re.sub(' ?{([^{]*)}', make_footnote, text)

    note = '<div><a href="#footnote%d"><sup>%d</sup></a>: %s</div>'
    footer = '\n'.join([note % (i + 1, i + 1, s) for i, s in
                        enumerate(notes)])

    print(res)
    if last_index > 0:
        print('\n- - -\n<h3>Footnotes:</h3>\n')
        print(footer)

if __name__ == '__main__':
    main()
