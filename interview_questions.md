1. The CALL instruction doesn't allow you to pass any arguments. What are some
   ways to effectively get arguments to a subroutine?

At the machine level, functions are known as subroutines. You can call them and return from them, 
just like functions in higher-level languages. You can call a subroutine(i.e.push the address of the next instruction onto the stack,
move the PC to the address of the subroutine) and it can return from that subroutine(i.e. pop the value from the top of the stack into the PC.)

2. What's the result of bitwise-AND between `0b110` and `0b011`?

1011000000010000

3. Convert the 8-bit binary number 0bXXXXXXXX (PM's choice) to hex.

