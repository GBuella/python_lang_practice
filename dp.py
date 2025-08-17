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

parser = argparse.ArgumentParser(description='Noun declensions.')
parser.add_argument('-p', help='CSV file path - nouns', default='pldb.csv',
		dest='path')
parser.add_argument('-Q', help='CSV file path - prepositions', default='pldb_prep.csv',
		dest='prepdb_path')
parser.add_argument('-W', help='CSV file path - adjectives', default='pldb_adj.csv',
		dest='adjdb_path')
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
parser.add_argument('-f', help='all 6 cases, 2 numbers', action='store_true',
		dest='full6')
parser.add_argument('-F', help='all 7 cases, 2 numbers', action='store_true',
		dest='full7')
parser.add_argument('-q', help='ask prepositions', action='store_true',
		dest='preps')
parser.add_argument('-w', help='ask adjectives', action='store_true',
		dest='adjs')
parser.add_argument('-r', help='randomize case order', action='store_true',
		dest='rcases')

args = parser.parse_args()

words = []
preps = {}
adjs = []

if args.adjs:
	with open(args.adjdb_path, newline='') as csvfile:
		datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		hasword = False
		adj = {}
		for row in datareader:
			if len(row) == 0:
				if hasword:
					adjs.append(adj)
				hasword = False
				adj = {}
			elif not hasword:
				if row[0].startswith('#'):
					continue
				adj['id'] = int(row[0])
				assert len(row) == 2 or len(row) == 3
				adj['def'] = row[1]
				adj['decl'] = {
					'viril_plural': {},
					'nonviril_plural': {},
					'masculine_animate': {},
					'masculine_inanimate': {},
					'feminine': {},
					'neuter': {}}
				hasword = True
			else:
				if row[0].startswith('#'):
					continue
				assert len(row) >= 5 and len(row) <= 7
				case = row[0]
				if case == 'vocative':
					continue
				adj['decl']['masculine_animate'][case] = row[1]
				i = 2
				if case == 'accusative':
					adj['decl']['masculine_inanimate'][case] = row[2]
					i = 3
				else:
					adj['decl']['masculine_inanimate'][case] = row[1]
				adj['decl']['feminine'][case] = row[i]
				i = i + 1
				adj['decl']['neuter'][case] = row[i]
				i = i + 1
				adj['decl']['viril_plural'][case] = row[i]
				if (case == 'accusative' or case == 'nominative'):
					adj['decl']['nonviril_plural'][case] = row[i+1]
				else:
					adj['decl']['nonviril_plural'][case] = row[i]
		if hasword:
			adjs.append(adj)

if args.preps:
	with open(args.prepdb_path, newline='') as csvfile:
		datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		for row in datareader:
			if (len(row) == 0 or row[0].startswith('#')):
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
			word['irregular'] = False
			word['no_prep'] = False
			word['only_prep'] = False
			if len(row) == 4:
				if "irr" in row[3]:
					word['irregular'] = True
				if "no_prep" in row[3]:
					word['no_prep'] = True
				if "only_prep" in row[3]:
					word['only_prep'] = True
			if row[1] == 'f':
				word['gender'] = 'feminine'
			elif row[1] == 'n':
				word['gender'] = 'neuter'
			elif row[1] == 'nps':
				word['gender'] = 'pronoun' # no-gender pronouns, singular
			elif row[1] == 'npp':
				word['gender'] = 'pronoun_plural' # no-gender pronouns, plural
			elif row[1] == 'nns':
				word['gender'] = 'numeral' # no-gender numerals, singular
			elif row[1] == 'nnp':
				word['gender'] = 'numeral_plural' # no-gender numerals, plural
			elif row[1] == 'minan':
				word['gender'] = 'masculine_inanimate'
			elif row[1] == 'man':
				word['gender'] = 'masculine_animal'
			elif row[1] == 'mpers':
				word['gender'] = 'masculine_personal'
			elif row[1] == 'nvirpl':
				word['gender'] = 'nonviril_plural'
				word['irregular'] = True
			elif row[1] == 'virpl':
				word['gender'] = 'viril_plural'
				word['irregular'] = True
			else:
				print(row[1])
				assert False, 'unknown gender'
			word['def'] = row[2]
			word['decl'] = []
			hasword = True
		else:
			if row[0].startswith('#'):
				continue
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

def ask(case, number, answer, ns, prev, gender, no_prep, no_adj):
	prompt_adj = ''
	prompt_prep = ''
	prompt_postp = ''
	prompt_case = ' ' + case
	if (args.adjs and case != 'vocative' and gender != 'pronoun_plural'
		and gender != 'pronoun' and gender != 'numeral'
		and not no_adj
		and gender != 'numeral_plural'):
		adj = random.choice(adjs)
		adjg = gender
		if ((gender == 'masculine_personal' or gender == 'masculine_animal')
			and number == 'singular'):
			adjg = 'masculine_animate'
		if gender == 'masculine_personal' and number == 'plural':
			adjg = 'viril_plural'
		if ((gender == 'masculine_animal' or gender == 'masculine_inanimate'
			or gender == 'feminine' or gender == 'neuter')
			and number == 'plural'):
			adjg = 'nonviril_plural'
		answer = adj['decl'][adjg][case] + ' ' + answer
		prompt_adj = ' ' + adj['def']
		
	if (args.preps and (case + '_' + number) in preps
		and not no_prep
		and gender != 'numeral' and gender != 'numeral_plural'):
		prompt_case = ''
		prep = random.choice(preps[case + '_' + number])
		if 'question_prep' in prep:
			prompt_prep = ' ' + prep['question_prep']
		if 'question_postp' in prep:
			prompt_postp = '   ' + prep['question_postp']
		answer = prep['preposition'] + ' ' + answer
		# TODO: allow ze, we, pode...
	prompt = prompt_prep + prompt_adj + prompt_case + ' ' + number + prompt_postp + ' :'

	prompt = prompt.strip().rjust(50) + ' '

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
	elif picked['only_prep'] and not args.preps:
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
			and picked['gender'] != 'pronoun_plural'
			and picked['gender'] != 'numeral_plural'
			and picked['gender'] != 'viril_plural'
			and picked['gender'] != 'nonviril_plural'):
			ask(d[0], 'singular', d[1], ns, prev, picked['gender'], picked['no_prep'], picked['only_prep'])
			prev = d[1]
		if (args.number != 'singular'
			and picked['gender'] != 'pronoun'
			and picked['gender'] != 'numeral'
			and (args.full6 or args.full7 or picked['irregular'] or
				d[0] == 'nominative' or d[0] == 'genitive' or
				d[0] == 'accusative'
			)):
			answer = d[1]
			if (picked['gender'] != 'viril_plural'
				and picked['gender'] != 'pronoun_plural'
				and picked['gender'] != 'numeral_plural'
				and picked['gender'] != 'nonviril_plural'):
				if (len(d) == 2):
					continue
				answer = d[2]
			ask(d[0], 'plural', answer, ns, prev, picked['gender'], picked['no_prep'], picked['only_prep'])
			prev = answer
