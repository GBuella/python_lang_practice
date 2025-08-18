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

import unittest
import copy
from unittest.mock import patch, mock_open
import write
from datetime import date

example_terms = [{'target': 'a', 'def': 'b', 'score': 0, 'last': 0},
	{'target': 'a2', 'def': 'b2', 'score': 0, 'last': 0},
	{'target': 'a3', 'def': 'b3', 'score': 0, 'last': 0},
	{'target': 'a4', 'def': 'b4', 'score': 0, 'last': 0}]

class test_term_reading(unittest.TestCase):
	def test_read_file(self):
		with patch("builtins.open", mock_open(read_data="id\t1\n")) as mock_file:
			self.assertEqual(write.read_terms("any"), (1, []))
			mock_file.assert_called_with("any", newline='')
		with patch("builtins.open", mock_open(read_data="# comment\nid\t99\n")) as mock_file:
			self.assertEqual(write.read_terms("any"), (99, []))
			mock_file.assert_called_with("any", newline='')
		text = "id\t3\na\tb\n"
		expected = [{'target': 'a', 'def': 'b', 'score': 0, 'last':0}]
		with patch("builtins.open", mock_open(read_data=text)) as mock_file:
			id, t = write.read_terms("any")
			self.assertEqual(id, 3)
			self.assertEqual(t, expected)
		text = text + "c\td\t5\t739479\n"
		expected.append({'target': 'c', 'def': 'd', 'score': 5, 'last': 739479})
		with patch("builtins.open", mock_open(read_data=text)) as mock_file:
			id, t = write.read_terms("any")
			self.assertEqual(id, 3)
			self.assertEqual(t, expected)

	def test_compute_term_delta(self):
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 0, 'last':0}, 730120), 1)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730120}, 730120), 1)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730119}, 730120), 4)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730118}, 730120), 8)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730101}, 730120), 76)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730099}, 730120), 84)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730098}, 730120), 84)
		self.assertEqual(write.compute_term_delta(
			{'target': 'a', 'def': 'b', 'score': 1, 'last': 730000}, 730120), 84)

	def test_fill_totals(self):
		terms = copy.deepcopy(example_terms)
		target = 1024
		expected = copy.deepcopy(terms)
		expected[0]['sum'] = target
		expected[1]['sum'] = 2 * target
		expected[2]['sum'] = 3 * target
		expected[3]['sum'] = 4 * target
		t = copy.deepcopy(terms)
		write.fill_totals(t, target)
		self.assertEqual(t, expected)

		terms[3]['score'] = 30
		expected[3]['score'] = terms[3]['score']
		expected[3]['sum'] = expected[3]['sum'] - 30
		t = copy.deepcopy(terms)
		write.fill_totals(t, target)
		self.assertEqual(t, expected)

		terms[0]['score'] = 7
		terms[1]['score'] = 800
		terms[2]['score'] = 2099
		terms[3]['score'] = 87

		expected[0]['score'] = 7
		expected[1]['score'] = 800
		expected[2]['score'] = 2099
		expected[3]['score'] = 87

		expected[0]['sum'] = target - 7
		expected[1]['sum'] = 2*target - 807
		expected[2]['sum'] = expected[1]['sum']
		expected[3]['sum'] = 3 * target - 894

		t = copy.deepcopy(terms)
		write.fill_totals(t, target)
		self.assertEqual(t, expected)

	def test_inc_term_score(self):
		terms = copy.deepcopy(example_terms)
		terms[0]['sum'] = 100
		terms[1]['sum'] = 200
		terms[2]['sum'] = 300
		terms[3]['sum'] = 400

		write.inc_term_score(terms, 3, 100, 1, 730120)
		self.assertEqual(terms,
			[{'target': 'a', 'def': 'b', 'score': 0, 'sum': 100, 'last': 0},
			{'target': 'a2', 'def': 'b2', 'score': 0, 'sum': 200, 'last': 0},
			{'target': 'a3', 'def': 'b3', 'score': 0, 'sum': 300, 'last': 0},
			{'target': 'a4', 'def': 'b4', 'score': 1, 'sum': 399, 'last': 730120}])

		write.inc_term_score(terms, 0, 100, 1, 730123)
		self.assertEqual(terms,
			[{'target': 'a', 'def': 'b', 'score': 1, 'sum': 99, 'last': 730123},
			{'target': 'a2', 'def': 'b2', 'score': 0, 'sum': 199, 'last': 0},
			{'target': 'a3', 'def': 'b3', 'score': 0, 'sum': 299, 'last': 0},
			{'target': 'a4', 'def': 'b4', 'score': 1, 'sum': 398, 'last': 730120}])

	@patch('os.path.isfile')
	def test_readlog(self, mock_isfile):
		mock_isfile.return_value = True
		with patch("builtins.open", mock_open(read_data="id\t33\n")) as mock_file:
			terms = copy.deepcopy(example_terms)
			with self.assertRaises(Exception) as err:
				write.readlog("any", terms, 99)
			self.assertEqual(str(err.exception), 'log does not match')
			mock_file.assert_called_with("any", newline='')
			self.assertEqual(terms, example_terms)
		with patch("builtins.open", mock_open(read_data="id\t3\n")) as mock_file:
			terms = copy.deepcopy(example_terms)
			write.readlog("any", terms, 3)
			mock_file.assert_called_with("any", newline='')
			self.assertEqual(terms, example_terms)
		log = "id\t3\n1\t1\t730120\n0\t1\t730120\n1\t1\t730121\n2\t2\t730121\n"
		with patch("builtins.open", mock_open(read_data=log)) as mock_file:
			terms = copy.deepcopy(example_terms)
			write.readlog("any", terms, 3)
			mock_file.assert_called_with("any", newline='')
			self.assertEqual(terms,
				[{'target': 'a', 'def': 'b', 'score': 1, 'last': 730120},
				{'target': 'a2', 'def': 'b2', 'score': 2, 'last': 730121},
				{'target': 'a3', 'def': 'b3', 'score': 2, 'last': 730121},
				{'target': 'a4', 'def': 'b4', 'score': 0, 'last': 0}])

	def test_find_term_index(self):
		terms = copy.deepcopy(example_terms)
		terms[0]['score'] = 50
		terms[0]['sum'] = 50
		terms[1]['score'] = 50
		terms[1]['sum'] = 100
		terms[2]['score'] = 50
		terms[2]['sum'] = 150
		terms[3]['score'] = 50
		terms[3]['sum'] = 200
		self.assertEqual(write.find_term_index(terms, 1), 0)
		self.assertEqual(write.find_term_index(terms, 2), 0)
		self.assertEqual(write.find_term_index(terms, 50), 0)
		self.assertEqual(write.find_term_index(terms, 51), 1)
		self.assertEqual(write.find_term_index(terms, 52), 1)
		self.assertEqual(write.find_term_index(terms, 99), 1)
		self.assertEqual(write.find_term_index(terms, 100), 1)
		self.assertEqual(write.find_term_index(terms, 101), 2)
		self.assertEqual(write.find_term_index(terms, 150), 2)
		self.assertEqual(write.find_term_index(terms, 151), 3)
		self.assertEqual(write.find_term_index(terms, 200), 3)
		terms[0]['score'] = 100
		terms[0]['sum'] = 0
		self.assertEqual(write.find_term_index(terms, 1), 1)

	def test_match_response(self):
		self.assertTrue(write.match_response('a', 'a'))
		self.assertFalse(write.match_response('a', 'a b'))
		self.assertFalse(write.match_response('a', 'b'))
		self.assertTrue(write.match_response('A', 'a'))
		self.assertTrue(write.match_response('a', 'A'))

if __name__ == '__main__':
	unittest.main()
