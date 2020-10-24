#include <stdlib.h>
#include <stdio.h>
 
int main(void)
{
 unsigned long long i = 0;
 for (unsigned int j = 0; j <= 5000000; j++)
  i += j;
 printf("Hello world! %llu \n", i);
  return EXIT_SUCCESS;
}