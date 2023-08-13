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

# ========  main   ========


ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

# import csv sentences
with open(sentence_file_path, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    sentence_list = []
    for row in rows:
        print(row['Sentence'])
        sentence_list.append(row['Sentence'])

# entity extraction
word_sentence_list = ws(
    sentence_list,
    # sentence_segmentation = True, # To consider delimiters
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
    # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    # coerce_dictionary = dictionary2, # words in this dictionary are forced
)

pos_sentence_list = pos(word_sentence_list)

entity_sentence_list = ner(word_sentence_list, pos_sentence_list)


output_entities = []

for i, sentence in enumerate(sentence_list):
    # print()
    # print(f"'{sentence}'")
    # print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
    for entity in sorted(entity_sentence_list[i]):
        # print(entity)
        # saving entity list w/ specific label
        output_entities.append([entity[3] , entity[2]])

        


#  saving all entity as csv 

# 開啟CSV檔案並將內容清空
with open(entity_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容

# 資料來源（假設這裡有某些資料）
new_row = {'entity_name': '', 'type': ''}


# 新建CSV檔案並寫入資料
with open(entity_file_path, mode='w', newline='') as file:
    fieldnames = list(new_row.keys())  # 新的欄位名稱列表
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()  # 寫入欄位名稱

    # 逐筆寫入資料到CSV檔案
    for i, entity in enumerate(output_entities):
        
        new_row['entity_name'] = entity[0]  # 將新資料放入新欄位
        new_row['type'] = entity[1] 
        writer.writerow(new_row)

# saving entity info & sentences into json file

# TODO : counting entity #

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