"""
Script for building resources:

1. Downloading Kaggle data.
2. Building preprocessor and pickling for later use.
3. Building topic models and pickling for later use.

"""
import os
import sys
import pickle
import argparse

import pandas as pd
import time

sys.path.append("../libraries")
sys.path.append("news_analyzer/libraries")
import configs # noqa
import text_processing # noqa
import topic_modeling # noqa
import nytimes_article_retriever # noqa

# Module Constants
KAGGLE_COMP = "all-the-news"
# Change to include fewer csv files if desired
CSV_NAMES = ["articles1.csv", "articles2.csv", "articles3.csv"]
RESOURCE_PATH = "../" + configs.RESOURCE_FOLDER
FPATHS = [RESOURCE_PATH + "/" + name for name in CSV_NAMES]
CONTENT_COLUMN = "content"
MIN_WORDS_IN_ARTICLE = 200
# Topic Modeling Constants
BAD_GUIDED_TOPICS = ['national', 'nyregion', 'obituaries']
GUIDED_TOPICS_CONFIDENCE = 0.5
N_ITERATIONS = 100
RANDOM_STATE = 0
REFRESH = 20


def get_files():
    """ Function for downloading Kaggle files (see CSV_NAMES in module header),
        removing short articles (potential ads), and combining into one
        large table.
    """
    os.system("kaggle datasets download -d \
                snapcrack/all-the-news --force -p '{}'".
              format(configs.RESOURCE_PATH))

    list_of_tables = []
    for fpath in FPATHS:
        print(fpath)
        list_of_tables.append(pd.read_csv(fpath, encoding='utf8'))

    full_table = pd.concat(list_of_tables)
    article_lengths = \
        full_table[CONTENT_COLUMN].apply(lambda x: len(x.split()))
    full_table = full_table[article_lengths > MIN_WORDS_IN_ARTICLE]
    full_table.to_csv(configs.CORPUS_PATH, index=False)
    return full_table


if __name__ == "__main__":
    """ Main script used to download Kaggle files, preprocessing data,
        and builds topic models. All resources will be saved in the resources
        folder as csv files (data) or .pkl (objects).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_files',
                        dest='download_files',
                        action='store_true',
                        required=False)
    parser.set_defaults(download_files=False)
    args = parser.parse_args()
    download_files = args.download_files

    # If corpus csv does not exist download and build.
    print('checking if dataset exists...')
    if not os.path.isfile(configs.CORPUS_PATH) or download_files:
        print('dataset not found, downloading from Kaggle...')
        full_table = get_files()
    else:
        print('dataset found!')
        full_table = pd.read_csv(configs.CORPUS_PATH)

    # Fit preprocessor
    print('fitting preprocessor...')
    s_time = time.time()
    processor = text_processing.ArticlePreprocessor()
    processor.fit(full_table[CONTENT_COLUMN])
    e_time = time.time()
    dtm_time = round(e_time - s_time, 3)
    print('fitting complete in {}s! saving the document-term-matrix...'.format(
        dtm_time))
    with open(configs.PREPROCESSOR_PATH, 'wb') as file_handle:
        pickle.dump(processor, file_handle)
    dtm = processor.transform(full_table[CONTENT_COLUMN])
    vocab, word2id = topic_modeling.get_vocab(dtm)

    # Get nyt seed topics
    print('accessing NYT API...')
    topics_raw = nytimes_article_retriever.get_nytimes_topic_words()
    topics_clean = topic_modeling.clean_topics(topics_raw,
                                               word2id,
                                               BAD_GUIDED_TOPICS)
    seed_topics = topic_modeling.get_seed_topics(topics_clean,
                                                 word2id)

    # Fit guided LDA model
    s_time = time.time()
    n_guided_topics = len(topics_clean)
    print('fitting guided LDA model with {} topics...'.format(
        n_guided_topics))
    guidedlda_model = topic_modeling.TopicModeler(n_guided_topics,
                                                  N_ITERATIONS,
                                                  RANDOM_STATE,
                                                  REFRESH)
    guidedlda_model = guidedlda_model.fit(dtm,
                                          seed_topics,
                                          GUIDED_TOPICS_CONFIDENCE)
    # Fit unguided LDA model
    n_unguided_topics = int(len(dtm)/100)
    print('fitting unguided LDA model using {} topics...'.format(
        n_unguided_topics))
    unguidedlda_model = topic_modeling.TopicModeler(n_unguided_topics,
                                                    N_ITERATIONS,
                                                    RANDOM_STATE,
                                                    REFRESH)
    unguidedlda_model = unguidedlda_model.fit(dtm)
    e_time = time.time()

    # Save results
    print('model building complete. total training time: {}s'.format(
        round(e_time - s_time, 3)))
    print('saving pkl files...')
    # unguided model is large, so get rid of extra matrices
    unguidedlda_model.purge_extra_matrices()
    with open(RESOURCE_PATH + 'guidedlda_model.pkl', 'wb') as file_handle:
        pickle.dump(guidedlda_model, file_handle)
    with open(RESOURCE_PATH + 'unguidedlda_model.pkl', 'wb') as file_handle:
        pickle.dump(unguidedlda_model, file_handle)
    with open(RESOURCE_PATH + "preprocessor.pkl", "wb") as file_handle:
        pickle.dump(processor, file_handle)
