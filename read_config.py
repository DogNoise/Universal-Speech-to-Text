# -*- coding: UTF-8 -*-
_lan_pack={
    "PL":
    {
        "lanNameEN":"Polish",
        "lanName":"Polski",
        "Live":{
            "mainTitle":"Rozpoznawanie mowy na żywo",
            "mainButton":["rozpocznij rozpoznawanie mowy","rozpoznaję mowę","zakończ rozpoznawanie mowy"],
            "alts":"Alternatywy",
            "defTextInput":"Tu pojawi się przetworzony tekst"
        },
        "File":{
            "mainTitle":"Rozpoznawanie mowy z plików",
            "sideTitle":["zaznacz plik audio (tylko .wav)","zaznaczyłeś plik audio","zaznacz obsługiwany plik audio","zakończono"],
            "mainButton":["rozpocznij transkrypcje pliku","dzielę plik","transkrypcja kolejnego pliku"],
            "fileName":"Nazwa pliku",
            "size":"Rozmiar",
            "defTextInput":"Tu pojawi się przetworzony tekst"
        },
        "Settings":{
            "panelName":"Panel ustawień",
            "selectAppLang":"Wybierz język aplikacji",
            "selectTranscriptionLang":"Wybierz język transkrypcji",
            "supportedLang":[
                    ["pl-PL", "Polski"],
                    ["ar-EG", "Egipski"],
                    ["cs-CZ", "Czeski"],
                    ["en-AU", "Angielski — (Australia)"],
                    ["en-CA", "Angielski — (Kanada)"],
                    ["en-NZ", "Angielski — (Nowa Zelandia)"],
                    ["en-GB", "Angielski - (Zjednoczone Królestwo)"],
                    ["en-US", "Angielski -  (Stany Zjednoczone)"],
                    ["fr-FR", "Francuski"],
                    ["fil-PH", "Filipiński"],
                    ["de-DE", "Niemiecki"],
                    ["id-ID", "Indonezyjski"],
                    ["it-IT", "Włoski"],
                    ["ja-JP", "Japoński"],
                    ["ko-KR", "Koreański"],
                    ["nb-NO", "Norweski"],
                    ["ru-RU", "Rosyjski"],
                    ["eu-ES", "Hiszpański"],
                    ["sv-SE", "Szwedzki"],
                    ["uk-UA", "Ukraiński"],
                    ["vi-VN", "Wietnamski"]
                ]

        },
        "MotherScreen":{
            "AppName":"Aplikacja zamieniająca mowę na tekst",
            "Live":"Na żywo",
            "File":"Z pliku",
            "Settings":"Ustawienia",
        }

    },
    "EN":
        {
            "lanNameEN": "English",
            "lanName": "English",
            "Live": {
                "mainTitle": "Live speech recognition",
                "mainButton": ["start speech recognition", "I recognize speech", "end speech recognition"],
                "alts": "Alternatives",
                "defTextInput": "The processed text will appear here"
            },
            "File": {
                "mainTitle": "Speech recognition from files",
                "sideTitle": ["select an audio file (only .wav)", "you selected an audio file","select a supported audio file","done"],
                "mainButton": ["start transcribing the file", "splitting file into chunks", "transcribe of the next file"],
                "fileName": "File Name",
                "size": "Size",
                "defTextInput": "The processed text will appear here"
            },
            "Settings": {
                "panelName": "Settings panel",
                "selectAppLang": "Select language",
                "selectTranscriptionLang": "Select the transcription language",
                "supportedLang":[
                    ["en-AU", "English - (Australia)"],
                    ["en-CA", "English - (Canada)"],
                    ["en-NZ", "English - (New Zealand)"],
                    ["en-GB", "English - (United Kingdom)"],
                    ["en-US", "English - (United States)"],
                    ["ar-EG","Egyptian"],
                    ["cs-CZ","Czech"],
                    ["fr-FR","French"],
                    ["fil-PH","Filipino"],
                    ["de-DE","German"],
                    ["id-ID","Indonesian"],
                    ["it-IT","Italian"],
                    ["ja-JP","Japanese"],
                    ["ko-KR","Korean"],
                    ["nb-NO","Norwegian"],
                    ["pl-PL","Polish"],
                    ["ru-RU","Russian"],
                    ["es-ES","Spanish"],
                    ["sv-SE","Swedish"],
                    ["uk-UA","Ukrainian"],
                    ["vi-VN","Vietnamese"]
                ]
            },
            "MotherScreen": {
                "AppName": "Speech-to-text application",
                "Live": "Live",
                "File": "File",
                "Settings": "Settings",
            }

        }

}

