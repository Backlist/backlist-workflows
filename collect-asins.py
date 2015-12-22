#!/usr/bin/env python3

# Given a Backlist post file, collect ASINs for books as a
# comma-separated list to use as seed content in Amazon aStore categories.

import os
import sys

import yaml


def grab_yaml_frontmatter(f):
    '''Given a file, return YAML frontmatter as string, if present'''
    yaml_result = ''

    if f.readline() == '---\n':
        yaml_active = True
        for line in f.readlines():
            if yaml_active:
                if line != '---\n':
                    yaml_result += line
                else:
                    yaml_active = False

    return yaml_result


def book_ids_from_frontmatter(frontmatter):
    '''Return a list of book id hashes from frontmatter of list file.'''
    sections = yaml.load(frontmatter)['sections']

    books = []
    for section in sections:
        for book_id in section['books']:
            books.append(book_id)

    return books


def get_book_data_paths(list_file_path, books):
    '''Given root book data directory, return list of paths to files that \
    match book id hashes in given list of hashes.'''
    book_data_dir = os.path.abspath(list_file_path) + '/../../../../../_books'
    book_data_dir = os.path.abspath(book_data_dir)

    book_data_paths = []
    for path, visit, arg in os.walk(book_data_dir):
        for filename in arg:
            if os.path.splitext(filename)[1] == '.bib':
                for book in books:
                    if filename.find(book) >= 0:
                        book_data_paths.append(path + '/' + filename)

    return book_data_paths


def get_asins_from_files(book_data_paths):
    '''Given list of file paths, return list of ASIN strings in YAML \
    frontmatter in specified files.'''
    asins = []

    for path in book_data_paths:
        book_file = open(path)
        book_yaml = grab_yaml_frontmatter(book_file)
        asins.append(yaml.load(book_yaml)['amzn'])
        book_file.close()

    return asins


if __name__ == '__main__':
    f = open(sys.argv[1])

    yaml_frontmatter = grab_yaml_frontmatter(f)

    books = book_ids_from_frontmatter(yaml_frontmatter)
    book_data_paths = get_book_data_paths(sys.argv[1], books)
    asins = get_asins_from_files(book_data_paths)

    asin_string = ''
    for asin in asins:
        asin_string += asin + ', '
    asin_string = asin_string[:-2]

    print("ASINs for aStore:")
    print(asin_string)

    f.close()
