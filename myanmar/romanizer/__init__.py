# romanizer.py - transliteration module
# coding: utf-8
# The MIT License (MIT)
# Copyright (c) 2018 Thura Hlaing

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from myanmar.encodings import UnicodeEncoding
from myanmar.language import PhonemicSyllableBreak

__author__ = 'Thura Hlaing'
__email__ = 'trhura@gmail.com'
__version__ = '1.1.0'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2018 Thura Hlaing'

from .ipa import IPA  # noqa
from .mlc import MLC  # noqa
from .bgp_pgcn import BGN_PCGN  # noqa
from .parse import parse, decode


def romanize(string, system):
    """
    Transliterate Burmese text with latin letters.

    >>> romanize("ကွန်ပျူတာ", IPA)
    'kʊ̀ɴpjùtà'
    >>> romanize("ပဒေသရာဇာ", MLC)
    'padezarājā'
    >>> romanize("ဘင်္ဂလားအော်", BGN_PCGN)
    'bin-gala-aw'
    """
    try:
        string_ = string

        table = system.table
        table_ = system.table_
        romans = []

        special_char = ['~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`',
                        '}', '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/']

        syllables = list(PhonemicSyllableBreak(string, UnicodeEncoding()))
        syllables = [i['syllable'] for i in syllables]

        trans = []

        for syl in syllables:
            if syl in table:
                trans.append(table[syl])
            elif syl in table_:
                trans.append(table_[syl])
            elif syl in special_char:
                trans.append(syl)
            else:
                morpho = parse(syl)
                trans_ = []
                chars = decode(morpho)

                for i in chars:
                    if i in table_:
                        trans_.append(table_[i])
                    elif i in table:
                        trans_.append(table[i])
                    else:
                        return False
                trans_ = "".join(trans_)
                trans.append(trans_)

        if len(syllables) == len(trans):
            return " ".join(trans)
        else:
            return False
    except:
        return False


if __name__ == "__main__":
    print(romanize("မောင်ခန့်ကိုကို", BGN_PCGN))
