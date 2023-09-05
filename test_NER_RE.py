import re
import ast
import csv
import time
import GPT_NER_RE



# TODO : change '，' into ','


input_file_path = './sentence_entities.json'
output_relation_file_path = './relation_data.csv'
sentence_file_path = 'sentences.csv'
entity_file_path = 'entity_list.csv'
GPT_key_file_path = './GPT_key.txt'

raw_data = """找到的實體與關係：
    '''
    { 'named entity' :
        { 'LOC': [] ,
        'ORG' : [] ,
        'PER': [] ,
        'EVE' : [] ,
        'MEDIA' : []
        } ,
    'relation' :
        []
    }

    '''
"""

sub_test_data1 = { 'named entity' :
    { 'LOC': [] ,
    'ORG' : ['吳王闔閭','孫武','齊國','孫臏'] ,
    'PER': ['孫子'] ,
    'EVE' : [] ,
    'MEDIA' : []} ,
'relation' :
    [['吳王闔閭', '是', '孫武'],
    ['孫武','很有','貢獻'],
    ['孫武','是','齊人'],
    ['孫王','是','齊人'],
    ['孫武','是','將軍'],
    ['齊王','是','老王'],
    ]
}

sub_test_data2 = { 'named entity' :
    { 'LOC': ['古城'] ,
    'ORG' : [] ,
    'PER': ['吳王' , '孫子'] , # redundent data
    'EVE' : ['兵臨城下'] ,
    'MEDIA' : ['孫子兵法']} ,
'relation' :
    [
    ['孫武','在','古城'],  # cross data
    ['吳王','在','古城'], 
    ['孫武','遇到','兵臨城下'],
    ]
}

edge_test_data = { 'named entity' :
    { 'LOC': [''] ,
    'ORG' : [] ,
    'PER': [ '孫子'] , # redundent data
    'EVE' : ['兵臨城下'] ,
    'MEDIA' : ['孫子兵法']} ,
'relation' :
    [
    ['孫武','在'],  # cross data
    ['吳王','古城'], 
    ['孫武','遇到','兵臨城下'],
    ]
}


test_data = [sub_test_data1 , sub_test_data2]
test_data_with_empty_dict = [sub_test_data1 , sub_test_data2 , {} , {'relation' : []} ]
test_data_with_edge_case =  [sub_test_data1 , sub_test_data2 , edge_test_data]
print(test_data)


def extract_entity_data(raw_data : list):
    entity_data = { 'LOC': [] ,
        'ORG' : [] ,
        'PER': [] ,
        'EVE' : [] ,
        'MEDIA' : [] , 
        'attribute' : []
        } 
    for sentence_data in raw_data:
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
                if not(relation_ele in entity_list['attribute']) : 
                    entity_list['attribute'].append(relation_ele[2])

            if relation_ele[2] in all_entity and not(relation_ele[0] in all_entity):
                all_attr.append(relation_ele)
                if not(relation_ele in entity_list['attribute']) : 
                    entity_list['attribute'].append(relation_ele[0])
    return all_attr

def is_entity_in_relation(entity :str , relation_list  : list):
    for relation_ele in relation_list:
        if entity == relation_ele[0] or entity == relation_ele[2]:
            return True 
    return False


# =====  main  =====

entity_data = GPT_NER_RE.extract_entity_data(test_data)
# print(entity_data)


# filter out 'relation' , which both has entity tag

# print("relation")
relation_data = GPT_NER_RE.extract_relation(test_data, entity_data)
# print(relation_data)
#  filter out 'attribute' , which only one side has entity
# print("Attr")
attr_data = GPT_NER_RE.extract_attr_and_find_attr(test_data , entity_data)
# print(attr_data)

relation_list = [['head', 'relation', 'tail']]
for relation_ele in relation_data:
    relation_list.append(relation_ele)
for relation_ele in attr_data:
    relation_list.append(relation_ele)

print(relation_list)




# try:
pattern = r"\{.*\}"
match = re.search(pattern, raw_data, re.DOTALL)

if match:

    dict_string = match.group(0)


    GPT_result = ast.literal_eval(dict_string)  # change GPT massage string as list
    # print(GPT_result.type)
    # print(GPT_result)
# except:
#     print("exception")




# 開啟CSV檔案並將內容清空
with open(output_relation_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([])  # 寫入空白的一列，即清空CSV檔案內容


with open(output_relation_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    # print(relation_list)
    try:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(relation_list)
    except:
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
    except:
        print('csv encoding error')

# test_case2 : data with empty dict

specific_keys = ['named entity', 'relation']

test_data_with_empty_dict = [d for d in test_data_with_empty_dict if all(key in d for key in specific_keys)]

# test_case 3 : data w/ relation below 3 ele
print(test_data_with_edge_case)
for sentence_relation in test_data_with_edge_case : 
    # print("sentence_relation")
    # print(sentence_relation)
    sentence_relation['relation'] = [sublist for sublist in sentence_relation['relation'] if len(sublist) >= 3]
print(test_data_with_edge_case)


# test_case 4 : find and delete entity which is not in any relation or has no attr

for key ,  entity_list in entity_data.items() :
    delete_idx = []
    for i , entity_ele in enumerate(entity_list) : 
        if is_entity_in_relation(entity_ele , relation_list) : 
            continue
        delete_idx.append(i)
    
    # delete entity
    new_entity_list = [entity_list[i]  for i  in range(len(entity_list)) if i not in delete_idx]
    entity_data[key] = new_entity_list


end_time = time.time()
print("結束時間 : " , time.ctime(end_time))