The code in shared-signals-guide.py provides working code that corresponds to the snippets found on http://sharedsignals.guide

To run this example you need to have the event transmitter app running on port 443 on `localhost` 
([see the README](../transmitter/README.md)).

Then, from this directory, run shared-signals-guide.py using python (Python 3.8+ are supported): 
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 shared-signals-guide.py --no-ssl
```

`--no-ssl` parameter makes this script ignore invalid SSL certificates of the event transmitter. It should only be used for testing.

The output should roughly match the various `example_***.json` files in this directory.
Note that the JSON was re-arranged a bit for increased readability.
