import nltk
nltk.download('punkt')
from nltk import sent_tokenize, word_tokenize
import math

from model.config import *
import numpy as np
from keras_preprocessing.sequence import pad_sequences
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

def create_attention_mask(input_ids):
  attention_masks = []
  for sent in input_ids:
    att_mask = [int(token_id > 0) for token_id in sent]  # create a list of 0 and 1.
    attention_masks.append(att_mask)  # basically attention_masks is a list of list
  return attention_masks

def extractive_sum(text):
    # Extractive summarization
    paragraph_split = sent_tokenize(text)
    input_tokens = []
    for i in paragraph_split:
        input_tokens.append(tokenizer.encode(i, add_special_tokens=True))
    
    temp = []
    for i in input_tokens:
        temp.append(len(i))

    input_ids = pad_sequences(input_tokens, maxlen=100, dtype="long", value=0, truncating="post", padding="post")
    input_masks = create_attention_mask(input_ids)
    
    #creating a tensor for input_ids and input_masks
    input_ids = torch.tensor(input_ids, dtype=torch.long)
    input_masks = torch.tensor(input_masks, dtype=torch.long)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=input_masks)

    encoder_output = outputs.encoder_last_hidden_state
    sentence_features = encoder_output[:,0,:].detach().numpy()

    sent_count = len(paragraph_split)

    topic_answer = []
    word_count = len(word_tokenize(text))

    number_extract = 14 #default value
    if word_count<1024:
        number_extract = math.ceil(sent_count*0.8)
    elif word_count>1024 and word_count<1800:
        number_extract = math.ceil(sent_count*0.6)
    else:
        number_extract = math.ceil(sent_count*0.4)

    kmeans = KMeans(n_clusters=number_extract, 
                    random_state=0).fit(sentence_features)
    cluster_center = kmeans.cluster_centers_

    nbrs = NearestNeighbors(n_neighbors= 1, 
                        algorithm='brute').fit(sentence_features)
    distances, indices = nbrs.kneighbors(
                    cluster_center.reshape(number_extract,-1))

    indices = np.sort(indices.reshape(1,-1))
    for i in indices[0]:
        topic_answer.append(paragraph_split[i])
    return topic_answer

def abstractive_sum(text):
    # Abstractive summarization
    input_ids = tokenizer(
        text, max_length=1024,
        truncation=True, padding='max_length',
        return_tensors='pt'
    ).to(device)

    summaries = model.generate(
        input_ids=input_ids['input_ids'],
        attention_mask=input_ids['attention_mask'],
        max_length=512,
        min_length=256
    )
    decoded_summaries = [tokenizer.decode(s, skip_special_tokens=True, clean_up_tokenization_spaces=True) for s in summaries]
    return decoded_summaries

def summarize(text):
    topic_answer = extractive_sum(text)
    extracted_text = ' '.join(topic_answer)
    abstractive_answer = abstractive_sum(extracted_text)
    sentences = sent_tokenize(abstractive_answer[0])
    num_of_sents = len(sentences)
    generated_sentences = {}
    sent_per_slide = 3
    num_of_slides = math.ceil(num_of_sents/sent_per_slide)
    k=0
    for i in range(num_of_slides):
        generated_sentences[i] = sentences[k:k+sent_per_slide]
        k=k+sent_per_slide

    return generated_sentences
