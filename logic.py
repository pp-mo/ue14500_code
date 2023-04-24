import numpy as np
from ue14500_sim import disp_7seg, seg_nums_usage

"""
Notes on NOR equivalence.
without dedicating a reg to '1', we can't easily invert the current output
nor(a,b) = a==0.b==0
requires ability to NOT the result of an OR
  - or to load complements (not so easy)
where result goes to temporary, can be done ...
ld(a)
or(b)
xor(const_1)

ld(a)
or(b)
sto(tmp)
one()
xor(tmp)

one()
xor(a)
sto(tmp)
one()
xor(b)
and(tmp)
"""

def ttas(n_bits, shape=None):
    # Construct a full n-bit truth-table with a given shape
    n = 2 ** n_bits
    if shape is None:
        shape = (n,)
    base = np.arange(n).reshape(shape)
    return [
        ((base & (2 ** i)) != 0)
        for i in list(range(n_bits))[::-1]
    ]

def pa(a):
    # Print a boolean array as ints [[0, 1, 0]] for compactness
    print(a.astype(int))

def seg_a():
    a, b, c, d = ttas(4, (4, 4))
    print(a)
    print('')
    print(b)

    print('')
    axb = a ^ b
    print('AxC')
    pa(axb)

    print('')
    cxd = c ^ d
    print('CxD')
    pa(cxd)

    print('')
    half_aeqb = ~axb & (~cxd | c)
    print('half_aeqb == ~AxC . (~CxD + C)')
    pa(half_aeqb)

    print('')
    half_aneb = axb & (cxd | a^c)
    print('half_aneb == AxC . (CxD + AxC)')
    pa(half_aneb)

    print('')
    full = half_aeqb | half_aneb
    print('full == half_aeqb + half_aneb')
    pa(full)


def seg_d():
    a, b, c, d = ttas(4, (4, 4))
    print('A')
    print(a)
    print('')
    print('B')
    print(b)

    print('')
    ab00 = ~a & ~b
    print('~A.~B')
    pa(ab00)

    print('')
    ab01 = ~a & b
    print('~A.B')
    pa(ab01)

    print('')
    ab10 = a & ~b
    print('A.~B')
    pa(ab10)

    print('')
    ab11 = a & b
    print('A.B')
    pa(ab11)

    cxd = c ^ d  #NB term in common with at least one more seg ??

    print('')
    out00 = ab00 & (~cxd | c)
    print('out00 = AB00 . (~CxD + C)')
    pa(out00)

    print('')
    out01 = ab01 & cxd
    print('out01 = AB01 . CxD')
    pa(out01)

    print('')
    out10 = ab10 & (~cxd | d)
    print('out10 = AB10 . (~CxD + D)')
    pa(out10)

    print('')
    out11 = ab11 & (cxd | ~d)
    print('out11 = AB11 . (CxD + ~C)')
    pa(out11)

    print('')
    out = out00 | out01 | out10 | out11
    print('out = out00 + out01 + out10 +out11')
    pa(out)

def seg_e():
    a, b, c, d = ttas(4, (4, 4))
    print('D')
    pa(d)

    print('')
    print('half_d0 = ~D . (~AxC + C)')
    half_d0 = ~d & (~(a ^ b) | c)
    pa(half_d0)

    print('')
    print('half_d1 = D . A')
    half_d1 = d & a
    pa(half_d1)

    print('')
    print('full = half_d0 | half_d1')
    full = half_d0 | half_d1
    pa(full)


