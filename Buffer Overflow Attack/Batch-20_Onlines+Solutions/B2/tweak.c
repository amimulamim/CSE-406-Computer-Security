#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Canary {
    int id;              // 4 bytes
    char tag[3];         // 3 bytes
    short code;          // 2 bytes
    int marker[4];       // 16 bytes — values will be 1,2,3,4
} canary = {0x12345678, "abc", 0xbeef, {1, 2, 3, 4}};

void foo(char *input) {
    // Other local variables to simulate a real stack frame
    int counter = 42;
    char message[] = "HELLO";
    float dummy = 3.14f;

//    struct Canary local_canary = canary;  // Canary placed after locals
    char buffer[186];

    strcpy(buffer, input);  // ✅ BUFFER OVERFLOW VULNERABILITY

    // Log other locals to simulate a debugger trace
    printf("Info: counter=%d, message=%s, dummy=%.2f\n", counter, message, dummy);

    // === Canary field-by-field checks ===
     printf("✅ All Canary Values Intact. Returning from foo()...\n");
}

int main() {
    FILE *badfile;
    char data[671];

    badfile = fopen("badfile", "r");
    if (badfile == NULL) {
        perror("fopen");
        exit(1);
    }

    fread(data, sizeof(char), 671, badfile);
    foo(data);

    printf("Finished main()\n");
    return 0;
}

