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
    print(query)
    output = subprocess.check_output(['../bin/spimi-retrieve',
                                      'H',
                                      '--i', '../bin/var/',
                                      '--ngram', query])
    output = output.decode('utf8')
    if lower != 'undefined':
        output = output.lower()
        query = query.lower()
    if ignchar != 'undefined':
        output = re.sub('[^a-zA-Z0-9\n]', ' ', output)
        sentences = output.split('\n')
    else:
        output = ' '.join(re.split(r'(\W)', output))
        output = re.sub(r' +', ' ', output)
        sentences = re.split('\n', output)
    return query, sentences


def mark_sentence(qpos, word, sentence):
    sent_before= ' '.join(['<span class=\"wmatch\">'
                         + word + '</span>'
                         if word == w else w for w in sentence[:qpos]])
    sent_after= ' '.join(['<span class=\"wmatch\">'
                         + word + '</span>'
                         if word == w else w for w in sentence[qpos+1:]])
    return sent_before, sent_after



@app.route('/spimi/api/get_freq_after', methods=['GET'])
def return_freq_after():
    """Return the 50 most frequent words succeding the query, their frequency,
       and a random sample that contains an example containing the query,
       it's left and right context where the query as well as the current
       most word per line is highlighted
       (marked with qmatch and colored with css)

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json
    """
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    after_count = Counter()
    for sentence in sentences:
        if query in sentence:
            qhit = sentence.index(query)
            qlen = len(query)
            qpart = [sentence[qhit:qhit+qlen]]
            prepart = sentence[:qhit].split()
            aftpart = sentence[qhit+qlen:].split()
            sentence = prepart + qpart + aftpart
            # Need to index again since we had to take care of multiword requests
            qhit = sentence.index(query)
            ahit = sentence.index(query)+1
            if ahit < (len(sentence)):
                after = sentence[ahit]
                after_count.update([after])
                # Need to do the following lines to highlight the words in
                # the html document, this will be found in the preceding
                # functions as well
                sent_before, sent_after = mark_sentence(qhit, after, sentence)
                wic = [sent_before, query, sent_after]
                if after not in words.keys():
                    words[after] = [wic]
                sent_before = ' '.join(sentence[:qhit])
                wic = [sent_before, query, sent_after]
                if after not in words.keys():
                    words[after] = [wic]
                elif wic not in words[after]:
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
    """Return the 50 most frequent words preceding the query, their frequency,
       and a random sample that contains an example containing the query,
       it's left and right context where the query as well as the
       current word per line is highlighted
       (marked with qmatch and colored with css)

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json
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
                sent_before, sent_after = mark_sentence(qhit, prev, sentence)
                wic = [sent_before, query, sent_after]
                if prev not in words.keys():
                    words[prev] = [wic]
                elif wic not in words[prev]:
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
    """Returns the 50 most frequent words coocurring the query,
       their frequency as well as a random sample containing the query,
       its left and right context, where the query as well as the coocurring
       word is highlighted

       :returns nested list of [dict(word, frequency, sent)]:
       :rtype: json
       """
    query = request.args.get('q', '')
    lowercase = request.args.get('lower', False)
    ignchar = request.args.get('strip', False)
    query, sentences = get_output(query, lowercase, ignchar)
    words = rec_dd()
    cont_count = Counter()
    for sentence in sentences:
        if query in sentence:
            sentlen = len(sentence)
            qhit = sentence.index(query)
            qlen = len(query)
            qpart = [sentence[qhit:qhit+qlen]]
            prepart = sentence[:qhit].split()
            aftpart = sentence[qhit+qlen:].split()
            sentence = prepart + qpart + aftpart
            qhit = sentence.index(query)
            for word in sentence:
                cont_count.update([word])
                sent_before, sent_after = mark_sentence(qhit, word, sentence)
                wic = [sent_before, query, sent_after]
                if word not in words.keys():
                    words[word] = [wic]
                elif wic not in words[word]:
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
    pass

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
