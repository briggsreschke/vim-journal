# Parses journal entries into json
# Uses regex to parse date/time stamp

import re
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dt = r'^[A-Za-z]{3}\s[A-Za-z]{3}\s+\d*'
text = ""
dic = {}
entries  = [] 

with open("TWELVE") as twelve:
    journal = [line.rstrip("\n") for line in twelve]

for line in journal:
    line = line.lstrip("\n")
    if re.search(dt, line):
        if text:
            dic["text"] = text 
            text = ""
            
            entries.append(dic)
            dic = {}
        
        dic["date"] = line
        continue
    elif line:
        text += line + "\n" 

dic["text"] = text
entries.append(dic)

with open("twelve.json", "w") as outf:
    json.dump(entries, outf, indent=3)


entry = {}
entries = []

with open("twelve.json", "r") as inf:
    journal = json.load(inf)

for entry in journal:
    dt = re.search(r"([A-Za-z]{3})\s([A-Za-z]{3})\s+(\d*)\s(\d\d:\d\d:\d\d)\s(\d*)", entry["date"])
    entry["day_name"] = dt.group(1)
    entry['month'] = dt.group(2)
    entry['day_num'] = dt.group(3)
    entry["time"] = dt.group(4)
    entry["year"] = dt.group(5)
    entry['text'] = entry['text']
    
    entries.append(entry)
    entry  = {}

# ------------------------------------------------------------------------------------
# Graph of num entries by day of week
# -----------------------------------------------------------------------------------

from collections import defaultdict
from collections import OrderedDict

tmp = [entry["day_name"] for entry in entries]
day_cnt = defaultdict(int)

for day in tmp:
    day_cnt[day] += 1 

days = dict(day_cnt)

day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
foo = {}

for i in range(0, 7):
    bar = day_order[i]
    foo[bar] = days[bar]


days_y = list(foo.values())
days_x = list(foo.keys())

fig, ax = plt.subplots()

ax.bar(days_x, days_y)
ax.set_ylabel('# of Entries')
#plt.show()
plt.savefig("graphs/days.png")

# ------------------------------------------------------------------------------------
# NLP count words by kind. Most used words: verbs and nouns
# ------------------------------------------------------------------------------------
import spacy

txt = ""
for entry in entries:
    txt += entry['text'].lower()

exclude = ['foobar']
nlp = spacy.load("en_core_web_lg")
doc = nlp(txt)

nouns = defaultdict(int)
verbs = defaultdict(int)

for tok in doc:
    word = tok.text 
    if word[0] == "*":
        word = tok.text[1:]
    if word in exclude:
        continue
    if tok.pos_ == "NOUN" or tok.pos_ == "PROPN":
        if word.isalnum():
            nouns[word] += 1
    elif tok.pos_== "VERB":
        if word.isalnum():
            verbs[word] += 1   

from collections import Counter

# -------------------------------------------------------------------
# NOUNS
# -------------------------------------------------------------------

foo = sorted(nouns.items(), key=lambda x:x[1], reverse=True)
noun_dict = dict(foo)

n = 10
counter = Counter(noun_dict)
result = dict(counter.most_common(n))

word_x = list(result.keys())
word_y = list(result.values())

fig, ax = plt.subplots()

ax.barh(word_x, word_y)
#plt.xticks(word_x, word_x, rotation='vertical')
ax.set_title("Nouns")
ax.set_xlabel('Word Frequency')
#plt.show()
plt.savefig("graphs/words-noun.png")
# -------------------------------------------------------------------
# VERBS
# -------------------------------------------------------------------


foo = sorted(verbs.items(), key=lambda x:x[1], reverse=True)
verb_dict = dict(foo)

n = 15
counter = Counter(verb_dict)
result = dict(counter.most_common(n))

word_x = list(result.keys())
word_y = list(result.values())

fig, ax = plt.subplots()

ax.barh(word_x, word_y)
#plt.xticks(word_x, word_x, rotation='vertical')
ax.set_title("Verbs")
ax.set_xlabel('Word Frequency')

#plt.show()
plt.savefig("graphs/words-verb.png")

# ------------------------------------------------------------------------------------
# Time of Day | # of entries
# ------------------------------------------------------------------------------------

pattern = r"(\d+):(\d+):(\d+)"
time_by_hour = defaultdict(int)

for entry in entries:
    foo = re.search(pattern, entry["time"])
    if foo:
        hours = int(foo.group(1))
        minutes = int(foo.group(2))
        seconds = int(foo.group(3))
        time_by_hour[hours] += 1

time_by_hour = dict(time_by_hour)
od = OrderedDict(sorted(time_by_hour.items()))
time_by_hour = dict(od)

y = list(time_by_hour.values())
x = list(time_by_hour.keys())

fig, ax = plt.subplots()

plt.ylabel("Number of Entries") 
plt.xlabel("Hour of Day")

lim = max(y) + 1

ax.plot(x, y, linewidth=2.0)
ax.set(xlim=(-1, 24), xticks=np.arange(0,24+1
                                      ),
       ylim=(0, lim), yticks=np.arange(0, lim+1))
#ax.bar(x, y )

#plt.show()

plt.savefig("graphs/time-ebh.png")

