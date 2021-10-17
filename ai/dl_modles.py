import os
from urllib.request import urlretrieve

FTP_BASE_URL = 'https://s3.amazonaws.com/models.huggingface.co/bert/Helsinki-NLP'
FILE_NAMES = ['config.json', 'source.spm', 'target.spm', 'tokenizer_config.json', 'vocab.json', 'pytorch_model.bin']
DATA_PATH = 'data'


def download_language_model(source, target):
    """从ftp下载model"""
    model = f"opus-mt-{source}-{target}"
    print(">>>Downloading data for %s to %s model..." % (source, target))
    model_save_folder = os.path.join(os.getcwd(), DATA_PATH, model)
    from pathlib import Path
    Path(model_save_folder).mkdir(parents=True, exist_ok=True)
    for f in FILE_NAMES:
        model_path = os.path.join(model_save_folder, f)
        if os.path.exists(model_path):
            print(f"model file {f} exists, skip...")
            continue
        try:
            print(os.path.join(FTP_BASE_URL, model, f))
            print(f">>>Saving model file {f} in: {model_path}")
            urlretrieve(
                "/".join([FTP_BASE_URL, model, f]),
                model_path,
            )
            print("Download complete!")
        except:
            print("Error retrieving model from url. Please confirm model exists.")
            break


def download_models():
    download_language_model('zh', 'en')
    download_language_model('en', 'zh')


if __name__ == '__main__':
    download_models()
