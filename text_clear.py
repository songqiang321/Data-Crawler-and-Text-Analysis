import json
from tqdm.auto import tqdm
import os
import logging

logging.basicConfig(filename=f'tc_log.log', filemode='a', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_text(txt_name, txt_path, save_path):
    str_clear = ''
    with open(txt_path+'/'+txt_name, 'r', encoding='utf-8') as f:
        try:
            content = f.readlines()
        except Exception as e:
            logging.error(f"处理 {txt_name}时出错： {e}")
            return

        for i in range(len(content)):
            json_str = json.loads(content[i])
            if json_str['type'] == 'text' and '。' in json_str['inside']: # json_str['inside'][-1] == '。' or len(json_str['inside'])>19
                str_clear = str_clear + json_str["inside"]
    sentences = str_clear.split('。')
    if sentences[-1] == '':
        sentences.pop()
    content_clear = [item + '。\n' for item in sentences]

    with open(save_path+'/'+txt_name, 'w', encoding='utf-8') as file:
        file.writelines(content_clear)



def main():
    txt_list = os.listdir(txt_path)
    for txt_name in tqdm(txt_list, desc="Processing files"):
        clear_text(txt_name, txt_path, save_path)


if __name__ == '__main__':
    year = 2021
    txt_path = f'./data/txt/{year}txt年报'
    save_path = f'./data/txt_clear/{year}'
    main()