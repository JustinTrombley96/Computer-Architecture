"""CPU functionality."""
import sys
class CPU:
    """Main CPU class."""
    ADD = 0b10100000
    SUB = 0b10100001
    MUL = 0b10100010
    DIV = 0b10100011
    MOD = 0b10100100

    INC = 0b01100101
    DEC = 0b01100110

    CMP = 0b10100111

    AND = 0b10101000
    NOT = 0b01101001
    OR = 0b10101010
    XOR = 0b10101011
    SHL = 0b10101100
    SHR = 0b10101101

    CALL = 0b01010000
    RET = 0b00010001

    INT = 0b01010010
    IRET = 0b00010011

    JMP = 0b01010100
    JEQ = 0b01010101
    JNE = 0b01010110
    JGT = 0b01010111
    JLT = 0b01011000
    JLE = 0b01011001
    JGE = 0b01011010

    NOP = 0b00000000

    HLT = 0b00000001

    LDI = 0b10000010

    LD = 0b10000011
    ST = 0b10000100

    PUSH = 0b01000101
    POP = 0b01000110

    PRN = 0b01000111
    PRA = 0b01001000



    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 
        # +-----------------------+
        # | FF  I7 vector         |    Interrupt vector table
        # | FE  I6 vector         |
        # | FD  I5 vector         |
        # | FC  I4 vector         |
        # | FB  I3 vector         |
        # | FA  I2 vector         |
        # | F9  I1 vector         |
        # | F8  I0 vector         |
        # | F7  Reserved          |
        # | F6  Reserved          |
        # | F5  Reserved          |
        # | F4  Key pressed       |    Holds the most recent key pressed on the keyboard
        # | F3  Start of Stack    |
        # | F2  [more stack]      |    Stack grows down
        # | ...                   |
        # | 01  [more program]    |
        # | 00  Program entry     |    Program loaded upward in memory starting at 0
        # +-----------------------+
        self.reg = [0] * 8
        #R5 is reserved as the interrupt mask (IM)
        #R6 is reserved as the interrupt status (IS)
        #R7 is reserved as the stack pointer (SP)
        # `PC`: Program Counter, address of the currently executing instruction
        self.pc = 0
        # * `FL`: Flags, see below  
        self.fl = 0  
    # Inside the CPU, there are two internal registers used for memory operations: the Memory Address Register (MAR) and the Memory Data Register (MDR). The MAR contains the address that is being read or written to. The MDR contains the data that was read or the data to write. You don't need to add the MAR or MDR to your CPU class, but they would make handy parameter names for ram_read() and ram_write(), if you wanted.   
    # * `MAR`: Memory Address Register, holds the memory address we're reading or writing
    # * `MDR`: Memory Data Register, holds the value to write or the value just read
        self.reg[7] = 0xf4
        self.equal = 0
        self.dispatch= {}
        self.dispatch[self.ADD] = self.add
        self.dispatch[self.MUL] = self.mul
        self.dispatch[self.HLT] = self.hlt
        self.dispatch[self.LDI] = self.ldi
        self.dispatch[self.PUSH] = self.push
        self.dispatch[self.POP] = self.pop
        self.dispatch[self.CALL] = self.call
        self.dispatch[self.RET] = self.ret
        self.dispatch[self.CMP] = self.cmp  
        self.dispatch[self.JMP] = self.jmp  
        self.dispatch[self.JEQ] = self.jeq  
        self.dispatch[self.JNE] = self.jne
        self.dispatch[self.PRN] = self.prn


    def ram_read(self, MAR): 
    # should accept the address to read and return the value stored there.
        if MAR < len(self.ram):
            return self.ram[MAR]
        else:
            return None


    def ram_write(self, MAR, MDR): 
    # should accept a value to write, and the address to write it to. 
        self.ram[MAR] = MDR


    def load(self, program = None):
        """Load a program into memory."""
        if len(sys.argv) < 2:
            print("Please pass in a second filename: python3 in_and_out.py second_filename.py")
            sys.exit()
        try:
            address = 0
            with open(program) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    command = split_line.strip()
                    if command == '':
                        continue
                    instruction = int(command, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def hlt(self):
        exit()


#     ### LDI

# `LDI register immediate`

# Set the value of a register to an integer.

# Machine code:
# ```
# 10000010 00000rrr iiiiiiii
# 82 0r ii
# ```


    def ldi(self):
        target_register = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[target_register] = value
        self.pc = self.pc + 3

#         ### PRN

# `PRN register` pseudo-instruction

# Print numeric value stored in the given register.

# Print to the console the decimal integer value that is stored in the given
# register.

# Machine code:
# ```
# 01000111 00000rrr
# 47 0r
# ```


    def prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc = self.pc + 2


#         ### ADD

# *This is an instruction handled by the ALU.*

# `ADD registerA registerB`

# Add the value in two registers and store the result in registerA.

# Machine code:
# ```
# 10100000 00000aaa 00000bbb
# A0 0a 0b
# ```

    def add(self):
        self.alu('ADD', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc = self.pc + 3

# ### MUL

# *This is an instruction handled by the ALU.*

# `MUL registerA registerB`

# Multiply the values in two registers together and store the result in registerA.

# Machine code:
# ```
# 10100010 00000aaa 00000bbb
# A2 0a 0b
# ```


    def mul(self):
        self.alu('MUL', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc = self.pc + 3


#         ### PUSH

# `PUSH register`

# Push the value in the given register on the stack.

# 1. Decrement the `SP`.
# 2. Copy the value in the given register to the address pointed to by
#    `SP`.

# Machine code:
# ```
# 01000101 00000rrr
# 45 0r
# ```

    def push(self):
        self.reg[7] = self.reg[7] - 1
        self.ram_write(self.reg[7], self.reg[self.ram_read(self.pc + 1)])
        self.pc = self.pc + 2


#         ### POP

# `POP register`

# Pop the value at the top of the stack into the given register.

# 1. Copy the value from the address pointed to by `SP` to the given register.
# 2. Increment `SP`.

# Machine code:
# ```
# 01000110 00000rrr
# 46 0r
# ```


    def pop(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.reg[7])
        self.reg[7] = self.reg[7] + 1
        self.pc = self.pc + 2


#         ### CALL register

# `CALL register`

# Calls a subroutine (function) at the address stored in the register.

# 1. The address of the ***instruction*** _directly after_ `CALL` is
#    pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
# 2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.

# Machine code:
# ```
# 01010000 00000rrr
# 50 0r
# ```


    def call(self):
        self.reg[7] = self.reg[7] - 1
        self.ram_write(self.reg[7], self.pc + 2)
        self.pc = self.reg[self.ram_read(self.pc + 1)]


#         ### RET

# `RET`

# Return from subroutine.

# Pop the value from the top of the stack and store it in the `PC`.

# Machine Code:
# ```
# 00010001
# 11
# ```

    def ret(self):
        self.pc = self.ram_read(self.reg[7])
        self.reg[7] = self.reg[7] + 1



    # ### CMP

    # *This is an instruction handled by the ALU.*

    # `CMP registerA registerB`

    # Compare the values in two registers.

    # * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

    # * If registerA is less than registerB, set the Less-than `L` flag to 1,
    #   otherwise set it to 0.

    # * If registerA is greater than registerB, set the Greater-than `G` flag
    #   to 1, otherwise set it to 0.

    # Machine code:
    # ```
    # 10100111 00000aaa 00000bbb
    # A7 0a 0b

    def cmp(self):
        if self.reg[self.ram_read(self.pc + 1)] == self.reg[self.ram_read(self.pc + 2)]:
            self.equal = 1
        else:
            self.equal = 0
        self.pc += 3


    # JMP

    # `JMP register`

    # Jump to the address stored in the given register.

    # Set the `PC` to the address stored in the given register.

    # Machine code:
    # ```
    # 01010100 00000rrr
    # 54 0r
    
    def jmp(self):
        self.pc = self.reg[self.ram_read(self.pc + 1)]
    




    #  JEQ

    # `JEQ register`

    # If `equal` flag is set (true), jump to the address stored in the given register.

    # Machine code:
    # ```
    # 01010101 00000rrr
    # 55 0r

    def jeq(self):
        if self.equal == 1:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2
    




    ### JNE

    # `JNE register`

    # If `E` flag is clear (false, 0), jump to the address stored in the given
    # register.

    # Machine code:
    # ```
    # 01010110 00000rrr
    # 56 0r
    # ```


    def jne(self):
        if self.equal == 0:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2
        




    def run(self):
        """Run the CPU."""

        running = True

        while running:
            ir = self.ram_read(self.pc)
            old_counter = self.pc

            if ir not in self.dispatch:
                print('Bad instruction')
                self.trace()
                self.hlt()

            self.dispatch[ir]()

            if self.pc == old_counter:
                self.pc = self.pc + 1