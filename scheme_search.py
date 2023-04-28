"""
Looking for a semi-rational table calculation approach.

Try dividing the calc into 4 quadrants arranged by dividing over 2 data bits
We need to split the 4 options, but in order to mark exactly 2 of 4 states, we
see there are actually 3 possible functions (not counting inverse):
Possible perms are 6: 1100 1010 1001 0110 0101 0011
Not counting inverses, the patterns are basically A B and A^B.

Choose 2 bits from 4, 6 ways : ab ac ad bc bd cd
Choose one of 3 schemes : A,B AxB,A or AxB,B
For EACH of these scheme, each quadrant requires 7 4-bit patterns
Which are basically one of these:
0000 0     ld(k_0)
0001 A.B   ld(A); and(B)
0010 A.~B  ld(A); and(nB)
0011 A
0100 ~A.B  ld(nA); and(B)
0101 B
0110 A^B   ld(A); xor(B)
0111 A+B   ld(A); or(B)
1000 ... and so on (
    - remaining ones are inverses of the above
    - none take more than 2 instrs to calc

So count, over the 7 seg outputs of a quadrant, how many patterns are required
 - or count precisely
We can also figure how many non-trival patterns there are, maybe can be
pre-calced ?

"""
import numpy as np

# get code table : it is (7, 16)
from ue14500_sim import seg_nums_usage
print(seg_nums_usage.shape)
print(seg_nums_usage.dtype)
print(seg_nums_usage)

select_addr_indices = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
select_schemes = ['AB', 'XA', 'XB']  # X denotes the use of AxB as an index
scheme_quadrant_inds = {
    'AB': [[0, 0, 1, 1], [0, 1, 0, 1]],
    'XA': [[0, 1, 1, 0], [0, 1, 0, 1]],
    'XB': [[0, 1, 1, 0], [0, 0, 1, 1]],
}

# OLD pattern costs : assume existence of ¬a ¬b in storage
# pattern_costs = {
#     '0000': 1,  # 0
#     '0001': 2,  # a.b
#     '0010': 2,  # a.¬b
#     '0011': 1,  # a
#     '0100': 2,  # ¬a.b
#     '0101': 1,  # b
#     '0110': 2,  # a^b
#     '0111': 2,  # a|b
#     '1000': 2,  # ¬(a|b) = ¬a.¬b
#     '1001': 2,  # ¬(a^b) = ¬a^b
#     '1010': 1,  # ¬a
#     '1011': 2,  # ¬b|a
#     '1100': 1,  # ¬a
#     '1101': 2,  # ¬a|b
#     '1110': 2,  # ¬a.¬b
#     '1111': 1,  # 1
# }

# NEW pattern costs
#   assuming NO givens for precalculated+stored inverses
#   but do accept that a '1' is stored somewhere (for inversion), and a '0'
pattern_costs = {
    '0000': 1,  # 0
    '0001': 2,  # a.b
    '0010': 3,  # a.¬b
    '0011': 1,  # a
    '0100': 3,  # ¬a.b
    '0101': 1,  # b
    '0110': 2,  # a^b
    '0111': 2,  # a|b
    '1000': 3,  # ¬(a|b) = ¬a.¬b
    '1001': 3,  # ¬(a^b) = ¬a^b
    '1010': 2,  # ¬a
    '1011': 3,  # ¬b|a
    '1100': 2,  # ¬a
    '1101': 3,  # ¬a|b
    '1110': 3,  # ¬a.¬b = ¬(a.b)
    '1111': 1,  # 1
}

