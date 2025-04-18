import os
import logging
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tqdm import tqdm
import sys
import random
import string
import io

# Исправление кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("log-generation.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def generate_random_name(min_length=3, max_length=10):
    """Генерация случайного имени файла из букв."""
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(string.ascii_lowercase, k=length)) + '.jpg'

def download_image(index, output_dir):
    """Скачивание одного изображения с Lorem Picsum."""
    try:
        random_name = generate_random_name()
        logger.info(f"Downloading image {index + 1} as {random_name}")
        url = f"https://picsum.photos/1080/1080?random={index}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        output_path = os.path.join(output_dir, random_name)
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.info(f"Image {index + 1} saved: {output_path}")
        return random_name  # Возвращаем имя для ZIP
    except Exception as e:
        logger.error(f"Error downloading image {index + 1}: {str(e)}")
        return None

def main(num_images):
    """Основная функция для загрузки изображений."""
    start_time = datetime.now()
    logger.info(f"Starting download of {num_images} images...")

    # Создание папки
    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Многопоточная загрузка с прогресс-баром
    image_names = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_image, i, output_dir) for i in range(num_images)]
        for future in tqdm(futures, desc="Downloading images", unit="image"):
            result = future.result()
            if result:
                image_names.append(result)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Download completed. Total time: {elapsed_time}")

if __name__ == "__main__":
    # Настройка количества изображений
    parser = argparse.ArgumentParser(description="Download random images from Lorem Picsum")
    parser.add_argument("--num_images", type=int, default=10, help="Number of images to download")
    args = parser.parse_args()

    try:
        main(args.num_images)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")