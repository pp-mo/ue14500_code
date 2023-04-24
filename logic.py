import numpy as np

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


def disp_7seg(outputs):
    # Turn an output array into a string 'displaying' 7-segments
    bit_outputs = [
        '#' if bit else '_'
        for bit in outputs
    ]
    lines = """
       00
     5    1
     5    1
       66
     4    2
     4    2
       33
    """
    for i_bit in range(7):
        lines = lines.replace(f'{i_bit}', bit_outputs[i_bit])
    return lines


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
    for seg in segs:
        pa(seg.flatten())

    for i in range(16):
        print('')
        print(f'N = {i:02x}')
        outputs = [
            seg.flatten()[i]
            for seg in segs
        ]
        # outputs = np.array(outputs)
        print(disp_7seg(outputs))

unpick()