# seg_e()
def unpick():
    a, b, c, d =  ttas(4, (4, 4))
    A, B, C, D = a, b, c, d

    AxC = A ^ C
    BnD = B & D
    AxD = A ^ D

    X11 = AxC ^ B
    X12 = BnD ^ C
    O13 = BnD | AxD

    N21 = ~(X11 | X12)
    X22 = X11 ^ AxD
    N23 = ~(X12 | BnD)

    N31 = ~(N21 | AxC)
    N32 = ~(X22 | AxD)
    N33 = ~(N23 | A)

    X41 = N32 ^ A

    O51 = N31 | O13

    O61 = N31 | D

    A71 = O61 & X22
    N72 = ~(N31 | X41)
    A73 = N31 & D
    A74 = X41 & B
    X75 = O51 ^ A
    N76 = ~(O51 | N23)

    O81 = A73 | A74
    X82 = A74 ^ N76
    N83 = ~(X41 | N33)

    o1 = ~N21
    o2 = ~A71
    o3 = ~N72
    o4 = ~O81
    o5 = ~X75
    o6 = ~X82
    o7 = ~N83

    seg_a = o7
    seg_b = o4
    seg_c = o6
    seg_d = o2
    seg_e = o5
    seg_f = o3
    seg_g = o1

    segs = [
        seg_a,
        seg_b,
        seg_c,
        seg_d,
        seg_e,
        seg_f,
        seg_g,
    ]
    return segs


def unpick_reduced_beforeramfolding():

    # need to think about NOR = ~(x | y) == XY=00
    """

nor(a,b) = a==0 . b==0
nor(a, nor(b,c))

nor(x, nor(a,b))
== x==0 . nor(a,b)==0
== ~x . ~nor(a,b)
== ~x. (a | b)
    """

    a, b, c, d = ttas(4, (4, 4))
    A, B, C, D = a, b, c, d

    AxC = A ^ C             # ** 2 = 1 3
    BnD = B & D             # ** 3 = 1 1 2
    AxD = A ^ D             # ** 3 = 1 2 3

    X11 = AxC ^ B           #    2 = 2 2
    X12 = BnD ^ C           #    2 = 2 2
    # O13 = BnD | AxD       #    1 = 5

    # N21 = ~(X11 | X12)      #    2 = 3 out
    # ***NEEDED***
    X22 = X11 ^ AxD         #    2 = 3 7
    # N23 = ~(X12 | BnD)      #    2 = 3 7
    # N23 = ~X12 & ~BnD
    # ***NEEDED***
    nN23 = (X12 | BnD)

    _t = ~(X11 | X12)  # was N21
    OUT1 = _t
    # ***NEEDED***
    N31 = ~(_t | AxC)       #    4 = 5 6 7 7
    # N32 = ~(X22 | AxD)      #    1 = 4
    # N33 = ~(N23 | A)        #    1 = 8

    _t = ~(X22 | AxD)       # was N32
    # ***NEEDED***
    X41 = _t ^ A            #    3 = 7 7 8

    _t = BnD | AxD          # was O13
    # ***NEEDED***
    O51 = N31 | _t          #    2 = 7 7

    _t = N31 | D           # was O61
    OUT2 = _t & X22        # was A71
    OUT3 = ~(N31 | X41)      # was N72
    # A73 = N31 & D           #    1 = 8

    # ***NEEDED***
    A74 = X41 & B           #    2 = 8 8
    OUT5 = O51 ^ A           # was X75
    # N76 = ~(O51 | N23)      #    1 = 8

    _t = N31 & D            # was A73
    OUT4 = _t | A74         # was O81
    # _t = ~(O51 | N23)       # was N76
    _t = ~O51 & nN23
    OUT6 = A74 ^ _t          # was X82
    # _t = ~(N23 | A)         # was N33
    _t = ~A & nN23
    OUT7 = ~(X41 | _t)       # was N83

    o1 = ~OUT1
    o2 = ~OUT2
    o3 = ~OUT3
    o4 = ~OUT4
    o5 = ~OUT5
    o6 = ~OUT6
    o7 = ~OUT7

    seg_a = o7
    seg_b = o4
    seg_c = o6
    seg_d = o2
    seg_e = o5
    seg_f = o3
    seg_g = o1

    segs = [
        seg_a,
        seg_b,
        seg_c,
        seg_d,
        seg_e,
        seg_f,
        seg_g,
    ]
    return segs


