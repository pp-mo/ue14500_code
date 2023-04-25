from ue14500_sim import (
    ld, sto, one, xor, and_, or_, xor, skz, jmp, _LABEL, _HALT
)

# Routines for calculating individual segment functions
# These have been replaced by 'all_segs', but are retained for reference
# Combining them all has reduced code length from ~135 to ~87

def seg_a():
    ld('A')
    xor('B')
    skz('a__a_eq_b')
    jmp('a__a_ne_b')
    _LABEL('a__a_eq_b')
    one()
    xor('c_ne_d')
    or_('C')
    jmp('a__set')

    _LABEL('a__a_ne_b')
    ld('c_ne_d')
    skz('a__ceqd')
    jmp('a__set')  # shortcut!
    _LABEL('a__ceqd')
    ld('A')
    xor('C')

    _LABEL('a__set')
    sto('seg_a')


def seg_b():
    ld('A')
    skz('b__a0')
    jmp('b__a1')

    _LABEL('b__a0')
    ld('B')
    skz('b__ab00')
    jmp('b__ab01')

    _LABEL('b__ab00')
    one()
    jmp('b__set')

    _LABEL('b__ab01')
    one()
    xor('c_ne_d')
    jmp('b__set')

    _LABEL('b__a1')
    ld('B')
    skz('b__ab10')
    jmp('b__ab11')

    _LABEL('b__ab10')
    one()
    xor('C')
    or_('c_ne_d')
    jmp('b__set')

    _LABEL('b__ab11')
    ld('c_ne_d')
    and_('D')

    _LABEL('b__set')
    sto('seg_b')


def seg_c():
    # out = AxB ...
    #       + ~A . (~CxD + D)
    #       +  A . (CxD.D)
    ld('A')
    xor('B')
    skz('c__aeqb')
    jmp('c__set')  # AxB --> 1

    _LABEL('c__aeqb')
    ld('A')
    skz('c__a0')
    jmp('c__a1')

    _LABEL('c__a0')
    one()
    xor('c_ne_d')
    or_('D')
    jmp('c__set')

    _LABEL('c__a1')
    ld('c_ne_d')
    and_('D')
    _LABEL('c__set')
    sto('seg_c')


def seg_d():
    ld('A')
    skz('d__a0')
    jmp('d__a1')
    _LABEL('d__a0')
    ld('B')
    skz('d__ab00')
    jmp('d__ab01')
    _LABEL('d__ab00')
    one()
    xor('c_ne_d')
    or_('C')
    jmp('d__set')

    _LABEL('d__ab01')
    ld('c_ne_d')
    jmp('d__set')

    _LABEL('d__a1')
    ld('B')
    skz('d__ab10')
    jmp('d__ab11')
    _LABEL('d__ab10')
    one()
    xor('c_ne_d')
    or_('D')
    jmp('d__set')

    _LABEL('d__ab11')
    one()
    xor('C')
    or_('c_ne_d')

    _LABEL('d__set')
    sto('seg_d')


def seg_e():
    ld('D')
    skz('e__d0')
    jmp('e__d1')

    _LABEL('e__d0')
    ld('C')
    skz('e__cd00')
    jmp('e__set')  # CD=10 --> 1

    _LABEL('e__cd00')
    one()
    xor('A')
    and_('B')
    sto('tmp')
    one()
    xor('tmp')
    jmp('e__set')

    _LABEL('e__d1')
    ld('C')
    skz('e__cd01')
    jmp('e__cd11')

    _LABEL('e__cd01')
    ld('A')
    and_('B')
    jmp('e__set')

    _LABEL('e__cd11')
    ld('A')

    _LABEL('e__set')
    sto('seg_e')


def seg_f():
    ld('C')
    skz('f__c0')
    jmp('f__c1')

    _LABEL('f__c0')
    ld('D')
    skz('f__cd00')
    jmp('f__cd01')

    _LABEL('f__cd00')
    one()
    jmp('f__set')

    _LABEL('f__cd01')
    ld('A')
    xor('B')
    jmp('f__set')

    _LABEL('f__c1')
    ld('D')
    skz('f__cd10')
    jmp('f__cd11')

    _LABEL('f__cd10')
    ld('A')
    or_('B')
    jmp('f__set')

    _LABEL('f__cd11')
    ld('A')

    _LABEL('f__set')
    sto('seg_f')


