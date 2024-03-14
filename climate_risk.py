from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, pipeline
from tqdm.auto import tqdm
import os
import openpyxl
import logging


def main(txt_path, result_path):

    tokenizer_climatebert = AutoTokenizer.from_pretrained("./model/distilroberta-base-climate-detector")
    model_climatebert = AutoModelForSequenceClassification.from_pretrained("./model/distilroberta-base-climate-detector")
    tokenizer_zh2en = AutoTokenizer.from_pretrained("./model/opus-mt-zh-en", use_fast=False)
    model_zh2en = AutoModelForSeq2SeqLM.from_pretrained("./model/opus-mt-zh-en")
    pipe1 = pipeline(task='translation', model=model_zh2en, tokenizer=tokenizer_zh2en, device=0, truncation=True)
    pipe2 = pipeline(task='text-classification', model=model_climatebert, tokenizer=tokenizer_climatebert, device=0, truncation=True)

    workbook = openpyxl.load_workbook(result_path)
    worksheet = workbook['Sheet1']
    iteration_counter = 0
    save_counter = 0

    txt_path = txt_path # './data/txt_clear/2021'
    txt_list = os.listdir(txt_path)
    # error_index = txt_list.index('2021_000039_中集集团.txt')
    # txt_list = txt_list[error_index + 1:]
    for txt_name in tqdm(txt_list, desc="Processing files"):
        try :
            with open(txt_path+'/'+txt_name, 'r', encoding='utf-8') as f:
                content = f.readlines()
                total_sentences = len(content)
                for i in range(total_sentences):
                    content[i] = content[i].replace('\n', '')
                en_text = [m['translation_text'] for m in pipe1(content)]
                result = pipe2(en_text)
                yes_elements = [item for item in result if item['label'] == 'yes']
                yes_sentences = len(yes_elements)
        except Exception as e:
            logging.error(f"处理 {txt_name}时出错： {e}")
            continue

        year, code, name = txt_name.replace('.txt', '').split('_')
        worksheet.append([code, name, year, total_sentences, yes_sentences])
        if iteration_counter % 100 == 0:
            save_counter += 1
            workbook.save(result_path)
            print(f"Saved iteration {save_counter}")
    # 在循环结束后，确保保存最后一次数据        
    if iteration_counter % 100 != 0:
        save_counter += 1
        workbook.save(result_path)
        print(f"Final save at iteration {save_counter}") 


if __name__ == "__main__":
    year = 2021
    logging.basicConfig(filename=f'cr_log.log', filemode='a', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    txt_path = f'./data/txt_clear/{year}'
    result_path = f'./data/result/{year}结果数据.xlsx'
    main(txt_path, result_path)