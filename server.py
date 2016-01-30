from flask import Flask, redirect, url_for, render_template, session, \
                  make_response, flash, jsonify, request
from flask_bootstrap import Bootstrap
from collections import Counter, defaultdict
import subprocess
import json
import re

#TODO configuration via Make
#TODO implement tree visualisation
#TODO improve api by passing list of hits instead of html code

app = Flask(__name__)
Bootstrap(app)

def rec_dd():
    return defaultdict(rec_dd)

def get_output(query):
    output = subprocess.check_output(['./bin/spimi-retrieve',
                                      'H',
                                      '--i', './bin/var/',
                                      '--ngram', query])
    output = re.sub('[^a-zA-Z0-9\n\.]', ' ', output)
    sentences = output.decode('utf-8').split('\n')
    return sentences

@app.route('/spimi/api/get_freq_after', methods=['GET'])
def return_freq_after():
    """Return the 50 most frequent words and 20 corresponding sentences
       at the left side of the current query. As well as the sentences
       containing these at the correct position and the frequency

       :returns: nested list of [dict(word, frequency, sent)]:
       :rtype: json"""
    query = request.args.get('q', '')
    sentences = get_output(query)
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
                sentence[ahit] = ('<span class=\"wmatch\">' + sentence[ahit]
                                    + '</span>')
                sentence[qhit] = ('<span class=\"qmatch\">' + sentence[qhit]
                                    + '</span>')
                if after not in words.keys():
                    words[after] = [sentence]
                else:
                    words[after].append(sentence)
    to_return = []
    for word, count in after_count.most_common(50):
        for idx, sent in enumerate(words[word]):
            if idx < 20:
                sent = ' '.join(sent)
                to_return.append({'word': '<span class=\"wmatch\">' + word + '</span>',
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
    sentences = get_output(query)
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
                sentence[prehit] = ('<span class=\"wmatch\">' + sentence[prehit]
                                    + '</span>')
                sentence[qhit] = ('<span class=\"qmatch\">' + sentence[qhit]
                                    + '</span>')
                if prev not in words.keys():
                    words[prev] = [sentence]
                else:
                    words[prev].append(sentence)
    to_return = []
    for word, count in prev_count.most_common(50):
        for idx, sent in enumerate(words[word]):
            if idx < 20:
                sent = ' '.join(sent)
                to_return.append({'word': '<span class=\"wmatch\">' + word + '</span>',
                                'freq': count,
                                'sent': sent})
    return(json.dumps(to_return))

@app.route('/spimi/api/get_cooc', methods=['GET'])
def return_cooc():
    """Returns sentences containing query as well as a second word

       :returns nested list of [dict(word, frequency, sent)]:
       """
    query = request.args.get('q', '')
    query, cooc = query.split(';')
    sentences = get_output(query)
    words = rec_dd()
    cooc_count = Counter()
    for sentence in sentences:
        sentence = sentence.split()
        if query in sentence and cooc in sentence:
            cooc_count.update([cooc])
            qhit = sentence.index(query)
            chit = sentence.indext(cooc)
            sentence[chit] = ('<span class=\"wmatch\">' + sentence[prehit]
                                + '</span>')
            sentence[qhit] = ('<span class=\"qmatch\">' + sentence[qhit]
                                + '</span>')
            if cooc not in words.keys():
                words[cooc] = [sentence]
            else:
                words[cooc].append(sentence)
    to_return = []
    for word, count in cooc_count.most_common(50):
        for idx, sent in enumerate(words[word]):
            if idx < 20:
                sent = ' '.join(sent)
                to_return.append({'word': '<span class=\"wmatch\"' + word + '<span>',
                                  'freq': count,
                                  'sent': sent})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10800,debug=True)
