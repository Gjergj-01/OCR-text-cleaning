import json
import re
from difflib import get_close_matches

file_path = 'datasets/sharegpt-format-datasets/test_dataset.json'

def pulisci_spazi(testo):
    return re.sub(r'\s\s', ' ', testo)

def compatta_spazi(testo):
    # 1. Rimuovi gli spazi singoli tra caratteri alfanumerici
    testo = re.sub(r'(?<=\w) (?=\w)', '', testo)
    # 2. Riduci tutti gli altri spazi multipli a uno
    testo = re.sub(r' {2,}', ' ', testo)

    return testo


def unisci_parole_troncate(testo):
    # Matcha casi tipo: parola- \n parola
    pattern = re.compile(r'(\w+)-\s*\n\s*(\w+)')
    # Sostituisce con la parola unita
    return pattern.sub(lambda m: m.group(1) + m.group(2), testo)


def lcs(list1, list2):
    m, n = len(list1), len(list2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len, end_index = 0, 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if list1[i - 1] == list2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_index = i
    return list1[end_index - max_len: end_index]


def find_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind,ind+sll-1


def subwords(messy, clean):
    if len(messy) < 20:
        #print(f"Found pair: {messy, clean}")
        return [[messy, clean]]
    
    common_words = lcs(messy, clean)

    if not common_words: 
        #print(f"NO COMMON FOUND: {messy} | {clean}")
        return [[messy, clean]]
    #print("Found common words: ", common_words)
    # call 
    start_messy, end_messy = find_sub_list(common_words, messy)
    start_clean, end_clean = find_sub_list(common_words, clean)

    # take first half
    first_messy = messy[: start_messy]
    first_clean = clean[: start_clean]
    first_half = subwords(first_messy, first_clean)
    # take second half

    second_messy = messy[end_messy+1:]
    second_clean = clean[end_clean+1:]
    second_half = subwords(second_messy, second_clean)

    return first_half + second_half + [[messy[start_messy: end_messy+1], clean[start_clean: end_clean+1]]]

with open(file_path, 'r') as file:
    d = json.load(file)


final_list = []
unisci_parole = lambda coppie: [[' '.join(x), ' '.join(y)] for x, y in coppie]

for i in range(len(d)):

    print(f"Iteration number {i}")
    sporca = pulisci_spazi(unisci_parole_troncate((d[i]['conversations'][0]['value'])))
    pulita = d[i]['conversations'][1]['value']

    sporca = sporca.split(' ')
    pulita = pulita.split(' ')

    coppie = subwords(sporca, pulita)
    ret = unisci_parole(coppie)
    for pair in ret:
        final_list.append({
            "conversations": [{"from": "human", "value": pair[0]}, {"from": "Minerva-350", "value": pair[1]}]
        })

with open("datasets/sharegpt-format-datasets/new_test_dataset.json", "w") as out:
    json.dump(final_list, out, ensure_ascii=False, indent=2)