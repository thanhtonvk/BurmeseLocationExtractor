import json

from translate import translate

level_dict = {
    "village1": "ကျေးရွာ",
    "township": "မြို့နယ်",
    "city": "မြို့",
    "village2": "ရွာ",
    "region": "တိုင်းဒေသကြီး",
    "street": "လမ်း"
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
    with open('dictionary_backside/street_parse.json', encoding='utf-8') as json_file:
        street = json.load(json_file)
    return address_level, region, township, village, street


address_level, regions, townships, villages, streets = parseLocation()


def clean(address):
    address = address.replace('၊', ' ')
    return address.split()


def parseRegion(address_cleaned):
    value = None
    for idx, token in enumerate(address_cleaned):
        if level_dict['region'] in token:
            value = str(token).replace(level_dict['region'], '').strip()
            address_cleaned.pop(idx)
            break
    if value is not None:
        if value in regions.keys():
            return {"has_region": True, "region": value, 'en': regions[value], 'address_cleaned': address_cleaned}
        else:
            return {"has_region": True, "region": value, 'en': translate(value), 'address_cleaned': address_cleaned}
    else:
        for idx, token in enumerate(address_cleaned):
            if token in regions.keys():
                address_cleaned.pop(idx)
                return {"has_region": True, "region": value, 'en': regions[token], 'address_cleaned': address_cleaned}
        return {"has_region": False, "region": value, 'en': None, 'address_cleaned': address_cleaned}


def parseTownship(address_cleaned):
    value = None
    index_of_township = -1
    is_township = False
    for idx, token in enumerate(address_cleaned):
        if level_dict['city'] in token:
            value = str(token).replace(level_dict['city'], '').strip()
            index_of_township = idx
        if level_dict['township'] in token:
            value = str(token).replace(level_dict['township'], '').strip()
            index_of_township = idx
            is_township = True
    if value is not None:
        address_cleaned.pop(index_of_township)
        if value in townships.keys():
            if is_township:
                return {"has_township": True, "township": value, 'en': townships[value],
                        'address_cleaned': address_cleaned}
            else:
                return {"has_township": True, "city": value, 'en': townships[value],
                        'address_cleaned': address_cleaned}
        else:
            return {"has_township": True, "township": value, 'en': translate(value),
                    'address_cleaned': address_cleaned}
    else:
        for idx, token in enumerate(address_cleaned):
            if token in townships.keys():
                address_cleaned.pop(idx)
                return {"has_township": True, "township": token, 'en': townships[token],
                        'address_cleaned': address_cleaned}
        return {"has_township": False, "township": value, 'en': None, 'address_cleaned': address_cleaned}


def parseVillage(address_cleaned):
    value = None
    for idx, token in enumerate(address_cleaned):
        if level_dict['village1'] in token or level_dict['village2'] in token:
            value = str(token).replace(level_dict['village1'], '').replace(level_dict['village2'], '').strip()
            address_cleaned.pop(idx)
            break
    if value is not None:
        if value in regions.keys():
            return {"has_village": True, "village": value, 'en': villages[value], 'address_cleaned': address_cleaned}
        else:
            return {"has_village": True, "village": value, 'en': translate(value), 'address_cleaned': address_cleaned}
    else:
        for idx, token in enumerate(address_cleaned):
            if token in villages.keys():
                address_cleaned.pop(idx)
                return {"has_village": True, "village": value, 'en': villages[token],
                        'address_cleaned': address_cleaned}
        return {"has_village": False, "village": value, 'en': None, 'address_cleaned': address_cleaned}


def parseStreet(address_cleaned):
    value = None
    for idx, token in enumerate(address_cleaned):
        if level_dict['street'] in token:
            value = str(token).replace(level_dict['street'], '').strip()
            address_cleaned.pop(idx)
            break
    if value is not None:
        if value in regions.keys():
            return {"has_street": True, "street": value, 'en': streets[value], 'address_cleaned': address_cleaned}
        else:
            return {"has_street": True, "street": value, 'en': translate(value), 'address_cleaned': address_cleaned}
    else:
        for idx, token in enumerate(address_cleaned):
            if token in villages.keys():
                address_cleaned.pop(idx)
                return {"has_street": True, "street": value, 'en': streets[token],
                        'address_cleaned': address_cleaned}
        return {"has_street": False, "street": value, 'en': None, 'address_cleaned': address_cleaned}


def parseOther(address_cleaned):
    address = ' '.join(address_cleaned)
    if address != '':
        return {"has_other": True, "other": address, 'en': translate(address), 'address_cleaned': []}
    return {"has_other": False, "other": None, 'en': None, 'address_cleaned': []}


def locationExtractor(full_address):
    address_cleaned = clean(full_address)
    region = parseRegion(address_cleaned)
    township = parseTownship(region['address_cleaned'])
    village = parseVillage(township['address_cleaned'])
    street = parseStreet(village['address_cleaned'])
    other = parseOther(street['address_cleaned'])
    final = ''
    if other['has_other']:
        final += other['en'] + ', '
    if street['street']:
        final += (street['en'] + ' ' + list(street.keys())[1] + ', ')
    if village['has_village']:
        final += (village['en'] + ' ' + list(village.keys())[1] + ', ')
    if township['has_township']:
        final += (township['en'] + ' ' + list(township.keys())[1] + ', ')
    if region['has_region']:
        final += (region['en'] + ' ' + list(region.keys())[1])
    final = final.strip()
    if ',' == final[-1]:
        final = final[:-1]
    return final.title()


if __name__ == '__main__':
    from address_extractor import locationExtractor
    address = "၇၃၊အောင်သုခလမ်း၊ မြို့သစ်မြို့နယ် ၊ရေတွင်းကုန်းကျေးရွာ မန္တလေး ညာရေး-၂"
    print(locationExtractor(address))
