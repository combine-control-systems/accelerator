# -*- coding: utf-8 -*-
############################################################################
#                                                                          #
# Copyright (c) 2024 Carl Drougge                                          #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#  http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
#                                                                          #
############################################################################

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from accelerator.colourwrapper import colour
from accelerator.compat import fmt_num, num_types
from accelerator.error import NoSuchWhateverError
from accelerator.shell.parser import ArgumentParser
from accelerator.shell.parser import name2ds
from accelerator import g

from collections import Counter
import sys


# multiprocessing.Pool insists on pickling the function even when using
# forking (as we do). Thus we need this top level indirection function.
_indirected_func = None
def _indirection(sliceno):
	return _indirected_func(sliceno)


def format_aligned(hist):
	def fmt_k(k):
		if isinstance(k, num_types):
			return fmt_num(k)
		else:
			return str(k)
	hist = [(fmt_k(k), fmt_num(v)) for k, v in hist]
	klen = max(len(k) for k, v in hist)
	vlen = max(len(v) for k, v in hist)
	total_len = klen + vlen + 2
	hist = [(k, ' ' * (total_len - len(k) - len(v)), v) for k, v in hist]
	return hist, '%s%s%s'

def format_bars(hist):
	from accelerator.compat import terminal_size
	columns = terminal_size()[0]
	a_hist, a_fmt = format_aligned(hist)
	max_len = columns - len(''.join(a_hist[0])) - 3
	if max_len < 2:
		return a_hist, a_fmt
	values = [v for k, v in hist]
	max_v = max(values)
	if max_v > max_len:
		rounding = ('', '\u258f', '\u258e', '\u258d', '\u258c', '\u258b', '\u258a', '\u2589', '\u2588')
		def mkbar(v):
			size = v * max_len / max_v
			bonus = int(round((size - int(size)) * 8))
			return '\u2588' * int(size) + rounding[bonus]
	else:
		mkbar = '\u2588'.__mul__
	hist = [(a_fmt % a, mkbar(v)) for a, v in zip(a_hist, values)]
	return hist, '%s  ' + colour('%s', 'hist/bar')

def format_csv(hist):
	return hist, '%s,%d'

def format_tsv(hist):
	return hist, '%s\t%d'

formatters = {
	'aligned': format_aligned,
	'bars'   : format_bars,
	'csv'    : format_csv,
	'tsv'    : format_tsv,
}


def main(argv, cfg):
	parser = ArgumentParser(prog=argv.pop(0), description='''show a histogram of column(s) from a dataset.''')
	parser.add_argument('-c', '--chain',     action='store_true', negation='dont', help="follow dataset chain", )
	parser.add_argument(      '--chain-length', '--cl',         metavar='LENGTH',  help="follow chain at most this many datasets", type=int)
	parser.add_argument(      '--stop-ds',   metavar='DATASET', help="follow chain at most to this dataset")
	parser.add_argument('-f', '--format', choices=sorted(formatters), help="output format, " + ' / '.join(sorted(formatters)), metavar='FORMAT', )
	parser.add_argument('-m', '--max-count', metavar='NUM',     help="show at most this many values", type=int)
	parser.add_argument('-s', '--slice',     action='append',   help="this slice only, can be specified multiple times", type=int)
	parser.add_argument('dataset', help='can be specified in the same ways as for "ax ds"')
	parser.add_argument('column', nargs='+', help='you can specify multiple columns')
	args = parser.parse_intermixed_args(argv)

	try:
		ds = name2ds(cfg, args.dataset)
	except NoSuchWhateverError as e:
		print(e, file=sys.stderr)
		return 1

	chain = ds.chain(args.chain_length if args.chain else 1, stop_ds=args.stop_ds)
	if not chain:
		return

	ok = True
	for ds in chain:
		for col in args.column:
			if col not in ds.columns:
				print("Dataset %s does not have column %s." % (ds.quoted, col,), file=sys.stderr)
				ok = False
	if not ok:
		return 1

	columns = args.column[0] if len(args.column) == 1 else args.column
	useful_slices = [sliceno for sliceno in range(g.slices) if chain.lines(sliceno) > 0]
	if args.slice:
		useful_slices = list(set(useful_slices) & set(args.slice))
	if not useful_slices:
		return

	def one_slice(sliceno):
		return Counter(chain.iterate(sliceno, columns))

	if len(useful_slices) == 1:
		hist = one_slice(useful_slices[0])
	else:
		global _indirected_func
		_indirected_func = one_slice
		from multiprocessing import Pool
		pool = Pool(len(useful_slices))
		try:
			hist = None
			for part in pool.imap_unordered(_indirection, useful_slices, 1):
				if hist:
					hist.update(part)
				else:
					hist = part
		finally:
			pool.close()

	if args.format:
		formatter = formatters[args.format]
	elif sys.stdout.isatty():
		formatter = format_aligned
	else:
		formatter = format_tsv

	hist = hist.most_common(args.max_count)
	hist, fmt = formatter(hist)

	for item in hist:
		print(fmt % item)