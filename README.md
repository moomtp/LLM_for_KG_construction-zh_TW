# LLM_for_KG_construction-zh_TW
Knowledge graph construction based on LLM


# Installation
1. 安裝ckiptagger : https://github.com/ckiplab/ckiptagger#installation
2. 下載ckiptagger的model到目錄的data資料夾中(一樣參照上面的網站)
3. 安裝openai的api


# Usage
## 1. NER by ckiptagger, relation extraction by GPT

1. 在GPT_key.txt中放入GPT API_key的資料
2. 確定sentences.csv中放入需要的句子data
3. run NER.py將句子的實體找出並存成sentence_entities.json
4. run GPT_extraction.py將句子的關係抽出

## 2. NER, relation extraction by GPT
1. 直接使用GPT_NER_RE中定義的function即可
```python
import GPT_NER_RE

relation_and_entity = GPT_NER_RE.GPT_extraction_list_and_NER(sentence_list) 

```