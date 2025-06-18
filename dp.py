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
parser.add_argument('-p', help='CSV file - nouns', default='pldb.csv',
		dest='path')
parser.add_argument('-P', help='CSV file - prepositions', default='pldb_prep.csv',
		dest='prepdb_path')
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
parser.add_argument('-f', help='end id', action='store_true',
		dest='full6')
parser.add_argument('-F', help='end id', action='store_true',
		dest='full7')
parser.add_argument('-C', help='ask compounds', action='store_true',
		dest='preps')
parser.add_argument('-r', help='randomize case order', action='store_true',
		dest='rcases')

args = parser.parse_args()

words = []
preps = {}

if args.preps:
	with open(args.prepdb_path, newline='') as csvfile:
		datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		for row in datareader:
			if row[0].startswith('#'):
				continue
			item = {}
			item['preposition'] = row[0]
			case = row[1]
			if row[2] != '':
				item['question_prep'] = row[2]
			if len(row) > 3 and row[3] != '':
				item['question_postp'] = row[3]
			if len(row) > 4 and row[4] != '':
				item['number'] = row[4]
			if 'number' in item:
				if not (case + '_' + item['number']) in preps:
					preps[case + '_' + item['number']] = []
				preps[case + '_' + item['number']].append(item)
			else:
				if not (case + '_singular') in preps:
					preps[case + '_singular'] = []
				preps[case + '_singular'].append(item)
				if not (case + '_plural') in preps:
					preps[case + '_plural'] = []
				preps[case + '_plural'].append(item)

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

def ask(case, number, answer, ns, prev):
	answer2 = answer
	prompt = case + '   ' + number
	answer_prefix = ''
	if args.preps and (case + '_' + number) in preps:
		prep = random.choice(preps[case + '_' + number])
		if 'question_prep' in prep:
			prompt = prep['question_prep'] + '   '
		else:
			prompt = ''
		prompt = prompt + number
		if 'question_postp' in prep:
			prompt = prompt + '   ' + prep['question_postp']
		answer = prep['preposition'] + ' ' + answer
		# TODO explicit rules for ze, we, pode...
		if (prep['preposition'].endswith('z')
			or prep['preposition'].endswith('d')
			or prep['preposition'].endswith('w')):
			answer2 = prep['preposition'] + 'e ' + answer
		else:
			answer2 = answer
	prompt = prompt + ':  '
	prompt = prompt.rjust(50)

	resp = ' '.join(input(prompt).split()).strip()
	if resp == 'x':
		resp = prev
	c = 0
	while (resp != answer and resp != answer):
		if resp == '':
			c += 1
			if c == 1:
				print('The word is ' + ns)
			else:
				print('It is "' + answer + '"')
		resp = input(prompt)

for picked in words:
	if (args.number == 'singular' and (
		picked['gender'] == 'viril_plural'
		or picked['gender'] == 'nonviril_plural')):
		continue
	if (args.number == 'plural' and len(picked['decl'][0]) < 3):
		continue
	if (args.gender == 'masculine'
		and not picked['gender'].startswith('masculine')):
		continue
	elif (args.gender != 'all'
		and picked['gender'] != args.gender):
		continue
	print('')
	print(picked['def'])
	assert picked['decl'][0][0] == 'nominative'
	ns = picked['decl'][0][1]
	prev = ''
	if args.rcases:
		random.shuffle(picked['decl'])
	for d in picked['decl']:
		if args.case == 'all' and ((not args.full7) and d[0] == 'vocative'):
			continue;
		if args.case != 'all' and d[0] != args.case:
			continue;
		if (args.number != 'plural'
			and picked['gender'] != 'viril_plural'
			and picked['gender'] != 'nonviril_plural'):
			ask(d[0], 'singular', d[1], ns, prev)
			prev = d[1]
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
			ask(d[0], 'plural', answer, ns, prev)
			prev = answer
