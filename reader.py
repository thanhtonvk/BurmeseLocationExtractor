import json

from translate import translate

level_dict = {
    "village1": "ကျေးရွာ",
    "township": "မြို့နယ်",
    "city": "မြို့",
    "village2": "ရွာ",
    "region": "တိုင်းဒေသကြီး"

}


def parseLocation():
    with open('dictionary_backside/address.json', encoding='utf-8') as json_file:
        address_level = json.load(json_file)
    with open('dictionary_backside/region.json', encoding='utf-8') as json_file:
        region = json.load(json_file)
    with open('dictionary_backside/township.json', encoding='utf-8') as json_file:
        township = json.load(json_file)
    with open('dictionary_backside/village.json', encoding='utf-8') as json_file:
        village = json.load(json_file)
    return address_level, region, township, village


address_level, regions, townships, villages = parseLocation()


def split_address(address):
    return address.split('၊')


def clean_address(address):
    address = address.replace('၊', ' ')
    for level in address_level:
        if level in address:
            address = address.replace(level, " ")
    return ' '.join(address.split())


def parse_village(full_address):
    splited_address = split_address(full_address)
    village = None
    for address in splited_address:
        if level_dict["village1"] in address:
            village = address.replace(level_dict["village1"], "")
        elif level_dict["village2"] in address:
            village = address.replace(level_dict["village2"], "")
    if village is not None:
        if village in villages.keys():
            return {"has_village": True, "village": village, 'en': villages[village]}
        else:
            return {"has_village": True, "village": village, 'en': translate(village)}
    else:
        cleaned_address = clean_address(full_address)
        for add in cleaned_address.split():
            for value in villages.keys():
                if add == value:
                    return {"has_village": True, "village": value, 'en': villages[value]}
        return {"has_village": False, "village": village, 'en': None}


def parse_township(full_address):
    splited_address = split_address(full_address)
    township = None
    key = ""
    for address in splited_address:
        if level_dict["township"] in address:
            key = "township"
            township = full_address.replace(level_dict[key], "")
            break
        if level_dict["city"] in address:
            key = "city"
            township = address.replace(level_dict[key], "")
    if township is not None:
        for value in township.split():
            if value in townships.keys():
                return {"has_township": True, key: value, 'en': townships[value]}

        return {"has_township": True, key: township, 'en': translate(township)}
    else:
        cleaned_address = clean_address(address)
        for add in cleaned_address.split():
            for value in townships.keys():
                if add == value:
                    return {"has_township": True, "township": value, 'en': townships[value]}
        return {"has_township": False, "township": township, 'en': None}


def parseRegion(full_address):
    splited_address = split_address(full_address)
    region = None
    for address in splited_address:
        if level_dict["region"] in address:
            region = address.replace(level_dict["region"], "")
    if region is not None:
        if region in regions.keys():
            return {"has_region": True, "region": region, 'en': regions[region]}
        else:
            return {"has_region": True, "region": region, 'en': translate(region)}
    else:
        cleaned_address = clean_address(address)
        for add in cleaned_address.split():
            for value in regions.keys():
                if add == value:
                    return {"has_region": True, "region": value, 'en': regions[value]}
        return {"has_region": False, "region": region, 'en': None}


def location_extractor(full_address):
    final = ''
    region = parseRegion(full_address)
    if region['has_region']:
        full_address = full_address.replace(region['region'], "").replace(level_dict['region'], "").strip()
        final = region['en']
    township = parse_township(full_address)
    if township['has_township']:
        if 'township' in township.keys():
            full_address = full_address.replace(township['township'], "").replace(level_dict['township'], "").strip()
            final = township['en'] + ' township, ' + final
        else:
            full_address = full_address.replace(township['city'], " ").replace(level_dict['city'], " ").strip()
            final = township['en'] + ' city, ' + final
    village = parse_village(full_address)
    if village['has_village']:
        full_address = full_address.replace(village['village'], "").replace(level_dict['village1'], "").replace(
            level_dict['village2'], "").strip()
        final = village['en'] + ' village, ' + final
    last_address = ''
    for add in split_address(full_address):
        if add.strip() != '':
            last_address += (add.strip() + '၊ ')
    if last_address != '':
        final = translate(last_address) + final
    return final.title()


if __name__ == '__main__':
    import pandas as pd

    df = pd.read_csv('address.txt', sep='|', header=None)
    burmese = df[0]
    en = df[1]
    result = []
    for address in burmese:
        try:
            result.append(location_extractor(address))
        except:
            result.append(address)
    df[2] = result
    df.to_csv('final.csv')
