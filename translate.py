import json
import re
import traceback
from difflib import SequenceMatcher

import pyidaungsu as pds

from myanmar.language import ismyanmar
from myanmar.language import ismydigit
from myanmar.romanizer import BGN_PCGN
from myanmar.romanizer import romanize

special_char = ['~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}',
                '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/']
from googletrans import Translator

translator = Translator()


def googleTranslate(text):
    result = translator.translate(text, dest="my", src='my')
    return result.pronunciation


def similar_string(a, b):
    return SequenceMatcher(None, a, b).ratio()


def check_digit(text):
    for c in text:
        if ismydigit(c) or c in special_char:
            continue
        else:
            return False
    return True


def check_chr_in_dict(text, dict):
    res = []
    for i in text:
        if i in dict:
            res.append(dict[i])
        else:
            return False
    return "".join(res)


def translate2eng_back(text, field_name):
    dict_bu_eng_no = {
        "မှ": "from",
        "လဲလှယ်": "change",
        "မိတ္တူ": "copy"
    }

    confidence_similar = 0.8

    alphabet = json.load(
        open('myanmar/data/bgn-pcgn.json', encoding="utf-8")
    )

    region = json.load(
        open('dictionary_backside/region.json', encoding="utf-8")
    )
    township = json.load(
        open('dictionary_backside/township.json', encoding="utf-8")
    )
    village = json.load(
        open('dictionary_backside/village.json', encoding="utf-8")
    )
    street = json.load(
        open('dictionary_backside/street_parse.json', encoding="utf-8")
    )
    address = {**region, **township, **village, **street}

    rank_dict = {
        "ကျေးရွာ": "village",
        "မြို့နယ်": "township",
        "မြို့": "city",
        "အုပ်စု": "group",
        "ရပ်ကွက်": "ward",
        "လမ်း": "street",
        "ရွာ": "village"
    }
    num_dict = {
        "၀": "0",
        "၁": "1",
        "၂": "2",
        "၃": "3",
        "၄": "4",
        "၅": "5",
        "၆": "6",
        "၇": "7",
        "၈": "8",
        "၉": "9",
    }

    special_char_dict = {i: i for i in special_char}

    employment_json = json.load(
        open('dictionary_backside/employment.json', encoding="utf-8")
    )
    no_json = json.load(
        open('dictionary_backside/no.json', encoding="utf-8")
    )

    comma = "၊"
    text = text.replace(comma, ",")

    try:
        if field_name == "address":
            output = []
            text_split_comma = [i.strip() for i in text.split(",")]
            address = {**address, **rank_dict, **num_dict, **special_char_dict, **alphabet}

            for text in text_split_comma:
                result = []
                texts = text.split(" ")
                tmp = []
                for text in texts:
                    if len(text) > 0:
                        if text[0] == "(":
                            text = " " + text
                        tmp.extend(re.split(r'([^0-9]+)(\([^()]+\))', text))
                texts = tmp
                if " " in texts:
                    texts.remove(" ")
                for text in texts:
                    result_ = []
                    if check_digit(text):
                        result_.append("".join([address[i] for i in text]))
                    elif check_chr_in_dict(text, address):
                        result_.append(check_chr_in_dict(text, address))
                    else:
                        for i in special_char:
                            text.replace(i, "")
                        words = pds.tokenize(text, form="word")
                        words_process = []
                        key_pos = []
                        for key in rank_dict:
                            for i, word in enumerate(words):
                                if key == word:
                                    key_pos.append(i)
                        pos = 0
                        if len(key_pos) == 0:
                            words_process.extend(words)
                        else:
                            for i, word in enumerate(words):
                                if i in key_pos:
                                    if i == 0:
                                        words_process.append(words[i])
                                    else:
                                        words_process.append("".join(words[pos: i]))
                                        words_process.append(words[i])
                                    pos = i + 1
                        for i in words_process:
                            if i in address:
                                result_.append(address[i])
                            else:
                                a, b = 0, ''
                                for add in address:
                                    simi = similar_string(i, add)
                                    if simi > a:
                                        a = simi
                                        b = add
                                if a > confidence_similar:
                                    result_.append(address[b])
                                # else:
                                #     return googleTranslate(text)
                    result.append(" ".join(result_))
                output.append(" ".join(result))
            result = ", ".join(output)

        elif field_name == "backside":
            result = text

        elif field_name == "no":
            if text in no_json:
                return no_json[text]
            else:
                for no_bu in dict_bu_eng_no:
                    tmp = text.split(no_bu)
                    text = (" " + no_bu + " ").join(tmp).strip()

                list_text = text.split(" ")
                list_eng = []
                for txt in list_text:
                    if txt in dict_bu_eng_no:
                        list_eng.append(dict_bu_eng_no[txt])
                    else:
                        if romanize(txt, BGN_PCGN):
                            list_eng.append("".join(romanize(txt, BGN_PCGN).split(" ")))
                        elif not ismyanmar(txt):
                            list_eng.append(txt)
                        else:
                            return googleTranslate(text)
                result = " ".join(list_eng)
        elif field_name == "employment":
            if text in employment_json:
                result = employment_json[text]
            else:
                return googleTranslate(text)
        else:
            return googleTranslate(text)

        result = result.strip()
        while "  " in result:
            result = result.replace("  ", " ")
        result = result.replace("( ", "(")
        result = result.replace(" )", ")")
        result = result.replace(" , ", ", ")

        result = re.sub('(?<=\d)+ (?=\d)+', '', result)
        result = result.title()
        return result
    except Exception as e:
        traceback.print_exc()
        return googleTranslate(text)


def translate(text):
    result = translate2eng_back(text, 'address')
    if len(result) == 0:
        return googleTranslate(text)
    return result


if __name__ == "__main__":
    text = "သာစည်ရွာ၊ အုပ်စု"
    result = googleTranslate(text)
    print(result)
