import csv
import openai
import time
import ast
import warnings
import re
import logging
# ===== var setting  =====

input_file_path = './sentence_entities.json'
output_relation_file_path = './relation_data.csv'
sentence_file_path = 'sentences.csv'
entity_file_path = 'entity_list.csv'
GPT_key_file_path = './GPT_key.txt'

# log setting
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ====== def function  ======

# ----- GPT function  -----
def GPT_extraction_and_NER(sentence : str , mode:str='gpt-3.5' , filter: bool = True) -> dict:
    prompt_1 = """
    你是一個專門的命名實體識別（NER）與關係抽取 (Relationship extraction)系統。你的任務是接受文本作為輸入，並提取一組預定義的實體標籤的命名實體。 並找出所有命名實體之間的關係。
    從提供的文本輸入中，以下格式提取每個標籤的命名實體：
    LOC : 文本中提到的任何具名個人
    ORG : 文本中提到的任何具名組織
    PER : 任何政治或地理上定義的位置的名稱
    EVE : 文本中提到的任何特定事件
    MEDIA : 任何由人創作的藝術創作，如 : 書本、歌曲、繪畫...等

    下面是一個例子（只作為指南使用）：

    文本 : 
    '''
    美國參議院針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一位的華裔女性內閣成員。
    '''

    找到的實體與關係：
    '''
    { 'named entity' : 
        { 'LOC': ['美國'] , 
        'ORG' : ['參議院'] , 
        'PER': ['布什','趙小蘭'] , 
        'EVE' : [] , 
        'MEDIA' : []
    } ,
    'relation' : 
        [['布什', '提名', '趙小蘭'], 
        ['參議院','支持','趙小蘭'],
        ['參議院','展開','聽證會'],
        ['趙小蘭','是','第一位的華裔女性內閣'],
        ]
    }
    
    '''

    請從下列文本中提取實體
    文本 : 
    """



    # prompt setting 
    prompt = prompt_1 
    prompt = prompt + sentence
    if mode== 'gpt-3.5':
        MODEL_TYPE ='gpt-3.5-turbo' 
    elif mode == 'gpt-4':
        MODEL_TYPE ='gpt-4' 


    start_idx = 0
    GPT_result = {}
    print("\n ============================")

    print("\n給定句子：" + sentence)

    while start_idx < len(prompt):

        if(   start_idx + 1600 < len(prompt) ) : 
            warnings.warn("GPT out of range!")
        # assert input < 1600 english char or 400 chinese char
        end_idx = min(start_idx + 1600, len(prompt))
        sub_list = prompt[start_idx:end_idx]
        response = openai.ChatCompletion.create(
            model=MODEL_TYPE,
            messages=[
                # TODO : how to use role system 
                {"role": "user", "content": f"{sub_list}"}
            ]
        )  
        # response cleaner
        for choice in response.choices:
            print("\n GPT回傳資料 : " )
            # print(choice.message.content)
            # transfer response data type from str to dict
            try:
                pattern = r"\{.*\}"
                match = re.search(pattern, choice.message.content, re.DOTALL)

                if match:

                    dict_string = match.group(0)

                    GPT_result = ast.literal_eval(dict_string)  # change GPT massage string as list
                    print(GPT_result)

            except Exception as e :
                logging.error("GPT responce exception : %s" , e)
                print ("GPT exception")
                continue

        start_idx = end_idx
    return GPT_result


# ----- data manipulator  -----
def extract_entity_data(raw_data : list):
    entity_data = { 'LOC': [] ,
        'ORG' : [] ,
        'PER': [] ,
        'EVE' : [] ,
        'MEDIA' : [] , 
        'attribute' : []
        } 
    for sentence_data in raw_data:
        print(sentence_data)
        for i , (labeled_key , labeled_data) in enumerate(sentence_data['named entity'].items()):
            # print("key : " + labeled_key)
            # print("data : " + str(labeled_data))
            for entity_ele in labeled_data : 
                if entity_ele in entity_data[labeled_key] :  # skip if entity already exist
                    continue
                entity_data[labeled_key].append(entity_ele)
    
    return entity_data

def extract_relation(raw_data : list , entity_list : dict):
    all_entity = []
    for sublist in entity_list.values():
        for entity_ele in sublist : 
            all_entity.append(entity_ele)
    
    all_relation = []
    for sentence_data in raw_data:
        for i , relation_ele in enumerate(sentence_data['relation']):
            print(relation_ele)
            if relation_ele[0] in all_entity and relation_ele[2] in all_entity:
                all_relation.append(relation_ele)

    return  all_relation

