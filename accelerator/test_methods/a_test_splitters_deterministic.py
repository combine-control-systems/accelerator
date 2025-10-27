# -*- coding: utf-8 -*-
############################################################################
#                                                                          #
# Copyright (c) 2025 Carl Drougge                                          #
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

description = r'''
Test the roundrobin and chunked sequence splitters.
'''

from accelerator.splitters import RoundRobinSplitter, ChunkSplitter


def prepare(slices):
	class Unpicklable(str):
		"This can't be pickled, because it's local to the function."
	def populate(typ):
		res = {}
		# One with each number of left over elements
		# after dividing them evenly across slices.
		res['left_overs'] = [
			typ(range(slices * 2 + left_over))
			for left_over in range(slices)
		]
		# These all make ['a', 'b', 'c'] in various ways,
		# to make sure modifications work correctly.
		abcds = []
		abcds.append(typ('abcd'))
		abcds.append(typ('ab'))
		abcds[-1].append('c')
		abcds[-1].append('d')
		abcds.append(typ('aXXcd'))
		abcds[-1][1:3] = 'b'
		abcds.append(typ('a'))
		abcds[-1].extend('bcd')
		abcds.append(typ('aXcd'))
		abcds[-1][1] = 'b'
		assert len(abcds) == 5 and all(el == ['a', 'b', 'c', 'd'] for el in abcds)
		res['abcds'] = abcds
		res['unpicklable'] = [typ([Unpicklable('foo'), Unpicklable('bar')])]
		return res
	return (
		populate(list), # One without any magic, for comparing to
		populate(RoundRobinSplitter),
		populate(ChunkSplitter),
		Unpicklable,
	)


# This one is trivial, so we use the same implementation as in the splitter
def reimplemented_rr(slices, sliceno, lst):
	return lst[sliceno::slices]

# This one is trickier. We replicate the actual decision code, as we must,
# but then use a different (easier to understand but slower) offset calculation.
def reimplemented_chunk(slices, sliceno, lst):
	per_slice = len(lst) // slices
	left_over = len(lst) % slices
	# This is the sliceno where left_over elements start being added.
	# A reasonably large prime gives quite even distribution.
	extra_pos = (left_over * 27644437) % slices
	extra = [0] * slices
	for extra_pos in range(extra_pos, extra_pos + left_over):
		extra[extra_pos % slices] = 1
	start = per_slice * sliceno + sum(extra[:sliceno])
	end = start + per_slice + extra[sliceno]
	return lst[start:end]


def analysis(sliceno, slices, prepare_res):
	normal_lists, rrs, chunks, unpicklable_type = prepare_res
	for d in (normal_lists, rrs, chunks):
		assert all(type(item) is unpicklable_type for item in d['unpicklable'][0])
	def chk(err_prefix, d, split_func):
		for k, got in d.items():
			want = [split_func(slices, sliceno, v) for v in normal_lists[k]]
			assert got == want, "%s:%s had wrong values in slice %d:\nwanted %r\ngot    %r" % (err_prefix, k, sliceno, want, got,)
	chk("rrs", rrs, reimplemented_rr)
	chk("chunks", chunks, reimplemented_chunk)

	# left_overs covers all cases for how they split,
	# so simplify synthesis and only check those.
	return rrs['left_overs'], chunks['left_overs']


def synthesis(slices, prepare_res, analysis_res):
	want = {
		'left_overs': [
			list(range(slices * 2 + left_over))
			for left_over in range(slices)
		],
		'abcds': 5 * [list('abcd')],
		'unpicklable': [['foo', 'bar']],
	}
	def chk(err_prefix, d):
		for k, v in want.items():
			assert d[k] == v, "%s:%s had wrong values in synthesis:\nwanted %r\ngot    %r" % (err_prefix, k, v, d[k],)

	# They should all contain the full data in synthesis
	normal_lists, rrs, chunks, _ = prepare_res
	chk("prepare:normal_lists", normal_lists)
	chk("prepare:rrs", rrs)
	chk("prepare:chunks", chunks)

	# Check that the data seen in analysis is actually all of the data.
	# Since left_overs covers all cases for how they split, only check that.
	want_chunks = want['left_overs']
	want_rrs = []
	for sliceno in range(slices):
		want_rrs.append([lst[sliceno::slices] for lst in want_chunks])
	rrs, chunks = next(analysis_res)
	rrs = [rrs]
	for r, c in analysis_res:
		rrs.append(r)
		for dst, src in zip(chunks, c):
			dst.extend(src)
	assert chunks == want_chunks
	assert rrs == want_rrs
