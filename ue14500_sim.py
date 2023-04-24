from dataclasses import dataclass
from pprint import pprint

import numpy as np

#
# Reference design truth-table for desired 'correct' results
#
# truth table, matching the on/off patterns in the design notes
segs_tt_text = """
    1011 0111 1110 1011
    1111 1001 1110 0100
    1101 1111 1111 0100
    1011 0110 1101 1110
    1010 0010 1011 1111
    1000 1110 1111 1011
    0011 1110 1111 0111
"""
# tidy that all up into a character array
seg_rows = segs_tt_text.split('\n')
seg_row_chars = [
    [
        row[i] for i in range(len(row))
        if row[i].isalnum()
    ]
    for row in seg_rows if len(row) > 5
]
seg_nums_usage = np.array(seg_row_chars)


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


# Optional printout for design-table results in 7-seg form
def show_segs_design():
    # Display 7-seg for each input value according to a truth-table
    # Just here to test the design truth-table

    # output the 7-seg for each input value (==array column)
    n_segs, n_nums = seg_nums_usage.shape
    for i_num in range(n_nums):
        print('')
        print(f'@{i_num:02x}')
        outputs = seg_nums_usage[:, i_num].astype(int)
        print(disp_7seg(outputs))

# print('\n\nDESIGN ..')
# show_segs_design()
# exit(0)

# Memory-addressed stores
# lower-address reads come from here
inputs = [0] * 8
# lower-address writes go to here
outputs = [0] * 8
# higher-address r/w go here
ram = [0] * 8
RAM_BASE = 100  # Addresses >= this are r/w locations in the ram

# storage for building the program (a sort of one-pass assembler)
# (all accessed as globals for now, to simplify referencing)

# instruction codes for each instruction
instrs = []
# operand addresses for each instruction
addrs = []
# labels used to point to operand addresses
# (e.g. data variables or jump targets)
labels = {}


# Functions defining the memory map
# i.e. what read + write operations to different locations do
def _resolve_addr(addr):
    """Get the 'real' address, looking it up if passed a label."""
    if isinstance(addr, str):
        # strings index into the 'labels' array
        addr = labels[addr]
    return addr

def load_databit(addr):
    """Read a bit from an address."""
    addr = _resolve_addr(addr)
    if addr >= RAM_BASE:
        result = ram[addr - RAM_BASE]
    else:
        result = inputs[addr]
    return result

def save_databit(addr, val):
    """Write a bit to an address."""
    addr = _resolve_addr(addr)
    if addr >= RAM_BASE:
        ram[addr - RAM_BASE] = val
    else:
        outputs[addr] = val

# Internal execution state of the machine
# Note: not including i/o, which are treated as separate from the 'cpu'
@dataclass
class State:
    rr: int = 0
    pc: int = 0
    stopped: bool = False

# Machine state variable (global for now, to simplify referencing)
state = State()


#### op functions
# See 'run_code' for how they are actually invoked

# opcode table: maps each opcode name to a runnable "op_function"
ops = {}

def op(fn):
    # A function decorator to record the "op function" in the opcode table
    ops[fn.__name__[3:]] = fn

@op
def op_ld(addr):
    state.rr = load_databit(_resolve_addr(addr))
    state.pc += 1

@op
def op_sto(addr):
    save_databit(_resolve_addr(addr), state.rr)
    state.pc += 1

@op
def op_and(addr):
    state.rr &= load_databit(_resolve_addr(addr))
    state.pc += 1


@op
def op_or(addr):
    state.rr |= load_databit(_resolve_addr(addr))
    state.pc += 1

@op
def op_xor(addr):
    state.rr ^= load_databit(_resolve_addr(addr))
    state.pc += 1

@op
def op_one(addr=None):
    state.rr = 1
    state.pc += 1

@op
def op_skz(addr=None):
    resolved_addr = _resolve_addr(addr)
    if  resolved_addr is not None:
        if resolved_addr != state.pc + 2:
            print(f'    !! @pc={state.pc} SKZ label("{addr}")={resolved_addr} : not matching pc+1')
    if state.rr:
        state.pc += 1
    else:
        state.pc += 2

@op
def op_jmp(addr=None):
    state.pc = _resolve_addr(addr)

@op
def op_stop(addr=None):
    state.stopped = True

# Debug ops table
# print('\nOPS...')
# pprint(ops)
# print('')

#
# functions to run code
#

def showstate():
    return f'STATE: rr={state.rr}, pc={state.pc}, input={inputs}, ram={ram}, output={outputs}'


def run_code(step=False, showsteps=False):
    global state
    state.rr = 0
    state.pc = 0
    state.stopped = False

    if step:
        showsteps = True

    while not state.stopped:
        if showsteps:
            print(showstate())
        instr = instrs[state.pc]
        addr = addrs[state.pc]
        if showsteps:
            print(f'NEXT STEP : {instr}({addr} = {_resolve_addr(addr)})')
        if step:
            input()
        if showsteps:
            print('')
        ops[instr](addr)

    if showsteps:
        print(f'\nSTOPPED')
        print(showstate())

#
# code composition functions (these are basically like macros!)
#

def _add_instr(fn, addr):
    instrs.append(fn)
    # Note: "addrs" can also labels, as well as resolved numbers
    addrs.append(addr)

