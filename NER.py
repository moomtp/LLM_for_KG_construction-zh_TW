# using "pip install -U ckiptagger[tfgpu,gdown]" for installing module'ckiptagger'
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import json
import csv

# =====  var setting  =====
sentence_file_path = 'sentences.csv'
entity_file_path = 'entity_list.csv'

# =====  define function  ========
def print_word_pos_sentence(word_sentence, pos_sentence):
    assert len(word_sentence) == len(pos_sentence)
    for word, pos in zip(word_sentence, pos_sentence):
        print(f"{word}({pos})", end="\u3000")
    print()
    return

def load_sentence_data(_sentence_file_path : str):
    with open(_sentence_file_path, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        sentence_list = []
        for row in rows:
            sentence_list.append(row['Sentence'])

    return sentence_list

def ckiptagger_NER(_sentence_list : list):
    ws = WS("./data")
    pos = POS("./data")
    ner = NER("./data")

    # import csv sentences

    # entity extraction
    word_sentence_list = ws(
        _sentence_list,
        # sentence_segmentation = True, # To consider delimiters
        # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
        # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
        # coerce_dictionary = dictionary2, # words in this dictionary are forced
    )

    pos_sentence_list = pos(word_sentence_list)
    entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

    return entity_sentence_list


# ========  main   ========


sentence_list = load_sentence_data(sentence_file_path)

entity_sentence_list = ckiptagger_NER(sentence_list)

output_entities = []

for i, sentence in enumerate(sentence_list):

    for entity in sorted(entity_sentence_list[i]):

        # only saving entity list w/ specific label
        if(entity[2] == 'CARDINAL' or  entity[2] =='DATE' or entity[2] == 'TIME' or entity[2] == 'ORDINAL') :
            continue
        output_entities.append([entity[3] , entity[2]])

#  counting entity #
entity_counting_dict = {}
for name , type in output_entities:
    entity_ID = name + '-' + type
    if entity_ID in entity_counting_dict:
        entity_counting_dict[entity_ID] += 1       
    else:
        entity_counting_dict[entity_ID] = 1       

entity_counting_dict = sorted(entity_counting_dict.items(), key=lambda x: x[1], reverse=True)
for i, entity in enumerate(entity_counting_dict):
    print((entity[0].split('-'))[0])
    print(entity[1])


#  saving all entity as csv 

# 開啟CSV檔案並將內容清空
with open(entity_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容

# 資料來源（假設這裡有某些資料）
new_row = {'entity_name': '', 'type': '', 'count' : ''}


# 新建CSV檔案並寫入資料
with open(entity_file_path, mode='w', newline='') as file:
    fieldnames = list(new_row.keys())  # 新的欄位名稱列表
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()  # 寫入欄位名稱

    # 逐筆寫入資料到CSV檔案
    for i, entity in enumerate(entity_counting_dict):
        
        
        new_row['entity_name'] = (entity[0].split('-'))[0]  # 將新資料放入新欄位
        new_row['type'] =(entity[0].split('-'))[1] 
        new_row['count'] = entity[1]

        writer.writerow(new_row)

# saving entity info & sentences into json file


json_data = []

for i in range(len(sentence_list)):
    json_data.append({'sentence':'test' , 'entity':[]})


for i , sentence in enumerate(sentence_list):
    json_data[i]['sentence'] = str(sentence)
    for entity in entity_sentence_list[i]:

        json_data[i]['entity'].append(entity[3])

# save sentence & entity's json file
with open('sentence_entities.json', 'w' , encoding='utf8' ) as file:
    json.dump(json_data, file, ensure_ascii=False)