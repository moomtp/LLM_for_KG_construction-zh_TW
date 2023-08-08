# LLM_for_KG_construction-zh_TW
Knowledge graph construction based on LLM


# installation
1. 安裝ckiptagger : https://github.com/ckiplab/ckiptagger#installation
2. 下載ckiptagger的model到目錄的data資料夾中(一樣參照上面的網站)
3. 安裝openai的api


# Usage
1. 在GPT_key.txt中放入GPT API_key的資料
2. 確定sentences.csv中放入需要的句子data
3. run NER.py將句子的實體找出並存成sentence_entities.json
4. run GPT_extraction.py將句子的關係抽出