def ld(addr):
    _add_instr('ld', addr)

def sto(addr):
    _add_instr('sto', addr)

def or_(addr):
    _add_instr('or', addr)

def and_(addr):
    _add_instr('and', addr)

def xor(addr):
    _add_instr('xor', addr)

def one(addr=0):
    _add_instr('one', addr)

def skz(name=None):
    _add_instr('skz', name)

def jmp(name):
    _add_instr('jmp', name)

def _LABEL(name):
    # A pseudo-operation : assign an address label, *don't* add an instruction
    labels[name] = len(instrs)

def _HALT():
    # This is a real operation, but the *opcode* is a pseudo-op !
    # - since 'STOP' is not an instruction in the real processor
    _add_instr('stop', 0)


#
# Code definitions for this example
#

# setup constant addresses as pre-loaded labels

#inputs
labels['A'] = 0
labels['B'] = 1
labels['C'] = 2
labels['D'] = 3

# ram
labels['c_ne_d'] = RAM_BASE + 1
# labels['tmp'] = RAM_BASE + 2
labels['patt_0111'] = RAM_BASE + 3
labels['patt_1011'] = RAM_BASE + 4
labels['patt_1110'] = RAM_BASE + 5

#outputs
labels['seg_a'] = 0
labels['seg_b'] = 1
labels['seg_c'] = 2
labels['seg_d'] = 3
labels['seg_e'] = 4
labels['seg_f'] = 5
labels['seg_g'] = 6

#
# routines to build various code sections (i.e. add them to code tables)
#
def init__c_ne_d():
    ld('C')
    xor('D')
    sto('c_ne_d')

individual_seg_functions = False
if individual_seg_functions:
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


def all_segs():
    """
    A function that calculates all segments at once,
    sharing work where possible.
    """

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
    # one()
    # xor('c_ne_d')
    # or_('C')
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

    # ld('C')
    # or_('D')
    # sto('tmp')
    # one()
    # xor('tmp')
    # 1000
    # one()
    xor('patt_0111')  # using rr=1 from prev
    sto('seg_f')

    # xor('c_ne_d')  # using rr=1 from previous
    # or_('C')
    # # 1011
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

    # one()
    # xor('C')
    # or_('c_ne_d')
    # # 1110
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

    # one()
    xor('c_ne_d')  # using rr=1 from prev
    or_('D')
    # 1101
    sto('seg_d')

    # xor('C')    # using rr=1 from prev
    # or_('c_ne_d')
    # # 1110
    ld('patt_1110')
    sto('seg_b')   # NB CxD | ~C used elsewhere...

    # one()
    # xor('c_ne_d')
    # or_('C')
    # # 1011
    ld('patt_1011')
    jmp('x__set_e_DONE')

    #
    # AB=11 case, segs bdefg
    #
    _LABEL('x__ab11')
    # ld('c_ne_d')
    # and_('D')
    # # 0100
    xor('patt_1011')  # using rr=1 from jump
    sto('seg_b')

    # one()
    # xor('C')  # using rr=1
    # or_('c_ne_d')
    # # 1110
    ld('patt_1110')
    sto('seg_d')

    # one()
    # xor('c_ne_d')
    # or_('C')
    # # 1011
    ld('patt_1011')
    sto('seg_f')

    # ld('C')
    # or_('D')
    ld('patt_0111')
    # 0111
    sto('seg_g')

    one()  # seg_e == 1 for AB=11

    _LABEL('x__set_e_DONE')
    sto('seg_e')


# build the actual code table
init__c_ne_d()
all_segs()
# seg_a()
# seg_b()
# seg_c()
# seg_d()
# seg_e()
# seg_f()
# seg_g()
_HALT()

# output the code table (for debug)
print('')
print('CODE:')
pprint(list(zip(
    range(len(instrs)),
    instrs,
    [
        f'{addr} = {_resolve_addr(addr)}'
        for addr in addrs
    ]
)))

#
# Test runs code
#

def set_inputs(x):
    # Set inputs from an input value to be decoded
    for i in range(8):
        mask = 1 << i
        bit = 1 if x & mask else 0
        inputs[3 - i] = bit


# Debug run contols
# dbg_each_input = True
dbg_each_input = False

show_7s = True
# show_7s = False

catch_result_errors = True

for i in range(16):
    if dbg_each_input:
        print(f'*** next input code={i} ')

    set_inputs(i)
    if dbg_each_input:
        print('BEFORE: ' + showstate())

    # neither of these should be needed: it should set every seg, every time!
    # outputs = [0 for _ in outputs]
    # outputs = [1 for _ in outputs]

    run_code(step=False, showsteps=False)

    if dbg_each_input:
        print('AFTER: ' + showstate())

    if i%4 == 0:
        print('-')
    print(f' {i:02x} {inputs[:4]} -> {outputs}')

    if show_7s:
        print(disp_7seg(outputs))

    exp_segs_result = seg_nums_usage[:, i].astype(int)
    ok = np.all(exp_segs_result == outputs[:7])
    if catch_result_errors:
        assert ok
    if not ok:
        print(f'  *** FAIL: expected={exp_segs_result}')

    if dbg_each_input:
        print('')

