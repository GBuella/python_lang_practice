#
# Copyright 2025 Gabor Buella
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import argparse
import csv
import random

genderfilter = 'all'
casefilter = 'all'
numberfilter = 'all'
startid = 0
endid = 0

parser = argparse.ArgumentParser(description='Noun declensions.')
parser.add_argument('-p', help='CSV file', default='pldb.csv',
		dest='path')
parser.add_argument('-g', help='gender filter', default='all',
		dest='gender')
parser.add_argument('-c', help='case filter', default='all',
		dest='case')
parser.add_argument('-n', help='number filter', default='all',
		dest='number')
parser.add_argument('-s', help='start id', default=0, type=int,
		dest='startid')
parser.add_argument('-e', help='end id', default=0, type=int,
		dest='endid')
parser.add_argument('-f', help='end id', default=0, type=bool,
		dest='full6')
parser.add_argument('-F', help='end id', default=0, type=bool,
		dest='full7')

args = parser.parse_args()

words = []

with open(args.path, newline='') as csvfile:
	datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
	hasword = False
	word = {}
	for row in datareader:
		if len(row) == 0:
			if (hasword and word['id'] >= args.startid):
				words.append(word)
			word = {}
			hasword = False
		elif not hasword:
			if row[0].startswith('#'):
				continue
			word['id'] = int(row[0])
			if args.endid != 0 and word['id'] >= args.endid:
				break
			assert len(row) == 3 or len(row) == 4
			word['irregular'] = (len(row) == 4)
			if row[1] == 'f':
				word['gender'] = 'feminine'
			elif row[1] == 'n':
				word['gender'] = 'neuter'
			elif row[1] == 'minan':
				word['gender'] = 'masculine_inanimate'
			elif row[1] == 'man':
				word['gender'] = 'masculine_animal'
			elif row[1] == 'mpers':
				word['gender'] = 'masculine_personal'
			elif row[1] == 'nvirpl':
				word['gender'] = 'viril_plural'
			elif row[1] == 'virpl':
				word['gender'] = 'nonviril_plural'
			else:
				print(row[1])
				assert False, 'unknown gender'
			word['def'] = row[2]
			word['decl'] = []
			hasword = True
		else:
			if (word['gender'] == 'viril_plural'
				or word['gender'] == 'nonviril_plural'):
				assert len(row) == 2
			else:
				assert (len(row) == 3 or len(row) == 2)
			word['decl'].append(row)
	if hasword:
		if word['id'] >= args.startid:
			words.append(word)

random.shuffle(words)

def ask(form, answer, ns):
	resp = input(form + ': ')
	c = 0
	while (resp != answer):
		if resp == '':
			c += 1
			if c == 1:
				print('The word is ' + ns)
			else:
				print('It is "' + answer + '"')
		resp = input(form + ': ')

for picked in words:
	if (args.number == 'singular' and (
		picked['gender'] == 'viril_plural'
		or picked['gender'] == 'nonviril_plural')):
		continue
	if (args.number == 'plural' and len(picked['decl'][0]) < 3):
		continue
	print('')
	print(picked['def'])
	assert picked['decl'][0][0] == 'nominative'
	ns = picked['decl'][0][1]
	if (args.gender == 'masculine'
		and not picked['gender'].startswith('masculine')):
		continue
	elif (args.gender != 'all'
		and not picked['gender'] != args.gender):
		continue
	for d in picked['decl']:
		if args.case == 'all' and ((not args.full7) and d[0] == 'vocative'):
			continue;
		if args.case != 'all' and d[0] != args.case:
			continue;
		if (args.number != 'plural'
			and picked['gender'] != 'viril_plural'
			and picked['gender'] != 'nonviril_plural'):
			ask(d[0] + ' singular', d[1], ns)
		if (args.number != 'singular'
			and (args.full6 or args.full7 or picked['irregular'] or
				d[0] == 'nominative' or d[0] == 'genitive' or
				d[0] == 'accusative'
			)):
			answer = d[1]
			if (picked['gender'] != 'viril_plural'
				and picked['gender'] != 'nonviril_plural'):
				if (len(d) == 2):
					continue
				answer = d[2]
			ask(d[0] + ' plural', answer, ns)
