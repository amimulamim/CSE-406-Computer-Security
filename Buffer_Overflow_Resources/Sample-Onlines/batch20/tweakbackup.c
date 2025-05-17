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

    struct Canary local_canary = canary;  // Canary placed after locals
    char buffer[186];

    strcpy(buffer, input);  // ✅ BUFFER OVERFLOW VULNERABILITY

    // Log other locals to simulate a debugger trace
    printf("Info: counter=%d, message=%s, dummy=%.2f\n", counter, message, dummy);

    // === Canary field-by-field checks ===
    if (local_canary.id != canary.id) {
        printf("[!] Canary ID corrupted! Expected: 0x%x, Found: 0x%x\n", canary.id, local_canary.id);
    }
    if (strncmp(local_canary.tag, canary.tag, 3) != 0) {
        printf("[!] Canary TAG corrupted! Expected: %c%c%c, Found: %c%c%c\n",
               canary.tag[0], canary.tag[1], canary.tag[2],
               local_canary.tag[0], local_canary.tag[1], local_canary.tag[2]);
    }
    if (local_canary.code != canary.code) {
        printf("[!] Canary CODE corrupted! Expected: 0x%x, Found: 0x%x\n", canary.code, local_canary.code);
    }
    for (int i = 0; i < 4; i++) {
        if (local_canary.marker[i] != canary.marker[i]) {
            printf("[!] Canary MARKER[%d] corrupted! Expected: %d, Found: %d\n",
                   i, canary.marker[i], local_canary.marker[i]);
        }
    }

    // Final deep check
    if (memcmp(&local_canary, &canary, sizeof(canary)) != 0) {
        printf("💥 STACK CORRUPTION detected!\n");
        exit(1);
    }

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

