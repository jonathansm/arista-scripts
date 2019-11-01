#!/usr/bin/env python
''' Show CVEs command
This script pulls current CVEs from different organizations listed in the org array and totals them.
Displays totals in a bar graph. This is to show what you can do with an Arista switch.

To install run these commands. The last command will kick you out of the switch.
sudo cp /mnt/flash/CvesCli.py /usr/lib/python2.7/site-packages/CliPlugin/
sudo killall ConfigAgent
'''
from __future__ import print_function
import BasicCli
import CliParser
import urllib, json, time

def showCVEs( mode ):


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


tokenCVE = CliParser.KeywordRule( 'cves', helpdesc='Show total amount of CVEs for different Organizations' )


BasicCli.registerShowCommand( tokenCVE, showCVEs )
