// spray_vuln.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[100];  // You, the attacker, don’t know this size

    // No bounds check - buffer overflow vulnerability
    strcpy(buffer, input);

    printf("✅ Function returned safely. buffer = %p\n", buffer);
}

int main() {
    FILE *badfile;
    char data[600];  // May be larger than buffer in `vulnerable_function`

    badfile = fopen("badfile", "r");
    if (badfile == NULL) {
        perror("fopen");
        exit(1);
    }

    fread(data, sizeof(char), 600, badfile);
    vulnerable_function(data);

    printf("✅ Returned to main successfully.\n");
    return 0;
}

