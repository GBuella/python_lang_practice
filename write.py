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
import os.path
from datetime import datetime

def total_sum(terms):
	return terms[-1]['sum']

def read_terms(path):
	terms = []
	with open(path, newline='') as csvfile:
		datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		for row in datareader:
			if len(row) == 0:
				continue
			if row[0].startswith('#'):
				continue
			assert len(row) == 2 or len(row) == 4
			if row[0] in terms:
				print('Duplicate definition: ' + row[0])
				sys.exit(1)
			score = 0
			time = 0
			if len(row) == 4:
				score = int(row[2])
				time = int(row[3])
			term = {'target': row[0], 'def': row[1], 'score': score, 'last': time}
			terms.append(term)
	return terms

def fill_totals(terms, target):
	total = 0
	for i in range(0, len(terms)):
		if terms[i]['score'] < target:
			total = total + target - terms[i]['score']
		terms[i]['sum'] = total

def compute_term_delta(term, day):
	if term['last'] == 0:
		return 1
	assert(term['last'] <= day)
	d = day - term['last']
	if d == 0:
		return 1
	d = d * 4
	if d > 84:
		d = 84
	return d;

def readlog(logpath, terms):
	if not os.path.isfile(logpath):
		return
	with open(logpath, newline='') as log:
		datareader = csv.reader(log, delimiter='\t')
		for row in datareader:
			assert(len(row) == 3)
			index = int(row[0])
			delta = int(row[1])
			day = int(row[2])
			assert(index >= 0 and index < len(terms))
			assert(delta > 0)
			terms[index]['score'] = terms[index]['score'] + delta
			terms[index]['last'] = day

def find_term_index(terms, sum):
	left = 0
	right = len(terms)
	while terms[left]['sum'] < sum:
		mid = (left + right) // 2
		if terms[mid]['sum'] < sum:
			left = mid + 1
		else:
			right = mid
	return left

def inc_term_score(terms, index, target, delta, day):
	# TODO: perform this in O(log n)
	terms[index]['score'] = terms[index]['score'] + delta
	terms[index]['last'] = day
	if terms[index]['score'] >= target:
		if index == 0:
			delta = terms[index]['sum']
			terms[index]['sum'] = 0
		else:
			delta = terms[index]['sum'] - terms[index - 1]['sum']
			terms[index]['sum'] = terms[index - 1]['sum']
	else:
		terms[index]['sum'] = terms[index]['sum'] - delta
	index = index + 1

	while index < len(terms):
		terms[index]['sum'] = terms[index]['sum'] - delta
		index = index + 1

def match_response(term, response):
	term_parts = term.split()
	resp_parts = response.split()
	if len(term_parts) != len(resp_parts):
		return False
	for i in range(0, len(term_parts)):
		if term_parts[i].lower() != resp_parts[i].lower():
			return False
	return True

def review_loop(terms, logpath, target):
	with open(logpath, mode='a') as log:
		while total_sum(terms) > 0:
			pick = random.randint(1, total_sum(terms))
			index = find_term_index(terms, pick)
			t = terms[index]
			first = True
			while True:
				print("\x1b[2J\x1b[H")
				print('total_sum is {}'.format(total_sum(terms)))
				if not first:
					print('Try again!')
				print(t['def'])
				resp = input()
				if match_response(t['target'], resp):
					if first:
						day = datetime.utcnow().toordinal()
						delta = compute_term_delta(t, day)
						inc_term_score(terms, index, target, delta, day)
						log.write('{}\t{}\t{}\n'.format(index, delta, day))
						log.flush()
					break;
				if resp == '':
					print('It is: ' + t['target'])
					input()
				first = False

def overwrite_csv(path, terms):
	with open(path, mode='w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter='\t', quotechar='|', dialect='unix', quoting=csv.QUOTE_MINIMAL)
		for term in terms:
			if term['score'] == 0:
				writer.writerow([term['target'], term['def']])
			else:
				writer.writerow([term['target'], term['def'], term['score'], term['last']])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='practice spelling.')
	parser.add_argument('-p', help='CSV file path',
			default='pl_vocab_write.csv',
			dest='path')
	parser.add_argument('-t', help='target write score',
			default=1000, type=int,
			dest='target_count')
	parser.add_argument('-m', help='merge counts',
			action='store_true', dest='merge')
	args = parser.parse_args()
	terms = read_terms(args.path)
	if len(terms) == 0:
		sys.exit(0)
	logpath = args.path + '.log'
	readlog(logpath, terms)
	if args.merge:
		if not os.path.isfile(logpath):
			print("No log file found")
			sys.exit(0)
		overwrite_csv(args.path, terms)
		sys.exit(0)
	fill_totals(terms, args.target_count)
	review_loop(terms, logpath, args.target_count)
