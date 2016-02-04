Readme for Spimi Interface

1. Clone this repository into the root directory of the spimi version you wish 
    to work with
2. Install requirements from requirements.txt via pip install -r requirements.txt
3. Compile spimi
4. Run ../bin/spimi/spimi-index - specify output to ../bin/var/
5. Run server.py (options: -port [int] -debug) -port defaults to 10800
6. Address the server in your browser by localhost:PORT/spimi/interface

    Available options in the spimi-interface:

        sort by following: will find the most frequent words AFTER your query
        and return these words as well as a random sentence with this constellation

        sort by previous: does the same as sort by folllowing but with the words
        left to your query

        coocurrence: will sort by tye most frequent words in the context of
        the query and show a random corresponding sentence

Caution: In the current setting, the server will be available to any client
in your current network. Be sure the PORT is not forwarded, except your wish to,
or start the server without the -debug option. Running the server with -debug
will enable anyone with access to the address to inject malicious code

