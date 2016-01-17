# Bibliocommons import to list #

The purpose of this library is to add items to your BiblioCommons
"read later" list.

Basically, the program reads through a search file, searches
BiblioCommons for each line in that file, and then if it finds exactly
one match that can be added to your "read later" list then it adds
that match to your "read later" list.

## Using ##

To use this:

1. Set variables in `config.yml`. You can do this by copying
   `config.EXAMPLE.yml` and changing values as appropriate.

2. Install Python modules. The easiest way to do this is via
   virtualenv. For example:

        mkvirtualenv biblio-import
		workon biblio-import
		pip install -r requirements.txt

3. Populate your search file. Each line of the file will be submitted
   as a search to Bibliocommons. Ideally you use something unique such
   as ISBN13 records. NOTE: if more than one result is returned the
   program will error out.

4. Run the importer:

        python list_adder.py

This will generate a bunch of debugging output.
