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


