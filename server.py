from flask import Flask, redirect, url_for, render_template, session, \
                  make_response, flash, jsonify, request
from flask_bootstrap import Bootstrap
from collections import Counter, defaultdict
from random import choice
import subprocess
import json
import re
import argparse
import time

# TODO switch to HTTP POST from GET
# TODO implement tree visualisation

app = Flask(__name__)
Bootstrap(app)


def rec_dd():
    """Function to create a nested defaultdict

    :returns: a nested defaultdict
    :rtype: defaultdict
    """
    return defaultdict(rec_dd)


def get_output(query, lower, ignchar):
    """Function to fetch and parse the output of spimi

    :params:
    :query: the word to call spimi-retrieve with
    :lower: whether the returned text should be lowercased or not
    :ignchar: whether punctuation characters will be removed or not

    :returns: tuple of (query, list of sentences)
    :rtype: tuple
    """
    output = subprocess.check_output(['../bin/spimi-retrieve',
                                      'H',
                                      '--i', '../bin/var/',
                                      '--ngram', query])
    output = output.decode('utf8', 'ignore')
    print(query, 'output type: ', type(output))
    if lower != 'undefined':
        output = output.lower()
        query = query.lower()
    if ignchar != 'undefined':
        output = re.sub('[^a-zA-Z0-9\n\.]', ' ', output)
        sentences = output.split('\n')
        sentences = [sent for sent in sentences if query in sent]
    else:
        output = ' '.join(re.split(r'(\W)', output))
        output = re.sub(r' +', ' ', output)
        sentences = re.split('\n', output)
    return query, sentences


@app.route('/spimi/api/get_freq_after', methods=['GET'])
def return_freq_after():
    """Return the 50 most frequent words succeding the query, their frequency,
       and a random sample, containing the query as well as
       it's left and right context.

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json string
    """
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    # getting output
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    after_count = Counter()
    for sentence in sentences:
        # double check since spimi bugged out a few times
        if query in sentence:
            qhit = sentence.index(query)
            qlen = len(query)
            # determine parts of sentence and convert it to list
            qpart = [sentence[qhit:qhit+qlen]]
            prepart = sentence[:qhit].split()
            aftpart = sentence[qhit+qlen:].split()
            sentence = prepart + qpart + aftpart
            # Need to index again since we had to take care of multiword requests
            # and the sentence was meanwhile converted to a list
            qhit = sentence.index(query)
            ahit = sentence.index(query)+1
            if ahit < (len(sentence)):
                after = sentence[ahit]
                after_count.update([after])
                wic = (' '.join(prepart), query, ' '.join(aftpart))
                if after not in words.keys():
                    words[after] = set()
                    words[after].add((wic))
                else:
                    words[after].add((wic))
    to_return = []
    for word, count in after_count.most_common(50):
        sent = choice(list(words[word]))
        to_return.append({'word': word,
                          'freq': count,
                          'sent': sent})
    return(json.dumps(to_return))


@app.route('/spimi/api/get_freq_prev', methods=['GET'])
def return_freq_prev():
    """Return the 50 most frequent words preceding the query, their frequency,
       and a random sample that contains an example containing the query as well
       as it's left and right context

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json string
    """
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    prev_count = Counter()
    for sentence in sentences:
        if query in sentence:
            qhit = sentence.index(query)
            qlen = len(query)
            if qhit > 0:
                qpart = [sentence[qhit:qhit+qlen]]
                aftpart = sentence[qhit+qlen:].split()
                prepart = sentence[:qhit].split()
                sentence = prepart + qpart + aftpart
                qhit = sentence.index(query)
                prehit = sentence.index(query)-1
                prev = sentence[prehit]
                prev_count.update([prev])
                wic = (' '.join(prepart), query, ' '.join(aftpart))
                if prev not in words.keys():
                    words[prev] = set()
                    words[prev].add((wic))
                else:
                    words[prev].add((wic))
    to_return = []
    for word, count in prev_count.most_common(50):
        sent = choice(list(words[word]))
        to_return.append({'word': word,
                          'freq': count,
                          'sent': sent})
    return(json.dumps(to_return))

@app.route('/spimi/api/get_cooc', methods=['GET', 'POST'])
def return_cooc():
    """Returns the 50 most frequent words coocurring the query,
       their frequency as well as a random sample containing the query,
       its left and right context.

       :returns nested list of [dict(word, frequency, sent)]:
       :rtype: json string
       """
    starttime = time.clock()
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    charlen = int(request.args.get('charlen', 255))
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    cont_count = Counter()
    for sentence in sentences:
        if query in sentence:
            qhit = sentence.index(query)
            qlen = len(query)
            qpart = [sentence[qhit:qhit+qlen]]
            borderleft = max(0, qhit-charlen)
            while sentence[max(0, borderleft)] != " ":
                borderleft += 1
            borderright = min(qhit+qlen+charlen, len(sentence)-1)
            while sentence[min(len(sentence)-1, borderright)] != " ":
                borderright -= 1
            prepart = sentence[borderleft:qhit].split()
            aftpart = sentence[qhit+qlen:borderright].split()
            sentence = prepart + qpart + aftpart
            qhit = sentence.index(query)
            for word in sentence:
                if word != query:
                    cont_count.update([word])
                wic = (' '.join(prepart), query, ' '.join(aftpart))
                if word not in words.keys():
                    words[word] = set()
                    words[word].add((wic))
                else:
                    words[word].add((wic))
    to_return = []
    for word, count in cont_count.most_common(50):
        sent = choice(list(words[word]))
        to_return.append({'word': word,
                          'freq': count,
                          'sent': sent
                          })

    endtime = time.clock()
    print("request complete, this took: ", endtime - starttime, "seconds")
    return(json.dumps(to_return))


@app.route('/spimi/interface')
# Initial call to the interface
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
