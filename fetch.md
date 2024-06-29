# Converting FosWiki HTML pages for local storage

## Fetching HTML from phased out Wiki

The following seems to work reasonably well, for retrieving a sub network of topics out of the wiki.

Note the `Research\/ISO19152` in `--accept-regex`.

```bash
$ wget --no-clobber --reject-regex "(.*)\?(.*)|(.*)rdiff(.*)" --accept-regex "(.*)Research\/ISO19152(.*)" -e robots=off -r --mirror --convert-links --backup-converted https://wiki.tudelft.nl/bin/view/Research/ISO19152/WebHome
```

## Reformat

```python
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 reformat.py
```