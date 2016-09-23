#!/usr/bin/env python3

# Given a title and a Backlist post file, create a new collection
# on the Backlist Zotero group.

import os
import re
import sys

import bibtexparser
import json
from pyzotero import zotero

import backlist

library_id = os.getenv("BACKLIST_ZOT_LIBRARY_ID")
api_key = os.getenv("BACKLIST_ZOT_API_KEY")


def bibtex_data_from_file(f):
    '''Given book file, strip YAML frontmatter and return only Bibtex data.'''
    bibtex_result = ''

    if f.readline() == '---\n':
        yaml_active = True
        for line in f.readlines():
            if yaml_active:
                if line == '---\n':
                    yaml_active = False
            else:
                bibtex_result += line
    else:
        for line in f.readlines():
            bibtex_result += line

    return bibtex_result


def create_collection(collection_name, entries):
    test_collection = dict([
        ('name', collection_name)
    ])

    response = zot.create_collection([test_collection])
    collection_result = json.loads(response)

    print("Creating Collection…")
    collection_id = collection_result['success']['0']

    print("Creating Items…")
    created_items = zot.create_items(entries)

    for key in created_items['successful'].keys():
        print("Retrieve item…")
        item = zot.item(created_items['successful'][key]['key'])
        print("Add item to Collection…")
        zot.addto_collection(collection_id, item)


def create_entry(entry):
    entry_template = zot.item_template('book')
    entry_template['creators'] = []

    if 'author' in entry:
        authors = creators_list(entry['author'], 'author')
        entry_template['creators'] += authors

    if 'editor' in entry:
        editors = creators_list(entry['editor'], 'editor')
        entry_template['creators'] += editors

    if 'translator' in entry:
        translators = creators_list(entry['translator'], 'translator')
        entry_template['creators'] += translators

    if 'series' in entry:
        entry_template['series'] = entry['series']

    entry_template['title'] = re.sub(r'[\{\}]',
                                     '', entry['title'])
    entry_template['publisher'] = entry['publisher']
    entry_template['place'] = entry['address']
    entry_template['date'] = entry['year']

    return entry_template


def creators_list(creator_names, creator_type):
    creators = []

    for name in creator_names.split(' and '):
        creator = {}
        creator['creatorType'] = creator_type
        creator['firstName'] = ' '.join(name.split(' ')[:-1])
        creator['lastName'] = name.split(' ')[-1]

        creators += [creator]

    return creators


if __name__ == '__main__':
    zot = zotero.Zotero(library_id, 'group', api_key)

    collection_name = sys.argv[1]
    project_path = sys.argv[2]

    f = open(project_path)

    yaml_frontmatter = backlist.grab_yaml_frontmatter(f)

    books = backlist.book_ids_from_frontmatter(yaml_frontmatter)
    book_data_paths = backlist.get_book_data_paths(project_path, books)

    bibtex_string = ''
    for path in book_data_paths:
        book_file = open(path)
        bibtex_string += bibtex_data_from_file(book_file)

    bib_database = bibtexparser.loads(bibtex_string)

    entries = []
    for entry in bib_database.entries:
        entries += [create_entry(entry)]

    collection = create_collection(collection_name, entries)