def extract_attr_and_find_attr(raw_data : list , entity_list : dict):
    all_entity = []
    for sublist in entity_list.values():
        for entity_ele in sublist : 
            all_entity.append(entity_ele)
    
    all_attr = []
    for sentence_data in raw_data:
        for i , relation_ele in enumerate(sentence_data['relation']):
            if relation_ele[0] in all_entity and not(relation_ele[2] in all_entity):
                all_attr.append(relation_ele)
                if not(relation_ele[2] in entity_list['attribute']) : 
                    entity_list['attribute'].append(relation_ele[2])

            if relation_ele[2] in all_entity and not(relation_ele[0] in all_entity):
                all_attr.append(relation_ele)
                if not(relation_ele[0] in entity_list['attribute']) : 
                    entity_list['attribute'].append(relation_ele[0])
    return all_attr

def is_entity_in_relation(entity :str , relation_list  : list):
    for relation_ele in relation_list:
        if entity == relation_ele[0] or entity == relation_ele[2]:
            return True 
    return False


#  -----  csv & json function -----
def load_sentence_data(_sentence_file_path : str):
    with open(_sentence_file_path, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        sentence_list = []
        for row in rows:
            sentence_list.append(row['Sentence'])

    return sentence_list

# ========  main   ========
start_time = time.time()


sentence_list = load_sentence_data(sentence_file_path)

# GPT setting
keyfile = open(GPT_key_file_path, "r")
GPT_key = keyfile.readline()
openai.api_key = GPT_key


# extract relation & entity
raw_data = []
input_sentence = ""
for i , sentence in enumerate(sentence_list):
    input_sentence += sentence  # input two sentences instead of one
    if (i % 2) == 0 : 
        data_ele = GPT_extraction_and_NER(input_sentence, mode='gpt-4')
        raw_data.append(data_ele)
        input_sentence = ""

# entity preprocessing : check format correct
specific_keys = ['named entity', 'relation']
raw_data = [d for d in raw_data if all(key in d for key in specific_keys)]

# relation preprocessing : delete all relations which ele is less than 3
for sentence_relation in raw_data : 

    sentence_relation['relation'] = [sublist for sublist in sentence_relation['relation'] if len(sublist) >= 3]


# extract entity data
entity_data = extract_entity_data(raw_data)

#  filter out 'relation' , which both has entity tag
relation_data = extract_relation(raw_data, entity_data)
print("relation_data : " + str(relation_data))
#  filter out 'attribute' , which only one side has entity
attr_data = extract_attr_and_find_attr(raw_data , entity_data)
print("attr_data : " + str(attr_data))

# cat all relation and attr data
relation_list = [['head', 'relation', 'tail']]
for relation_ele in relation_data:
    relation_list.append(relation_ele)
for relation_ele in attr_data:
    relation_list.append(relation_ele)

# data prepocessing : delete entity which is not in any relation or has no attr
for key ,  entity_list in entity_data.items() :
    delete_idx = []
    for i , entity_ele in enumerate(entity_list) : 
        if is_entity_in_relation(entity_ele , relation_list) : 
            continue
        delete_idx.append(i)
    
    # delete entity
    new_entity_list = [entity_list[i]  for i  in range(len(entity_list)) if i not in delete_idx]
    entity_data[key] = new_entity_list



# ----- saving all data as csv  ------

# 開啟CSV檔案並將內容清空
with open(output_relation_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(output_relation_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    print(relation_list)
    try:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(relation_list)
    except Exception as e:
        logging.error("csv relation error : %s" , e)
        print('csv encoding error')



# 開啟CSV檔案並將內容清空
with open(entity_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(entity_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(['entity_name' , 'type'])
    try:
        for entity_field_key , entity_field_list  in entity_data.items(): # [{PER : []} , {LOC : []}]
            # print(entity_field_key)
            # print(entity_field_list)
            for entity_ele in entity_field_list:
                writer.writerow([entity_ele , entity_field_key])
    except Exception as e:
        logging.error("csv entity error : %s" , e)
        print('csv encoding error')


end_time = time.time()

print("開始時間 : " , time.ctime(start_time))
print("結束時間 : " , time.ctime(end_time))
