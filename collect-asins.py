#!/usr/bin/env python3

# Given a Backlist post file, collect ASINs for books as a
# comma-separated list to use as seed content in Amazon aStore categories.

import sys

import backlist


if __name__ == '__main__':
    f = open(sys.argv[1])

    yaml_frontmatter = backlist.grab_yaml_frontmatter(f)

    books = backlist.book_ids_from_frontmatter(yaml_frontmatter)
    book_data_paths = backlist.get_book_data_paths(sys.argv[1], books)
    asins = backlist.get_asins_from_files(book_data_paths)

    asin_string = ''
    for asin in asins:
        asin_string += asin + ', '
    asin_string = asin_string[:-2]

    print("ASINs for aStore:")
    print(asin_string)

    f.close()
