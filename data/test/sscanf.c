const int LINESIZE = 20;

#include <stdio.h>

int main ()
{

  char host[LINESIZE];
  char *s = "a:0";
  
  int display, screen;

  int res = sscanf(s, "%[a-zA-Z0-9.]:%d.%d", host, &display, &screen);

  printf ("%i",res);
  
  return 0;
}


