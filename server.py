from flask import Flask, redirect, url_for, render_template, session, \
                  make_response, flash, jsonify, request
from flask_bootstrap import Bootstrap
from collections import Counter, defaultdict
from random import choice
import subprocess
import json
import re
import argparse

# TODO configuration via Make
# TODO implement tree visualisation
# TODO improve api by passing list of hits instead of html code

app = Flask(__name__)
Bootstrap(app)


def rec_dd():
    return defaultdict(rec_dd)


def get_output(query, lower, ignchar):
    print(lower, ignchar)
    output = subprocess.check_output(['../bin/spimi-retrieve',
                                      'H',
                                      '--i', '../bin/var/',
                                      '--ngram', query])
    if lower != 'undefined':
        output = output.lower()
        query = query.lower()
    if ignchar != 'undefined':
        output = re.sub('[^a-zA-Z0-9\n]', ' ', output)
    sentences = output.decode('utf-8').split('\n')
    return query, sentences


@app.route('/spimi/api/get_freq_after', methods=['GET'])
def return_freq_after():
    """Return the 50 most frequent words and a random sentence that contains
       an example containing the query
       at the left side of the current query. As well as the sentences
       containing these at the correct position and the frequency

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json"""
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    after_count = Counter()
    for sentence in sentences:
        sentence = sentence.split()
        if query in sentence:
            qhit = sentence.index(query)
            pos = sentence[qhit]
            ahit = sentence.index(query)+1
            if ahit < (len(sentence)):
                after = sentence[ahit]
                after_count.update([after])
                sent_after= ' '.join(['<span class=\"qmatch\">' + after+ '</span>'
                                      if after == w else w for w in sentence[qhit+1:]])
                sent_before = ' '.join(sentence[:qhit])
                wic = [sent_before, query, sent_after]
                if after not in words.keys():
                    words[after] = [wic]
                else:
                    words[after].append(wic)
    to_return = []
    for word, count in after_count.most_common(50):
        sent = choice(words[word])
        to_return.append({'word': word,
                            'freq': count,
                            'sent': sent})
    return(json.dumps(to_return))


@app.route('/spimi/api/get_freq_prev', methods=['GET'])
def return_freq_prev():
    """Return the 50 most frequent words and 20 corresponding sentences
       at the left side of the current query. As well as the sentences
       containing these at the correct position and the frequency

       :returns: nested list of [dict(word, frequency, sent)]
       :rtype: json"""
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    prev_count = Counter()
    for sentence in sentences:
        sentence = sentence.split()
        if query in sentence:
            qhit = sentence.index(query)
            if qhit > 0:
                prehit = sentence.index(query)-1
                prev = sentence[prehit]
                prev_count.update([prev])
                sent_before = ' '.join(['<span class=\"qmatch\">' + prev + '</span>'
                                        if prev == w else w for w in sentence[:qhit]])
                sent_after = ' '.join(sentence[qhit+1:])
                wic = [sent_before, query, sent_after]
                if prev not in words.keys():
                    words[prev] = [wic]
                else:
                    words[prev].append(wic)
    to_return = []
    for word, count in prev_count.most_common(50):
        sent = choice(words[word])
        to_return.append({'word': word,
                            'freq': count,
                            'sent': sent})
    return(json.dumps(to_return))

@app.route('/spimi/api/get_cooc', methods=['GET', 'POST'])
def return_cooc():
    """Returns sentences containing query as well as a second word

       :returns nested list of [dict(word, frequency, sent)]:
       """
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    cont_count = Counter()
    for sentence in sentences:
        sentence = sentence.split()
        if query in sentence:
            qhit = sentence.index(query)
            for word in sentence:
                cont_count.update([word])
                sent_before = ' '.join(['<span class=\"qmatch\">' + word + '</span>'
                                        if word == w else w for w in sentence[:qhit]])
                sent_after= ' '.join(['<span class=\"qmatch\">' + word + '</span>'
                                        if word == w else w for w in sentence[qhit+1:]])
                wic = [sent_before, query, sent_after]
                if word not in words.keys():
                    words[word] = [wic]
                else:
                    words[word].append(wic)
    to_return = []
    for word, count in cont_count.most_common(50):
        sent = choice(words[word])
        to_return.append({'word': word,
                        'freq': count,
                        'sent': sent
                        })

    return(json.dumps(to_return))




@app.route('/spimi/api/build_tree', methods=['GET'])
def return_json():
    """Return a formatted JSON for usage with d3.tree() """
    query = request.args.get('q', '')
    sentences = get_output(query)
    sent_until_query = [sentence[:sentence.index(query)]
                        for sentence in sentences if query in sentence]
    sent_after_query = [sentence[sentence.index(query):] for sentence in
                        sentences if query in sentence]
    wordpos = rec_dd()
    #wordpos['name'] = query
    #wordpos['children'] = [dict()]
    #for sentence in sent_until_query:
    #    sentence = sentence.split()
    #    dictposition = wordpos['children']
    #    for idx, curr in enumerate(sentence):
    #        dictposition['name'] = curr
    #        dictposition['children'] = [dict()]
    #        if idx > 1:
    #            prev = sentence[sentence.index(curr)-1:sentence.index(curr)]
    #            for keys in (prev):
        #                dictposition = dictposition['children']

    for sentence in sent_until_query:
        sentence = sentence.split()
        for (idx, (prev, curr)) in enumerate(zip(sentence, sentence[1:])):
            if curr not in wordpos['prev'][idx].keys():
                wordpos['prev'][idx][curr] = set([prev])
            else:
                wordpos['prev'][idx][curr].update([prev])
    for sentence in sent_after_query:
        sentence = sentence.split()
        for (idx, (prev, curr)) in enumerate(zip(sentence, sentence[1:])):
            if curr not in wordpos['after'][idx].keys():
                wordpos['after'][idx][curr] = set([prev])
            else:
                wordpos['after'][idx][curr].update([prev])

    for idx in wordpos['prev'].keys():
#        wordpos['prev'][idx]['Counts'] = Counter(wordpos['prev'][idx].keys())
        for word in wordpos['prev'][idx].keys():
            wordpos['prev'][idx][word] = list(wordpos['prev'][idx][word])
    for idx in wordpos['after'].keys():
#        wordpos['after'][idx]['Counts'] = Counter(wordpos['after'][idx].keys())
        for word in wordpos['after'][idx].keys():
            wordpos['after'][idx][word] = list(wordpos['after'][idx][word])

    return jsonify(wordpos)


@app.route('/spimi/api/test', methods=['GET'])
def parse_search():
    return render_template('interface.html')


@app.route('/spimi/interface')
def test_interface():
    return render_template('interface.html')

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', type=int, default=10800)
    parser.add_argument('-debug', action='store_true', default=False)
    return parser

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port ,debug=args.debug)
