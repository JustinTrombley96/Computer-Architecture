"""CPU functionality."""
import sys
class CPU:
    """Main CPU class."""
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


    # def get_index(self, binary):
    #     binary_str = str(binary)
    #     binary_str.replace("0b", '')
    #     return int(binary_str, 2) 


    def ldi(self, reg_num, value):
        index = reg_num
        self.reg[index] = value


    def prn(self, reg_num):
        index = reg_num
        print(self.reg[index])

    def push(self, index):
        self.reg[7] -= 1
        value = self.reg[index]
        ram_address = self.reg[7]
        self.ram[ram_address] = value

    def pop(self, index):
        ram_address = self.reg[7]
        value = self.ram[ram_address]
        self.reg[index] = value
        self.reg[7] += 1
    



    def run(self):
        """Run the CPU."""
        # * `IR`: Instruction Register, contains a copy of the currently executing instruction
        ir = self.ram_read(self.pc)
        HLT = 0b00000001
        LDI = 0b10000010 
        PRN = 0b01000111
        MUL = 0b10100010
        POP = 0b01000110
        PUSH = 0b01000101

        while ir != HLT:
            ir = self.ram_read(self.pc)
            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction needs them.
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            if ir == MUL:
                #Run the ALU on both registers
                self.alu('MUL', operand_a, operand_b)
                self.pc += 2
                #Run the counter up by 3
            elif ir == LDI:
                self.ldi(operand_a, operand_b)
                self.pc += 2
            elif ir == PRN:
                self.prn(operand_a)
                self.pc +=1
            elif ir == POP:
                self.pop(operand_a)
                self.pc +=1
            elif ir == PUSH:
                self.push(operand_a)
                self.pc += 1
            self.pc += 1