segs_by_index = seg_nums_usage.reshape(7, 2, 2, 2, 2).astype(int)
i_scheme = 0
min_calc_cost = 9999
mincalc_scheme = -1
for ai0, ai1 in select_addr_indices:
    print('')
    print(f'---split on indices : {ai0}, {ai1}')
    # Find the 'other two' addresses to use
    ai2, ai3 = [x for x in range(4) if x not in (ai0, ai1)]
    for scheme in select_schemes:
        print(f'SCHEME #{i_scheme}: addr-bits={(ai0, ai1)} scheme={scheme}')
        scheme_patterns = set()
        scheme_calc_costs = 0
        for i_quadrant in range(4):
            a0 = i_quadrant % 2
            a1 = i_quadrant // 2
            # Now in one quadrant
            # Get a pattern by twiddling the 'other two' addresses
            quadrant_seg_patterns = np.zeros((7, 4), dtype=int)
            ixs, iys = scheme_quadrant_inds[scheme]
            for i_step, (ix, iy) in enumerate(zip(ixs, iys)):
                address = [slice(None)] * 5
                address[ai0 + 1] = a0
                address[ai1 + 1] = a1
                address[ai2 + 1] = ix
                address[ai3 + 1] = iy
                address = tuple(address)
                # print(f'   ----- QUADRANT#{i_quadrant} [{address}')
                quadrant_seg_patterns[:, i_step] = segs_by_index[address]
            quadrant_patterns_list = [
                ''.join(str(bit) for bit in quadrant_seg_patterns[i_seg])
                for i_seg in range(7)
            ]
            quadrant_patterns_set = set(quadrant_patterns_list)
            quadrant_patterns_usecount = {
                patt + ('*' if pattern_costs[patt] > 1 else ' '): sum([1 for p in quadrant_patterns_list if p == patt])
                for patt in sorted(quadrant_patterns_set)
            }
            quadrant_calc_costs = sum(pattern_costs[patt] for patt in quadrant_patterns_set)
            scheme_patterns |= quadrant_patterns_set
            scheme_calc_costs += quadrant_calc_costs
            print(f'    Q#{i_quadrant} cost-sum={quadrant_calc_costs} patterns={quadrant_patterns_usecount}')
        print('  :: total scheme :')
        patt_report = [
            patt + ('*' if pattern_costs[patt] > 1 else ' ')
            for patt in sorted(scheme_patterns)
        ]
        print(f'        patterns({len(scheme_patterns)}) = {patt_report}')
        n_complex = len([p for p in scheme_patterns if pattern_costs[p] > 1])
        print(f'        calc-cost={scheme_calc_costs}  n-complex-patts={n_complex}')
        if scheme_calc_costs < min_calc_cost:
            min_calc_cost = scheme_calc_costs
            mincalc_scheme = i_scheme
        i_scheme += 1

print('')
print(f'Overall min calc cost = {min_calc_cost}, for scheme #{mincalc_scheme}')

