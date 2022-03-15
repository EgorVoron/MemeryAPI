def classify_lang(text):
    if not text:
        return 'eng'
    rus_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    eng_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for letter in eng_alphabet:
        if letter in text:
            return 'eng'
    for letter in rus_alphabet:
        if letter in text:
            return 'rus'
    return classify_lang(text[1:])
