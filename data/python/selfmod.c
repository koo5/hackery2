#include <stdio.h>
#include <sys/mman.h> // linux
#include <stdlib.h>

int main(void) {
    unsigned char *a = mmap(NULL, 7, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|
                            MAP_ANONYMOUS, -1, 0); // get executable memory
    a[0] = 0b11000111; // mov (x86_64), immediate mode, full-sized (32 bits)
    a[1] = 0b11000000; // to register rax (000) which holds the return value
                       // according to linux x86_64 calling convention 
    a[6] = 0b11000011; // return
    
    
    unsigned char *b = malloc(7);
    
    unsigned char *c = b;
    
for (int i = 0; i < 65536; i++)
{
    for (c[2] = 0; c[2] < 255; c[2]++) { // incr immediate data after every run
        // rest of immediate data (c[3:6]) are already set to 0 by MAP_ANONYMOUS
       /* printf("%d ", */((int (*)(void)) c)()/*)*/; // cast c to func ptr, call ptr
    }
   
}
    return 0;
}