"""
sample output ...

---split on indices : 2, 3
SCHEME #15: addr-bits=(2, 3) scheme=AB
    Q#0 cost-sum=9 patterns={'0110*': 1, '1011*': 3, '1110*': 2, '1111 ': 1}
    Q#1 cost-sum=10 patterns={'0110*': 1, '0111*': 1, '1010*': 1, '1101*': 1, '1111 ': 3}
    Q#2 cost-sum=10 patterns={'0001*': 1, '0110*': 2, '0111*': 2, '1011*': 1, '1111 ': 1}
    Q#3 cost-sum=14 patterns={'0011 ': 2, '1010*': 1, '1011*': 1, '1100*': 1, '1101*': 1, '1110*': 1}
  :: total scheme :
        patterns(10) = ['0001*', '0011 ', '0110*', '0111*', '1010*', '1011*', '1100*', '1101*', '1110*', '1111 ']
        calc-cost=43  n-complex-patts=8

complex patt usage : COST *(n-quadrants which use each one) : total cost
  0001  2  *1  -    2
  0110  2  *3  -    6
  0111  2  *2  -    4
  1010  2  *2  -    4
  1011  3  *3  ++   7
  1100  2  *1  -    2
  1101  3  *3  ++   7
  1110  3  *2  -    6
                   --
                   38


SCHEME #16: addr-bits=(2, 3) scheme=XA
    Q#0 cost-sum=8 patterns={'0011 ': 1, '1011*': 2, '1110*': 3, '1111 ': 1}
    Q#1 cost-sum=9 patterns={'0011 ': 1, '0111*': 1, '1010*': 1, '1101*': 1, '1111 ': 3}
    Q#2 cost-sum=10 patterns={'0011 ': 2, '0100*': 1, '0111*': 2, '1110*': 1, '1111 ': 1}
    Q#3 cost-sum=16 patterns={'0110*': 2, '1001*': 1, '1010*': 1, '1011*': 1, '1101*': 1, '1110*': 1}
  :: total scheme :
        patterns(10) = ['0011 ', '0100*', '0110*', '0111*', '1001*', '1010*', '1011*', '1101*', '1110*', '1111 ']
        calc-cost=43  n-complex-patts=8

complex patt usage : COST *(n-quadrants which use each one)
  0100  3  *1  -    3
  0110  2  *1  -    2
  0111  2  *1  -    2
  1001  3  *1  -    3
  1010  2  *2  -    4
  1011  3  *2  -    6
  1101  3  *2  -    6
  1110  3  *3  ++   7
                   --
                   33

SCHEME #17: addr-bits=(2, 3) scheme=XB
    Q#0 cost-sum=8 patterns={'0101 ': 1, '1101*': 2, '1110*': 3, '1111 ': 1}
    Q#1 cost-sum=9 patterns={'0101 ': 1, '0111*': 1, '1011*': 1, '1100*': 1, '1111 ': 3}
    Q#2 cost-sum=10 patterns={'0010*': 1, '0101 ': 2, '0111*': 2, '1110*': 1, '1111 ': 1}
    Q#3 cost-sum=16 patterns={'0110*': 2, '1001*': 1, '1011*': 1, '1100*': 1, '1101*': 1, '1110*': 1}
  :: total scheme :
        patterns(10) = ['0010*', '0101 ', '0110*', '0111*', '1001*', '1011*', '1100*', '1101*', '1110*', '1111 ']
        calc-cost=43  n-complex-patts=8

complex patt usage : COST *(n-quadrants which use each one)
  0010  3  *1 -   3
  0110  3  *1 -   3
  0111  2  *1 -   2
  1001  3  *1 -   3
  1011  3  *2 -   6
  1100  2  *2 -   4
  1101  3  *2 -   6
  1110  3  *3 ++  7
                 --
                 34


Overall min calc cost = 43, for scheme #15

==================
CONCLUSION
selection on addrs A2,A3 is clearly best.
although we need to calc+test against (A0 x A1), A0 for an "XA" scheme,
  - it's better than the "AB" version, which needs another stored term + needs more instrs

Can also consider "awkward" terms, which are ones that will require to store '1'
- these are cases involving ¬a and ¬b, but mostly benign?
EG 1011 is ¬b|a : one();xor(b);or(a)
likewise NAND is 1110 ¬b|¬a, but ¬(a|b) -- REQUIRES a '1' constant
         NOR  is 1000 ¬a.¬b  --similar

--but none of the schemes can avoid storing BOTH of those
    - i.e. it is needed, and worth storing
but if it is stored, and not on-the-fly, then we DON'T need a '1' constant

Choose "XA" on A2+3

Estimated total program instruction count ...
    initial section
        one()
        sto('1')  # maybe same as '1110' ? (NO: at present we use it)
        ld(A3)
        and(A2)
        xor('1')
        sto('1110')     # **** N=6
    main
        ld(A3)
        xor(A2)
        skz
        jmp
        ld(A2)
        skz
        jmp     # **** N=7
        # Q#0 cost-sum=8 patterns={'0011 ': 1, '1011*': 2, '1110*': 3, '1111 ': 1}
            # '0011'
            ld(A1)
            sto()
            # '1111'
            one()
            sto()  
            # '1110' * 3
            ld('1110')
            sto()
            sto()
            sto()
            # '1011' *2
            xor(A2)
            sto()
            sto()
            jmp     # **** N=12
        # Q#1 cost-sum=9 patterns={'0011 ': 1, '0111*': 1, '1010*': 1, '1101*': 1, '1111 ': 3}
            # '0011'
            ld(A3)
            sto()
            # '0111'
            or(A2)
            sto()
            # '1010'
            one()
            xor(A2)
            sto()
            # '1101'
            one()
            sto()
            sto()
            sto()  # '1111'
            xor(A3)
            or(A2)
            sto()
            jmp     # **** N=15
        # AxB == 1
        ld(A2)
        skz
        jmp     # **** N=3
        # Q#2 cost-sum=10 patterns={'0011 ': 2, '0100*': 1, '0111*': 2, '1110*': 1, '1111 ': 1}
            # '0011' *2
            ld(A3)
            sto()
            sto()
            # '0100'
            one()
            sto()   # '1111'
            xor(A3)
            and(A2)
            sto()
            # '0111' *2
            ld(A3)
            or(A2)
            sto()
            sto()
            # '1110'
            ld('1110')
            sto()
            jmp     # **** N=15
        # Q#3 cost-sum=16 patterns={'0110*': 2, '1001*': 1, '1010*': 1, '1011*': 1, '1101*': 1, '1110*': 1}
            # '0110' *2
            ld(A3)
            xor(A2)
            sto()
            sto()
            # '1001'
            xor('1')
            sto()
            # '1010'
            xor(A2)
            sto()
            # '1011'
            ld('1110')
            xor(A3)
            sto()
            # '1110'
            ld('1110')
            sto()
            # '1101'
            xor(A2)
            sto()   # **** N=15

TOTAL = 
  6
  7
 12
 15
  3
 15
 15
---
 73
            
"""