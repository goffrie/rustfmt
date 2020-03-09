#!/usr/bin/python

import collections
import re

column_size = 8

categories = {
    'Cc': ['Other', 'Control'],
    'Cf': ['Other', 'Format'],
    'Cn': ['Other', 'NotAssigned'],
    'Co': ['Other', 'PrivateUse'],
    'Cs': ['Other', 'Surrogate'],
    'Ls': ['Letter', 'Cased'],
    'Ll': ['Letter', 'Lowercased'],
    'Lm': ['Letter', 'Modifier'],
    'Lo': ['Letter', 'Other'],
    'Lt': ['Letter', 'Titlecase'],
    'Lu': ['Letter', 'Uppercase'],
    'Mc': ['Mark', 'SpaceCombining'],
    'Me': ['Mark', 'Enclosing'],
    'Mn': ['Mark', 'Nonspacing'],
    'Nd': ['Number', 'DecimalDigit'],
    'Nl': ['Number', 'Letter'],
    'No': ['Number', 'Other'],
    'Pc': ['Punctuation', 'Connector'],
    'Pd': ['Punctuation', 'Dash'],
    'Pe': ['Punctuation', 'Close'],
    'Pf': ['Punctuation', 'FinalQuote'],
    'Pi': ['Punctuation', 'InitialQuote'],
    'Po': ['Punctuation', 'Other'],
    'Ps': ['Punctuation', 'Open'],
    'Sc': ['Symbol', 'Currency'],
    'Sk': ['Symbol', 'Modifier'],
    'Sm': ['Symbol', 'Math'],
    'So': ['Symbol', 'Other'],
    'Zl': ['Separator', 'Line'],
    'Zp': ['Separator', 'Paragraph'],
    'Zs': ['Separator', 'Space']
}

def generate_rows():
    with open('UnicodeData.txt', 'r') as ucd:
        for line in ucd:
            split = line.split(';')
            char, category = split[0], split[2]
            yield (char, category)


def generate_dict(rows_gen):
    d = collections.defaultdict(list)
    for char, category in rows_gen:
        if category == 'Cs':
            # for whatever reason, rust doesn't allow this class of characters
            # as unicode literals.
            continue
        d[category].append(char)
    return d

def generate_tables(d):
    new_dict = collections.defaultdict(list)
    for key in d.keys():
        name = ''.join(categories[key])
        new_dict[name] = d[key]
    return new_dict

def print_header():
    print("// This file is autogenerated by scripts/unicode.py.\n")

def main():
    print_header()
    row_generator = generate_rows()
    dictionary = generate_dict(row_generator)
    named_table = generate_tables(dictionary)
    output_tables(named_table)

def output_tables(d):
    for key in sorted(d.keys()):
        name = camel_to_snake_case(key).upper()
        rust_unicode_escapes = map(lambda x: r"'\u{{{}}}'".format(x), d[key])
        table_lines = []
        for chunk in [rust_unicode_escapes[x:x+column_size] for x in xrange(0, len(rust_unicode_escapes), column_size)]:
            table_lines.append('    ' + ', '.join(chunk))
        table_string = ',\n'.join(table_lines)
        print("pub static {} : &'static [char] = &[\n{}];\n".format(name, table_string))

def camel_to_snake_case(name):
    # thanks to http://stackoverflow.com/a/1176023/1030074
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

if __name__ == "__main__":
    main()
