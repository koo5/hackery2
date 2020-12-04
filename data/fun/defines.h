#ifdef PASCAL_ALGOL

#define begin {
#define end   }

#define then {
#define done }
#define fi   }
#define esac }
#define od   }
#define endsw }
#define endif }

#endif /*PASCAL_ALGOL*/

#ifdef SIMPLE_C

#define unless(x) while(!x)
#define or ||
#define nor && !
#define not !
#define import #include
#define is ==

#endif /*SIMPLE_C*/

#ifdef OBSFC

#define f float
#define c char
#define v void
#define cc case
#define g goto
#define i int
#define ui unsigned int
#define l long
#define ll long long
#define a asm
#define s switch
#define ff for
#define d #define
#define dd double
#define ccc continue
#define inc #include
#define std #include <stdio.h> \
#include <stdlib.h>
#define st char*
#define cns const
#define wh while
#define en enum
#define ex extern
#define pnt printf
#define ma int main()
#define re return
#define end return 0;
#define z );
#define a ("
#define h ");

#endif /*OBSFC*/

