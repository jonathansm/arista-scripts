#!/usr/bin/env python

'''
Same script as CvesCli.py but without the added code to allow this to be ran from the CLI natively
'''

from __future__ import print_function
import urllib, json, time

base_url = "http://cve.circl.lu/api/search/"

orgs = [
    ('Arista'),
    ('Cisco'),
    ('Juniper')
]

data = []

for org in orgs:

    response = urllib.urlopen(base_url + org)
    json_data = json.loads(response.read())
    
    data.append((org, len(json_data['data'])))

max_value = max(count for _, count in data)
increment = max_value / 50

longest_label_length = max(len(org) for org, _ in data)

display_width, remainder = divmod(int(max_value * 2 / increment), 2)
display_width += 20
title = "Total CVEs per organization"
print('\n', end='')
print('-' * (((display_width - len(title))/2) - 1) , title, '-' * (((display_width - len(title))/2)) )
for org, count in data:

    bar_chunks, remainder = divmod(int(count * 2 / increment), 2)

    bar = '#' * bar_chunks

    bar = bar or "|"

    print(org.rjust(longest_label_length) , "|" , str(count).ljust(5) , bar)

print('-' * display_width, '\n')