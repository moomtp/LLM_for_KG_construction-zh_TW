import csv
import openai
import json
import ast

# ===== var setting  =====

input_file_path = './sentence_entities.json'
output_relation_file_path = './relation_data.csv'

GPT_key_file_path = './GPT_key.txt'

# ====== def function  ======

def GPT_relation_extraction(_sentence : str, _entity_list : list, _mode:str='gpt-3.5') -> list:
    prompt_1 = "\n 請從以下文本中提取主語-謂語-賓語三元組(SPO三元組)，並以[[主語，謂語，賓語]，...]的形式回答，注意答案中的主語必須包含主語列表提供的實體，否則直接去除 : "  +  \
    "\n例如:" + \
    "\n給定句子 : 美國參議院針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一位的華裔女性內閣成員。" + \
    "\n主語和賓語列表：[ '布什','趙小蘭', '參議院']" + \
    "\nSPO三元組 : [['布什', '提名', '趙小蘭'], ['參議院','展開認可聽證會','趙小蘭']]" + \
    "\n主語和賓語列表：" + str(_entity_list) +\
    "\n給定句子 : " + _sentence + \
    "\nSPO三元組 : "     

    prompt_2 = "\n 請從以下文本中提取主語-謂語-賓語三元組(SPO三元組)，並以[[主語，謂語，賓語]，...]的形式回答，注意答案中的主語必須包含主語列表提供的實體，否則直接去除 : "  +  \
    "\n例如:" + \
    "\n給定句子 : 641年3月2日文成公主入藏，與松贊乾布和親。" + \
    "\n主語和賓語列表：['松赞干布' , '文成公主']" + \
    "\nSPO三元組 : [['松赞干布' , '妻子' , '文成公主' ],['文成公主' , '丈夫' , '松赞干布' ]]" + \
    "\n主語和賓語列表：" + str(_entity_list) +\
    "\n給定句子 : " + _sentence + \
    "\nSPO三元組 : "     


    # prompt setting 
    prompt = prompt_2  

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
            GPT_result = ast.literal_eval(choice.message.content)  # change GPT massage string as list
            for item in GPT_result:
                if((item[0] in _entity_list) and (item[2] in _entity_list) ):  # only head and tail object both in NER will be filtered out
                    result.append(item)

        start_idx = end_idx
    return result

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

    relation_result = (GPT_relation_extraction(data_ele['sentence'], data_ele['entity'], mode='gpt-3.5'))
    for relation_ele in relation_result:
        relation_list.append(relation_ele)



# print(relation_list)

# 開啟CSV檔案並將內容清空
with open(output_relation_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(output_relation_file_path, 'w', newline='') as csvfile:
    print(relation_list)

    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(relation_list)