def unpick_reduced():

    # need to think about NOR = ~(x | y) == XY=00
    """

nor(a,b) = a==0 . b==0
nor(a, nor(b,c))

nor(x, nor(a,b))
== x==0 . nor(a,b)==0
== ~x . ~nor(a,b)
== ~x. (a | b)
    """

    a, b, c, d = ttas(4, (4, 4))
    A, B, C, D = a, b, c, d

    t_1 = A ^ C             # t1=AxC:  ** 2 = 1 3
    t_2 = B & D             # t2=BnD:  ** 3 = 1 1 2
    t_3 = A ^ D             # t3=AxD:  ** 3 = 1 2 3
    t_4 = t_1 ^ B           # t1=AxC: t4=X11:  2 = 2 2
    t_5 = t_2 ^ C           # t2=BnD: t5=X12  2 = 2 2

    _t = (t_4 | t_5)  # was N21 : t4=X11: t5=X12
    seg_g = _t
    _t = ~_t
    # ***NEEDED***
    t_1 = ~(_t | t_1)       # t1 WAS=AxC NOW=N31:   4 = 5 6 7 7

    # ***NEEDED***
    t_5 = (t_5 | t_2)      # t2=BnD: t5 WAS=X12 NOW=nN23

    # ***NEEDED***
    t_4 = t_4 ^ t_3         # t3=AxD: t4 WAS=X11 NOW=X22:   2 = 3 7

    _t = t_2 | t_3          # t2=BnD: t3=AxD: was O13
    t_2 = 'now-unused'  # was BnD

    # ***NEEDED***
    t_2 = t_1 | _t          # t1=N31: t2=O51   2 = 7 7

    _t = ~(t_4 | t_3)       # t3=AxD: t4=X22: was N32
    # ***NEEDED***
    t_3 = _t ^ A            # t3=X41:   3 = 7 7 8

    _t = t_1 | D           # t1=N31: was O61
    seg_d = ~(_t & t_4)        # t4=X22: was A71
    t_4 = 'now-unused'  # was X22

    seg_f = t_1 | t_3      # t1=N31: t3=X41: was N72

    # ***NEEDED***
    t_4 = t_3 & B           # t3=X41: t4=A74:  2 = 8 8

    seg_e = ~(t_2 ^ A)           # t2=O51: was X75

    _t = t_1 & D            # t1=N31: was A73
    seg_b = ~(_t | t_4)         #  t4=A74: was O81

    # _t = ~t_2 & t_5     # t5=nN23: t2=O51:
    # seg_c = ~(t_4 ^ _t)          # t4=A74: was X82
    _t = t_2 | ~t_5
    seg_c = _t ^ t_4

    _t = ~A & t_5       # t5=nN23
    seg_a = (t_3 | _t)       # was N83 : t3=X41

    segs = [
        seg_a,
        seg_b,
        seg_c,
        seg_d,
        seg_e,
        seg_f,
        seg_g,
    ]
    return segs


def check_result(segs, display_all=False):
    for seg in segs:
        pa(seg.flatten())

    for i in range(16):
        if display_all:
            print('')
            print(f'N = {i:02x}')

        outputs = [
            seg.flatten()[i]
            for seg in segs
        ]

        if display_all:
            print(disp_7seg(outputs))

        # Also check against known-correct answers
        exp_segs_result = seg_nums_usage[:, i].astype(int)
        # EXCEPT that the map calculated here is different...
        if i == 9:
            # special case with slightly different expected answer
            assert np.all(exp_segs_result == [1, 1, 1, 1, 0, 1, 1])
            exp_segs_result[3] = 0
        ok = np.all(exp_segs_result == outputs[:7])
        if not ok:
            out_ints = np.array(outputs).astype(int)
            print(f'  diff@{i:02x} : expect={exp_segs_result} got={out_ints}')
            assert ok


if __name__ == '__main__':
    segs = unpick_reduced()
    check_result(segs, display_all=False)
