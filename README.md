Readme for Spimi Interface

1. Compile spimi
2. Run ./bin/spimi/spimi-index - specify output to ./bin/var/
3. Have the files of this repo in the base folder of spimi
4. Run server.py
5. Address the server in your browser by localhost:10800/spimi/interface

    Available options in the spimi-interface:
        sort by following: will find the most frequent words AFTER your query
        and return these words as well as 20 sentences with this constellation

        sort by previous: does the same as sort by folllowing but with the words
        left to your query

        sort by cooc: will find sentences containing your query and a second word,
        specified by query;word in the search box.

Caution: In the current setting, the server will be available to any client
in your current network. Be sure Port 10800 is not forwarded or to disable
'debug' in the server.py

