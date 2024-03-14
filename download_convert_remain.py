import pandas as pd
import os
import multiprocessing
import pdfplumber
import logging
import re
from pdf2txt import PDFProcessor
 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename=f'dc_remain_log.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert(start_page, end_page, code, name, year, pdf_dir, txt_dir, flag_pdf):
    pdf_file_path = os.path.join(pdf_dir, re.sub(r'[\\/:*?"<>|]', '',f"{year}_{code:06}_{name}.pdf"))
    txt_file_path = os.path.join(txt_dir, re.sub(r'[\\/:*?"<>|]', '', f"{year}_{code:06}_{name}.txt"))
    
    try:
        
        processor = PDFProcessor(pdf_file_path)
        processor.process_pdf(start_page, end_page)
        processor.save_all_text(path=txt_file_path)
        processor.pdf.close() # 此处必须手动关闭pdf，因为PDFProcessor类定义中没有使用with
 
        logging.info(f"{txt_file_path} 已保存.")
 
    except Exception as e:
        logging.error(f"处理 {year}_{code:06}_{name}时出错： {e}")
    else:
        # 删除已转换的PDF文件，以节省空间
        if flag_pdf:
            os.remove(pdf_file_path)
            logging.info(f"{pdf_file_path} 已被删除.")
 
 
def main(remain_ecxel_path, pdf_dir, txt_dir, flag_pdf):
    print("程序开始运行，请耐心等待……")
    # 读取Excel文件
    try:
        df = pd.read_excel(remain_ecxel_path)
    except Exception as e:
        logging.error(f"读取失败，请检查路径是否设置正确，建议输入绝对路径 {e}")
        return    
 
    # 读取文件内容并存储为字典,content_dict是一个生成器
    content_dict = ((row['公司代码'], row['公司简称'], row['开始页码'], row['结束页码']) for _, row in df.iterrows())
 
    # 多进程下载PDF并转为TXT文件
    with multiprocessing.Pool() as pool:
        for code, name, start_page, end_page in content_dict:
            txt_file_name = f"{year}_{code:06}_{name}.txt"
            txt_file_path = os.path.join(txt_dir, txt_file_name)
            if os.path.exists(txt_file_path):
                logging.info(f"{txt_file_name} 已存在，跳过.")
            else:
                pool.apply_async(convert, args=(start_page, end_page, code, name, year, pdf_dir, txt_dir, flag_pdf))
               
        pool.close()
        pool.join()
 
 
if __name__ == '__main__':
    # 从excel文件中读取章节页码
    remain_ecxel_path = './data/excel/2021年报remain.xlsx'
    # 是否删除pdf文件，True为是，False为否
    flag_pdf = True
    # 是否批量处理多个年份，True为是，False为否
    Flag = False
    if Flag:
        #批量下载并转换年份区间
        for year in range(2004,2022):
            # ===========Excel表格路径，建议使用绝对路径，务必请自行修改！！！！！！！===========
            file_name = f"./data/excel/年报链接_{year}.xlsx"
            # 创建存储文件的文件夹路径，如有需要请修改
            pdf_dir = f'./data/pdf/{year}pdf年报'
            txt_dir = f'./data/txt/{year}txt年报'
            main(remain_ecxel_path,pdf_dir,txt_dir,flag_pdf)
            print(f"{year}年年报处理完毕，若报错，请检查后重新运行")
    else:
        #处理单独年份：
        #特定年份的excel表格，请务必修改。
        year = 2021
        file_name = f"./data/excel/年报链接_{year}.xlsx"
        pdf_dir = f'./data/pdf/{year}pdf年报'
        txt_dir = f'./data/txt/{year}txt年报'
        main(remain_ecxel_path, pdf_dir, txt_dir, flag_pdf)
        print(f"{year}年年报处理完毕，若报错，请检查后重新运行")