def seg_g():
    ld('B')
    skz('g__b0')
    jmp('g__b1')

    _LABEL('g__b0')
    ld('A')
    skz('g__ab00')
    jmp('g__set')  # A.~B --> 1

    _LABEL('g__ab00')
    ld('C')
    jmp('g__set')

    _LABEL('g__b1')
    ld('A')
    skz('g__ab01')
    jmp('g__ab11')

    _LABEL('g__ab01')
    one()
    xor('C')
    or_('c_ne_d')
    jmp('g__set')

    _LABEL('g__ab11')
    ld('C')
    or_('D')

    _LABEL('g__set')
    sto('seg_g')


##################################
# Other older routines, now removed from main 'ue14500_sim' code

from ue14500_sim import RAM_BASE, labels

def init__c_ne_d():
    labels['c_ne_d'] = RAM_BASE + 1
    ld('C')
    xor('D')
    sto('c_ne_d')


def all_segs():
    """
    A function that calculates all segments at once,
    sharing work where possible.
    """
    labels['patt_0111'] = RAM_BASE + 3
    labels['patt_1011'] = RAM_BASE + 4
    labels['patt_1110'] = RAM_BASE + 5

    # first pre-calculate some common terms based on specific patterns in the
    # inputs CD, which can be re-used with advantage
    ld('C')
    or_('D')
    sto('patt_0111')

    one()
    xor('c_ne_d')
    or_('C')
    sto('patt_1011')

    one()
    xor('C')
    or_('c_ne_d')
    sto('patt_1110')

    #
    # First, split on AxB / ~(AxB)
    #  : calculate 'a' and 'c' segments this way.
    ld('A')
    xor('B')
    skz('x__aeqb')
    jmp('x__aneb')

    # AxB == 0 cases for segs a+c
    _LABEL('x__aeqb')
    ld('patt_1011')
    sto('seg_a')

    ld('A')
    skz('xc__aeqb_a0')
    jmp('xc__aeqb_a1')

    _LABEL('xc__aeqb_a0')
    one()
    xor('c_ne_d')
    or_('D')
    # 1101
    jmp('x__setc')

    _LABEL('xc__aeqb_a1')
    ld('D')
    and_('c_ne_d')
    # 0100
    jmp('x__setc')

    # AxB == 1 cases for segs a+c
    _LABEL('x__aneb')
    ld('A')
    xor('C')
    or_('c_ne_d')
    sto('seg_a')
    one()  # AxB --> 1

    _LABEL('x__setc')
    sto('seg_c')

    #
    # Now split all the other segs (bdefg) by AB values
    #
    ld('A')
    skz('x__a0')
    jmp('x__a1')

    _LABEL('x__a0')
    ld('B')
    skz('x__ab00')
    jmp('x__ab01')

    #
    # AB=00 case, segs bdefg
    #
    _LABEL('x__ab00')
    one()
    sto('seg_b')

    xor('patt_0111')  # using rr=1 from prev
    sto('seg_f')

    ld('patt_1011')
    sto('seg_d')

    ld('C')
    sto('seg_g')

    one()
    xor('D')
    jmp('x__set_e_DONE')

    #
    # AB=01 case, segs bdefg
    #
    _LABEL('x__ab01')
    xor('c_ne_d')  # using rr==1 from jump
    sto('seg_b')

    ld('c_ne_d')
    sto('seg_d')

    ld('patt_1110')
    sto('seg_f')
    sto('seg_g')  # same value

    ld('c_ne_d')
    and_('C')
    # 0010
    jmp('x__set_e_DONE')

    _LABEL('x__a1')
    ld('B')
    skz('x__ab10')
    jmp('x__ab11')

    #
    # AB=10 case, segs bdefg
    #
    _LABEL('x__ab10')
    one()
    sto('seg_f')
    sto('seg_g')

    xor('c_ne_d')  # using rr=1 from prev
    or_('D')
    # 1101
    sto('seg_d')

    ld('patt_1110')
    sto('seg_b')   # NB CxD | ~C used elsewhere...

    ld('patt_1011')
    jmp('x__set_e_DONE')

    #
    # AB=11 case, segs bdefg
    #
    _LABEL('x__ab11')
    xor('patt_1011')  # using rr=1 from jump
    sto('seg_b')

    ld('patt_1110')
    sto('seg_d')

    ld('patt_1011')
    sto('seg_f')

    ld('patt_0111')
    sto('seg_g')

    one()  # seg_e == 1 for AB=11

    _LABEL('x__set_e_DONE')
    sto('seg_e')


if __name__ == '__main__':
    # Just build the 'old' code table + debug-output it,
    # So we see what it looked like
    init__c_ne_d()
    all_segs()
    _HALT()

    from ue14500_sim import show_code_table
    show_code_table()

    # NOTE: old table used 173 instructions
