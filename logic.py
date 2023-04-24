import numpy as np

def ttas(n_bits, shape=None):
    n = 2 ** n_bits
    if shape is None:
        shape = (n,)
    base = np.arange(n).reshape(shape)
    return [
        ((base & (2 ** i)) != 0)
        for i in list(range(n_bits))[::-1]
    ]

def pa(a):
    print(a.astype(int))

def seg_a():
    a, b, c, d = ttas(4, (4, 4))
    print(a)
    print('')
    print(b)

    print('')
    axb = a ^ b
    print('AxB')
    pa(axb)

    print('')
    cxd = c ^ d
    print('CxD')
    pa(cxd)

    print('')
    half_aeqb = ~axb & (~cxd | c)
    print('half_aeqb == ~AxB . (~CxD + C)')
    pa(half_aeqb)

    print('')
    half_aneb = axb & (cxd | a^c)
    print('half_aneb == AxB . (CxD + AxC)')
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
    print('half_d0 = ~D . (~AxB + C)')
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

seg_e()