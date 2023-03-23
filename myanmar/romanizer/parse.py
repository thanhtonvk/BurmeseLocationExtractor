NON_INDIVIDUAL = [
    'င်္', 'ိ', 'ီ', 'ု', 'ူ', 'ဲ', 'ဳ', 'ဴ', 'ဵ', 'ံ', '့', '္',
    '္က', '္ခ', '္ဂ', '္ဃ', '္စ', '္ဆ', '္ဇ', '္ဈ', '္ဋ', '္ဌ', '္ဍ', '္ဏ',
    '္တ', '္ထ', '္ဒ', '္ဓ', '္န', '္ပ', '္ဖ', '္ဗ', '္ဘ', '္မ', '္ယ', '္ရ',
    '္လ', '္သ', '်', 'ျ', 'ျွ', 'ျွှ', 'ျှ', 'ြ', 'ြွ', 'ွ', 'ွှ', 'ှ',
    'ှု', 'ှူ', 'ၘ', 'ၙ', 'ၞ', 'ၟ', 'ၠ', 'ၱ', 'ၲ', 'ၳ', 'ၴ', 'ႂ',
    'ႅ', 'ႆ', 'ႍ', 'ႝ'
]

RIGHT_INDIVIDUAL = [
    'ါ', 'ာ', 'း', 'ၖ', 'ၗ', 'ၢ', 'ၣ', 'ၤ', 'ၧ', 'ၨ', 'ၩ',
    'ၪ', 'ၫ', 'ၬ', 'ၭ', 'ႃ', 'ႇ', 'ႈ', 'ႉ', 'ႊ', 'ႋ', 'ႌ',
    'ႏ', 'ႛ', 'ႜ'
]

LEFT_INDIVIDUAL = ['ေ', 'ႄ']

LEFT_TAGS = ['eVowel']

RIGHT_TAGS = ['aaVowel', 'visarga']


from myanmar.encodings import UnicodeEncoding
from myanmar.language import MorphoSyllableBreak
from .bgp_pgcn import BGN_PCGN


def parse(text):
    total_syllables = list(MorphoSyllableBreak(text, UnicodeEncoding()))
    total_symbols = list()
    
    for idx, syllable in enumerate(total_syllables):
        total_symbols_ = []
        tags = list(syllable.keys())
        if len(tags) > 1:
            left_pos, cen_pos, right_pos = str(), list(), str()
            for tag in tags[1:]:
                if tag in LEFT_TAGS:
                    left_pos = syllable[tag]
                elif tag in RIGHT_TAGS:
                    right_pos = syllable[tag]
                else:
                    if syllable[tag] == "း" or syllable[tag] == "့" or syllable[tag] == "္":
                        continue
                    else:
                        cen_pos.append(syllable[tag])

            is_str = False
            if ''.join(cen_pos) in BGN_PCGN.table or ''.join(cen_pos) in BGN_PCGN.table_:
                cen_pos = ''.join(cen_pos)
                is_str = True

            if left_pos != '':
                total_symbols_.append(left_pos)
            if is_str:
                total_symbols_.append(cen_pos)
            else:
                for i in cen_pos:
                    total_symbols_.append(i)
            if right_pos != '':
                total_symbols_.append(right_pos)


            total_symbols.append(total_symbols_)
        else:
            if syllable['syllable'] == "း" or syllable['syllable'] == "့" or syllable['syllable'] == "္":
                continue
            else:
                total_symbols.append(syllable['syllable'])
    if len(total_symbols) > 0:
        break_loop = 0
        while True:
            counter = 0
            for i, s in enumerate(total_symbols):
                if s in NON_INDIVIDUAL:
                    try:
                        total_symbols = \
                            total_symbols[:i-1] + \
                            [''.join([total_symbols[i-1], total_symbols[i]])] + \
                            total_symbols[i+1:]
                        break
                    except:
                        total_symbols[i-1] = "".join(total_symbols[i-1])
                        total_symbols = \
                            total_symbols[:i-1] + \
                            [''.join([total_symbols[i-1], total_symbols[i]])] + \
                            total_symbols[i+1:]
                        break
                else:
                    counter += 1
            break_loop += 1
            if counter == len(total_symbols) or break_loop == 20:
                break
    
    tmp = []
    for i in total_symbols:
        if isinstance(i, list):
            for j in i:
                tmp.append(j)
        else:
            tmp.append(i)

    return tmp

def decode(chars):
    i = 0
    while True:
        if chars[i] in LEFT_INDIVIDUAL:
            chars[i], chars[i+1] = chars[i+1], chars[i]
            i += 2
        else:
            i += 1
        if i == len(chars):
            break

    return chars



