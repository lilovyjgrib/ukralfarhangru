import json
import requests
import bs4
from bs4 import BeautifulSoup


"""
html structure:

body > div style="margin:30px 5px" > table ... > tbody > tr[3] > td...[2] >>
span class='xarf fa' -- orthographic entry (&zwnj; => "‌" -- но мб автоматически)
& span class='read' -- latin trans{literation}
(& index of a polysemantic sense)
(& i -- dict comment (мб забахать расшифровочку))
& span class='trans' (& * n of related translations)
(& "; " or "." or " (...).")
(& * n of polysemantic sense)
(br
    
span style='color:gray; > span clas='xarf fa' & i &  "[index]...[/index]; [index]...[/index].") -- collocation
& br*2 pre -- border
"""


# extracting
def collect_entries(it):
    """
    group sibling tags/strings by entry
    """
    dic = {'first': []}
    latest_entry = 'first'
    for sibling in it:
        if type(sibling) == bs4.element.Tag and sibling.name == 'span' and sibling.get('class') == ['xarf', 'fa']:
            latest_entry = sibling.text
            dic[latest_entry] = []
        else:
            dic[latest_entry].append(sibling)
    del dic['first']
    for i, j in dic.items():
        print(i)
        print(j)

    return dic


def get_article(l):
    """
    crazy analog of RegEx: makes a systemized article from list of tags & strings
    """
    res = {'transliteration': '', 'senses': [], 'collocations': {}}
    double = False  # часть костыля
    for t in l:

        if type(t) == bs4.element.NavigableString:
            if t.strip() in '[] !!!1.;,.    ()!':
                pass
            elif t.strip('.  ') in '23456789':
                res['senses'].append({'comments': [], 'translations': []})

            elif t.strip()[0] == '[' and t.strip()[-1] == ']' or ')':  # костыль для кринжовых транскрипций
                res['transliteration'] = t.strip(' \t[])')
                res['senses'].append({'comments': [], 'translations': []})
            elif t.strip()[0] == ']' and t.strip()[-1] == '.':  # костыль для кринжовых помет
                res['senses'][-1]['comments'].append(t.strip('\t .]'))
            elif t.strip()[0] == ']' and t.strip()[-1] == ';':  # костыль для кринжовых переводов
                res['senses'][-1]['translations'].append((t.strip(';]\t '), None))
            # костыль для переводов в кавычках
            elif t.strip()[0] == ']' and t.strip()[-1] == '«':
                pass
            elif t.strip()[-1] == '»':
                tup = res['senses'][-1]['translations'][-1]
                tup2 = ('«' + tup[0] + '»', tup[1])
                res['senses'][-1]['translations'][-1] = tup2
            # костыль для кринжовых помет №2
            elif type(t.previous_sibling) == bs4.element.Tag and t.previous_sibling.name == 'i':
                res['senses'][-1]['comments'].append(t.strip())
            # костыль для 2х транскрипций
            elif t.strip() == 'и' and type(t.previous_sibling) == bs4.element.Tag and t.previous_sibling.name == 'read':
                res['senses'][-1]['comments'].append(t.strip())
                double = True
            # костыль для кринжовой полисемии
            elif t.strip()[:2] == '1.' and t.strip()[-1] == ';':
                res['senses'][-1]['translations'].append((t.strip(';1.\t '), None))

            else:
                if res['senses'][-1]['translations']:
                    trans_no_comment = res['senses'][-1]['translations'][-1][0]
                    res['senses'][-1]['translations'][-1] = (trans_no_comment, t.strip(' \t.'))
                else:
                    res['senses'][-1]['translations'].append(t.strip('\t ]['))

        elif type(t) == bs4.element.Tag:
            if t.name == 'span' and 'class' in t.attrs and t['class'] == ['read']:
                if double:
                    res['transliteration'] += '|'
                res['transliteration'] += t.text
                res['senses'].append({'comments': [], 'translations': []})
            if t.name == 'i':
                if res['senses']:
                    res['senses'][-1]['comments'].append(t.text)
                else:
                    res['senses'].append({'comments': [], 'translations': []})
                    res['senses'][-1]['comments'].append(t.text)
            if t.name == 'span' and 'class' in t.attrs and t['class'] == ['trans']:
                res['senses'][-1]['translations'].append((t.text, None))
            if t.name == 'span' and 'class' not in t.attrs:
                trans = ''
                for line in t.strings:
                    if 'index' in line:
                        trans += line
                trans = trans.replace('[index]', '').replace('[/index]', '').strip(';—. ').split(';')
                res['collocations'][t.span.text] = {'translations': trans, 'comments': ''}
                if t.i:
                    res['collocations'][t.span.text]['comments'] = t.i.text

    return res


def extractor(s):

    soup = BeautifulSoup(s, 'lxml')
    content = soup.body.div.table
    if content.tbody is not None:
        content = content.tbody
    content = content.contents[5].contents[3].find_all('pre')[1].next_siblings

    res = collect_entries(content)
    for k, v in res.items():
        res[k] = get_article(v)

    return res


# requesting & collecting
pages = []
for pagen in range(12, 321):
    link = 'http://www.farhang.ru/newdix2021.html?page=' + str(pagen)
    response = requests.get(link)
    print(response)
    response.encoding = 'utf-8'
    page = response.text
    pages.append(page)

dictionary = {}
for i, j in enumerate(pages):
    if not i == 279:
        dictionary.update(extractor(j))


# writing down the data
with open("new_dictionary.json", "w") as f:
    json.dump(dictionary, f, indent=4)


# tbd:  1. make a csv 2. make an alphabetical stucture 3. make the russian key list

print(dictionary)
