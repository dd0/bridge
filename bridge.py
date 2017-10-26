# Pandoc plugin for typesetting bridge-related documents

import pandocfilters as pf
import re


def suit_symbols(key, value, fmt, meta):
    if key == 'Str':
        abbrevs = ['!C', '!D', '!H', '!S', '!N']
        orig_value = value

        if fmt != 'latex':
            suit_html = ['<font color=green>&clubs;</font>',
                         '<font color=orange>&diams;</font>',
                         '<font color=red>&hearts;</font>',
                         '<font color=blue>&spades;</font>',
                         'N']
            suit_other = ['C', 'D', 'H', 'S', 'N']

            suit_symbols = suit_html if fmt == 'html' else suit_other

            for (abbrev, symbol) in zip(abbrevs, suit_symbols):
                value = value.replace(abbrev, symbol)

        else:
            # LaTeX needs special handling (for mbox)
            value = value.replace('!N', 'N')
            suit = ['\\clubs{\\1}{\\2}',
                    '\\diamonds{\\1}{\\2}',
                    '\\hearts{\\1}{\\2}',
                    '\\spades{\\1}{\\2}']

            for (abbrev, symbol) in zip(abbrevs, suit):
                value = re.sub('([a-zA-Z0-9]*)%s([a-zA-Z0-9]*)' % abbrev,
                               symbol, value)

        if (fmt == 'html' or fmt == 'latex') and value != orig_value:
            return pf.RawInline(fmt, value)
        return pf.Str(value)
    else:
        return None


# Expand hands in inline code-blocks
def inline_hands(key, value, fmt, meta):
    if key == 'Code':
        hand = value[1]
        if hand.count(',') == 3 and len(hand) == 16:
            hold = hand.split(',')
            suit = ['!S', '!H', '!D', '!C']

            res = ' '.join(s + h for s, h in zip(suit, hold))

            return pf.Str(res)

    return None


def hand_diagram(hand):
    void = '--'
    hold = [x if len(x) > 0 else void for x in hand.split(',')]
    suit = ['!S', '!H', '!D', '!C']

    suits = [pf.Str(s + h) for s, h in zip(suit, hold)]
    res = sum(([x, pf.LineBreak()] for x in suits), [])[:-1]

    return pf.Plain(res)


def block_hands(key, value, fmt, meta):
    if key == 'CodeBlock':
        lines = value[1].split('\n')
        hands = {}

        for line in lines:
            m = re.match('([NSEW]): (.*)', line)
            if m:
                hands[m.group(1)] = m.group(2)

        empty_cell = [pf.Plain([])]

        diagram = [[empty_cell] * 3 for _ in range(3)]
        pos = {'N': (0, 1), 'S': (2, 1), 'E': (1, 2), 'W': (1, 0)}
        for (player, hand) in hands.items():
            i, j = pos[player]
            diagram[i][j] = [hand_diagram(hand)]

        AlignLeft = {'t': 'AlignLeft'}
        table = pf.Table([],
                         [AlignLeft, AlignLeft, AlignLeft],
                         [0, 0, 0],
                         [],
                         diagram)
        return table
    return None


# Interpret -- as an em-dash in html, unless it is between two words
# (without blanks), in which case it is interpreted as an en-dash
def html_dashes(key, value, fmt, meta):
    def fix_dash(s):
        s = re.sub('([^ ])--([^ ])', '\\1&ndash;\\2', s)
        s = s.replace('--', '&mdash;')
        return s

    if key == 'Str' and fmt == 'html':
        return pf.RawInline(fmt, fix_dash(value))
    elif key == 'RawInline' and fmt == 'html':
        return pf.RawInline(value[0], fix_dash(value[1]))
    else:
        return None

if __name__ == '__main__':
    pf.toJSONFilters([inline_hands,
                      block_hands,
                      suit_symbols,
                      html_dashes])

# pandoc src\defence.md --filter bridge.py -H bridge-header.tex -o defence.pdf
# cat src\onent.md | sed "s/--/\&mdash;/g" | pandoc --filter bridge.py -o onent.htm -H base.html
