"""Module fot parsing text from pdf"""
import argparse
import json
import os
import sys

import easyocr
import numpy as np
from pdf2image import convert_from_path
from tqdm import tqdm


def get_text_from_pdf(pdf_path: str, output_json: str, lang: str = 'en'):
    """Function for extracting text from pdf file

    Args:
        pdf_path (str): Path to pdf
        output_json (str): Path to output json file
        lang (str, optional): Lang of text to extract. Defaults to 'eng'.
    """
    try:
        images = convert_from_path(pdf_path=pdf_path)
    except Exception as e:
        print(f'Ошибка при конвертировании PDF в изображения: {e}')
        sys.exit(1)

    extracted_text = {}
    total_pages = len(images)

    try:
        reader = easyocr.Reader(lang_list=[lang])
    except Exception as e:
        print(f'Ошибка инициализации EasyOCR: {e}')
        sys.exit(1)

    iterator = tqdm(
        enumerate(images),
        total=total_pages,
        desc="OCR Processing",
        unit="page",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    )

    for i, image in iterator:
        try:
            img_np = np.array(image)
            result = reader.readtext(img_np, detail=0)
            extracted_text[f'page_{i + 1}'] = result
        except Exception as e:
            print(f'Ошибка при обработке страницы {i + 1}: {e}')
            sys.exit(1)

    try:
        with open(output_json, 'w', encoding='utf-8') as file:
            json.dump(extracted_text, file, ensure_ascii=False, indent=4)
        print(f'Текст успешно сохранен в {output_json}')
    except Exception as e:
        print(f'Ошибка при записи JSON: {e}')
        sys.exit(1)


def parse_args():
    """Function for parsing console arguments"""
    parser = argparse.ArgumentParser(
        description='Извлечение текста из PDF файлов'
    )
    parser.add_argument('pdf_path', type=str, help='Путь к PDF файлу')
    parser.add_argument('--output', type=str, default='output.json',
                        help='Выходной JSON файл')
    parser.add_argument('--lang', type=str, default='en',
                        help='Язык OCR (например, en, ru)')
    return parser.parse_args()


def main():
    """Start function"""
    args = parse_args()

    if not os.path.exists(args.pdf_path):
        print(f'Файл {args.pdf_path} не найден')
        sys.exit(1)

    get_text_from_pdf(
        pdf_path=args.pdf_path,
        output_json=args.output,
        lang=args.lang
    )


if __name__ == "__main__":
    main()
