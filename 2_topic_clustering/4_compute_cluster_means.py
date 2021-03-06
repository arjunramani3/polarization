#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from nltk.cluster import KMeansClusterer
import nltk
import json
import random
from nltk.cluster.util import cosine_distance

config = json.load(open('../config.json', 'r'))
INPUT_DIR = config['INPUT_DIR']
OUTPUT_DIR = config['OUTPUT_DIR']
TWEET_DIR = config['TWEET_DIR']
NUM_CLUSTERS = config['NUM_CLUSTERS']
RNG = random.Random()
RNG.seed(config['SEED'])
events = open(INPUT_DIR + 'event_names.txt', 'r').read().splitlines()


print('loading...')

# use a joint sample of embeddings from each event to determine the cluster centroids
def get_samples():
    tweet_embeds = ''
    for event in events:
        embeds = np.load(TWEET_DIR + event + '/' + event + '_embeddings_partisan.npy')
        indices = np.load(TWEET_DIR + event + '/' + event + '_indices_among_embeddings_for_getting_topics.npy')
        embeds = embeds[indices, :]
        if len(tweet_embeds) == 0:
            tweet_embeds = embeds
        else:
            tweet_embeds = np.vstack([tweet_embeds, embeds])

    return tweet_embeds

tweet_embeds = get_samples()

print(tweet_embeds.shape)
print(NUM_CLUSTERS)
kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=1, rng=RNG)

print('clustering...')
assigned_clusters = kclusterer.cluster(tweet_embeds, assign_clusters=True)

means = np.array(kclusterer.means())

print('calculating sum of distances...')
sum_dists = []
for i, c in enumerate(assigned_clusters):
    sum_dists.append(cosine_distance(means[c], tweet_embeds[i]))
print(np.mean(sum_dists))  # the smaller, the better


print('saving...')
np.save(OUTPUT_DIR +'/cluster_'+str(NUM_CLUSTERS)+'_means.npy', means)
