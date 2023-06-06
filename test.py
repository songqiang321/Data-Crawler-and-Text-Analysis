from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModelForSeq2SeqLM
from transformers import pipeline
import torch

def model_compute(sentence):
    # Translate Chinese sentence into English
    batch = tokenizer_zh2en([sentence], return_tensors="pt")
    generated_ids = model_zh2en.generate(**batch)
    tokenizer_zh2en.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Detect whether the sentence is related to climate risk
    inputs = tokenizer_climatebert(tokenizer_zh2en.batch_decode(generated_ids, skip_special_tokens=True)[0], return_tensors="pt")
    with torch.no_grad():
        logits = model_climatebert(**inputs).logits
    predicted_class_id = logits.argmax().item()
    return model_climatebert.config.id2label[predicted_class_id]

if __name__ == '__main__':
    
    tokenizer_climatebert = AutoTokenizer.from_pretrained("climatebert/distilroberta-base-climate-detector")
    model_climatebert = AutoModelForSequenceClassification.from_pretrained("climatebert/distilroberta-base-climate-detector")

    tokenizer_zh2en = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en", use_fast=False)
    model_zh2en = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en")