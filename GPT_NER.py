import csv
import openai
import json
import ast
import warnings
import re

# ===== var setting  =====

input_file_path = './sentence_entities.json'
output_relation_file_path = './relation_data.csv'

GPT_key_file_path = './GPT_key.txt'

# ====== def function  ======

def GPT_relation_extraction(_sentence : str, _entity_list : list, _mode:str='gpt-3.5' , _filter: bool = True) -> list:
    prompt_1 = """你是一個專門的關係抽取 (Relationship extraction)系統。你的任務是讀取上面的文本與抽取出來的實體作為輸入，並提取一或多組命名實體之間的關係，並以[[實體，關係，實體]，...]的形式回答。 

        下面是一個例子（只作為指南使用）：
    文本 : 
    '''
    美國參議院針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一位的華裔女性內閣成員。
    '''

    找到的實體列表：
    '''
    {PER :  ['布什','趙小蘭'], ORG :  ['參議院']}
    '''

    '''
    [['布什', '提名', '趙小蘭'], ['參議院','支持','趙小蘭']]
    '''


    請從下列文本中提取實體
    文本 : 
    給定句子 : 
    SPO三元組 :   

    """



    # prompt setting 
    prompt = prompt_1 

    if _mode== 'gpt-3.5':
        MODEL_TYPE ='gpt-3.5-turbo' 
    elif _mode == 'gpt-4':
        MODEL_TYPE ='gpt-4' 


    start_idx = 0
    result = []
    print("\n ============================")
    print("\n主語和賓語列表：" + str(_entity_list))
    print("\n給定句子：" + _sentence)

    while start_idx < len(prompt):
        # TODO : if possible can extract muti relation in one api call?

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
        for choice in response.choices:
            print("\n GPT回傳資料 : " + choice.message.content)
            try:
                GPT_result = ast.literal_eval(choice.message.content)  # change GPT massage string as list
                for item in GPT_result:
                    # TODO : filter condition change to search whole entity list
                    if(not _filter):
                        result.append(item)
                    elif((item[0] in _entity_list) and (item[2] in _entity_list) ):  # only head and tail object both in NER will be filtered out
                        result.append(item)
            except:
                print ("GPT exception")
                continue

        start_idx = end_idx
    return result
# interface for neal4j

# def GPT_NER(_sentence : str, _entity_list : list, _mode:str='gpt-3.5' , _filter: bool = True) -> list:
#     prompt_1 = """
#     你是一個專門的命名實體識別（NER）系統。你的任務是接受文本作為輸入，並提取一組預定義的實體標籤的命名實體。 
#     從提供的文本輸入中，以下格式提取每個標籤的命名實體：
#     LOC : 文本中提到的任何具名個人
#     ORG : 文本中提到的任何具名組織
#     PER : 任何政治或地理上定義的位置的名稱
#     EVE : 文本中提到的任何特定事件
#     MEDIA : 任何由人創作的藝術創作，如 : 書本、歌曲、繪畫...等

#     下面是一個例子（只作為指南使用）：

#     文本：
#     '''
#     杰克和吉爾上山去。
#     '''
#     { 'LOC': ['山'] , 
#     'ORG' : [] , 
#     'PER': ['杰克','吉爾'] , 
#     'EVE' : [] , 
#     'MEDIA' : []}

#     請從下列文本中提取實體
#     文本 : 
#     """

#     return result

def I_GPT_extraction(_sentence_and_entity_list : list) -> list:
    GPT_key_file_path = './GPT_key.txt'
    data = _sentence_and_entity_list



    # GPT setting
    keyfile = open(GPT_key_file_path, "r")
    GPT_key = keyfile.readline()
    openai.api_key = GPT_key


    # extract relation & save result into csv file

    for data_ele  in data :
        # if no entity be reconized , skip extraction
        if(not(data_ele['entity'])):
            continue

        relation_result = (GPT_relation_extraction(data_ele['sentence'], data_ele['entity'], _mode='gpt-4'))
        data_ele['relation'] = relation_result
    return data

def all_in(sentence : str , mode:str='gpt-3.5' , filter: bool = True) -> dict:
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
    { 'namely entity' : 
        { 'LOC': [] , 
        'ORG' : ['參議院'] , 
        'PER': ['布什','趙小蘭'] , 
        'EVE' : [] , 
        'MEDIA' : []} ,
    'relation' : 
        [['布什', '提名', '趙小蘭'], 
        ['參議院','支持','趙小蘭']]
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
        # TODO : if possible can extract muti relation in one api call?
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
        for choice in response.choices:
            print("\n GPT回傳資料 : " )
            try:
                pattern = r"{.*}"
                match = re.search(pattern, choice.message.content)
                print(match)
                if(match):
                    # print(match.group(0))
                    dict_string = match.group(0)
                    print(dict_string)
                    GPT_result = json.loads(dict_string)  # change GPT massage string as list
                    # print(GPT_result.type)
                    print(GPT_result)

            except:
                print ("GPT exception")
                continue

        start_idx = end_idx
    return GPT_result


# ========  main   ========


# import sentences file (.json)
sentence_list = []
with open(input_file_path, 'r' , encoding='utf8') as jsonfile:
    data = json.load(jsonfile)



# GPT setting
keyfile = open(GPT_key_file_path, "r")
GPT_key = keyfile.readline()
openai.api_key = GPT_key


# extract relation & save result into csv file


relation_list = [['head', 'relation', 'tail']]

for data_ele  in data :
    # if no entity be reconized , skip extraction
    if(not(data_ele['entity'])):
        continue

    relation_result = (all_in(data_ele['sentence'], mode='gpt-3.5'))
    for relation_ele in relation_result:
        relation_list.append(relation_ele)



# print(relation_list)

# 開啟CSV檔案並將內容清空
with open(output_relation_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(output_relation_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    print(relation_list)
    try:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(relation_list)
    except:
        print('csv encoding error')




