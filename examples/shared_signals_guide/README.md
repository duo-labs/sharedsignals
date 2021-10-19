The code in shared-signals-guide.py provides working code that corresponds to the snippets found on http://sharedsignals.guide

To run this example you need to have the event transmitter app running on port 443 on localhost (see the README in
the ./transmitter), with an entry
in `/etc/hosts` mapping `localhost` to `transmitter.most-secure.com`:
```
127.0.0.1       transmitter.most-secure.com
```

Then, from `examples`, run
```
python3 shared_signals_guide/shared-signals-guide.py
```

The output should roughtly match the various `example_***.json` files in this directory.
Note that the JSON was re-arranged a bit for increased readability.
