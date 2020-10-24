#include <stdio.h>

float Q_rsqrt( float number )
{
  long i;
  float x2, y;
  const float threehalfs = 1.5F;
 
  printf("Number: %.5f\n", number); 

  x2 = number * 0.5F;
  y  = number;
  i  = * ( long * ) &y;

  printf("casted y(i): %ld number * 0.5F: %.5f\n", i, x2);

  i  = 0x5f3759df - ( i >> 1 );

  printf("i after math stuff %d\n", i);

  y  = * ( float * ) &i;

  printf("back to float %.5f", y);

  y  = y * ( threehalfs - ( x2 * y * y ) ); // 1st iteration

  printf("y after newton's method: %.5f", y);

  return y;
}

int main()
{
  Q_rsqrt(49.0f);
  return 0;
}
