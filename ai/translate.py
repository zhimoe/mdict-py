from transformers import MarianTokenizer, MarianMTModel
import os
from typing import List


class Translator():
    def __init__(self, models_dir):
        self.models = {}
        self.models_dir = models_dir

    def get_supported_langs(self):
        routes = [x.split('-')[-2:] for x in os.listdir(self.models_dir)]
        return routes

    def load_model(self, route):
        model = f'opus-mt-{route}'
        path = os.path.join(self.models_dir, model)
        try:
            model = MarianMTModel.from_pretrained(path)
            tok = MarianTokenizer.from_pretrained(path)
        except:
            return 0, f"Make sure you have downloaded model for {route} translation"
        self.models[route] = (model, tok)
        return 1, f"Successfully loaded model for {route} transation"

    def translate(self, source, target, text):
        route = f'{source}-{target}'
        if not self.models.get(route):
            success_code, message = self.load_model(route)
            if not success_code:
                return message
        # todo: the prepare_seq2seq_batch is deprecated
        batch = self.models[route][1].prepare_seq2seq_batch(src_texts=list([text]), return_tensors="pt")
        gen = self.models[route][0].generate(**batch)
        words: List[str] = self.models[route][1].batch_decode(gen, skip_special_tokens=True)
        return words
