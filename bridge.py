# Pandoc plugin for typesetting bridge-related documents

import pandocfilters as pf
import re


def is_bidding(blocks):
    for block in blocks:
        data = pf.stringify(block[0])
        if re.match('.*![CDHSN].*--.*', data):
            return True
    return False


prev_key = ''  # worst hack ever


def bidding_divs(key, value, fmt, meta):
    global prev_key
    if key == 'BulletList' and prev_key != pf.stringify(value[0]):
        prev_key = pf.stringify(value[0])
        if is_bidding(value):
            attr = ('', ['bids'], [])
            return pf.Div(attr, [pf.BulletList(value)])
    return None


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

            res = ' '.join(s + (h if len(h) > 0 else '--')
                           for s, h in zip(suit, hold))

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
        if len(hands) == 0:
            return None
                
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
        attr = ('', ['hands'], [])

        return pf.Div(attr, [table])
    return None


def reshape(n, data, fill=None):
    res = []
    line = []
    for x in data:
        line.append(x)
        if len(line) == n:
            res.append(line)
            line = []
    if len(line) > 0:
        while(len(line) < n):
            line.append(fill)
        res.append(line)
    return res


def block_bids(key, value, fmt, meta):
    def disp_bid(b):
        if b == 'p':
            return 'pass'
        elif b[0] in '1234567' and b[1] in 'CDHS':
            return b[0] + '!' + b[1:]
        else:
            return b

    if key == 'CodeBlock':
        m = re.match('(NS|EW|all)(/[NSEW])?: (.*)', value[1])
        if m is None:
            return None

        players = m.group(1)
        def_mod = {'NS': 1, 'EW': 0, 'all': -1}

        raw_bids = m.group(3)
        auction_done = raw_bids[-1] != '-'
        if not auction_done:
            raw_bids = raw_bids[:-1]
        bids = raw_bids.split('-')

        first_player = 1 if players == 'EW' else 0
        if m.group(2):
            first_player = 'NESW'.find(m.group(2)[1])
        player = first_player
        res = []
    
        for bid in bids:
            defence = bid[0] == '(' and bid[-1] == ')'

            if player % 2 == def_mod[players] and not defence:
                res.append('p')
                player = (player + 1) % 4

            if defence:
                res.append(bid[1:-1])
            else:
                res.append(bid)
            player = (player + 1) % 4

        if auction_done:
            while len(res) < 3 or res[-3:].count('p') != 3:
                res.append('p')

        res = [disp_bid(b) for b in res]

        empty_cell = [pf.Plain([])]
        def make_cell(r):
            return [pf.Plain([pf.Str(r)])]
        flat_cells = [empty_cell] * first_player + [make_cell(r) for r in res]
        cells = reshape(4, flat_cells, empty_cell)

        names = [make_cell(x) for x in ['North', 'East', 'South', 'West']]

        AlignCenter = {'t': 'AlignCenter'}
        table = pf.Table([], [AlignCenter] * 4, [0] * 4, names, cells)
        attr = ('', ['bidding'], [])
        
        return pf.Div(attr, [table])

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
    pf.toJSONFilters([bidding_divs,
                      inline_hands,
                      block_hands,
                      block_bids,
                      suit_symbols,
                      html_dashes])

# pandoc src\defence.md --filter bridge.py -H bridge-header.tex -o defence.pdf
# cat src\onent.md | sed "s/--/\&mdash;/g" | pandoc --filter bridge.py -o onent.htm -H base.html