_app_config={
    "curr_lang":"PL",
    "curr_transcription_lang":"pl-PL",
    "curr_mic":0
}

def get_list_of_languages(out_type=0):
    '''Function that returns all avaliable languages
    :param out_type: int
    0 - return language code, E.g. PL
    1 - return language names
    2 - return english language names
    :param print_output: bool - should function print output
    :return:
    '''
    list=[]
    print_output = False

    if not out_type:
        for lan in _lan_pack:
            list.append(lan)

    elif out_type==1:
        for key,value in _lan_pack.items():
            list.append(value.get('lanName'))
    else:
        for key, value in _lan_pack.items():
            list.append(value.get('lanNameEN'))

    if print_output:
        print(list)

    return list

def get_config(key):
    assert _app_config.get(key) != None, "key {} does not exist in {}".format(key, "config file")
    return _app_config.get(key)

def update_config(key, newValue):
    _app_config.update({key:newValue})

def get_key(key):
    curr_lang=_app_config.get("curr_lang")
    assert _lan_pack.get(curr_lang).get(key) != None, "key {} does not exist in {}".format(key, curr_lang)
    return _lan_pack.get(curr_lang).get(key)

def get_key_for_live(key):
    curr_lang=_app_config.get("curr_lang")
    assert _lan_pack.get(curr_lang).get('Live').get(key) != None, "key {} does not exist in {}".format(key, curr_lang)
    return _lan_pack.get(curr_lang).get('Live').get(key)

def get_key_for_file(key):
    curr_lang=_app_config.get("curr_lang")
    assert _lan_pack.get(curr_lang).get('File').get(key) != None, "key {} does not exist in {}".format(key, curr_lang)
    return _lan_pack.get(curr_lang).get('File').get(key)

def get_key_for_settings(key):
    curr_lang=_app_config.get("curr_lang")
    assert _lan_pack.get(curr_lang).get('Settings').get(key) != None, "key {} does not exist in {}".format(key, curr_lang)
    return _lan_pack.get(curr_lang).get('Settings').get(key)

def get_key_for_mother_screen(key):
    curr_lang=_app_config.get("curr_lang")
    assert _lan_pack.get(curr_lang).get('MotherScreen').get(key) != None, "key {} does not exist in {}".format(key, curr_lang)
    return _lan_pack.get(curr_lang).get('MotherScreen').get(key)

def set_app_language(lang):
    if not lang in get_list_of_languages():
        print('\033[91m'+"This language is not supported, I wont' change language of Aplication"+'\033[0m')
    else:
        _app_config.update({"curr_lang":lang})

def test():
    #test of Changing languages
    print("Current language of aplication {}".format(get_config("curr_transcription_lang")))
    print("Change language of aplication to EN")
    set_app_language("EN")
    print("Now current language is {}\n".format(get_config("curr_transcription_lang")))
    print("Now I will try to change to lanuage that is not suported - AR")
    set_app_language("AR")
    print("Current language of aplication {}".format(get_config("curr_transcription_lang")))
    print("Back to PL")
    set_app_language("PL")
    print("Current language of aplication {}".format(get_config("curr_transcription_lang")))

    #Read config
    print("This is current transcription lanuage {}".format(get_config("curr_transcription_lang")))
    print("This is ID of current microphone  {}".format(get_config("curr_mic")))
    print("Current language of aplication {}".format(get_config("curr_transcription_lang")))


