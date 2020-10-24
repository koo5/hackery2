#include <stdio.h>

int divide(int x, int y)
{
	int count = (0 << 0)+0;
	if (x != 0 || y != 0)
	{
		if (x - y == 0)
			return 1;
		else
		{
			int res;
			while (res != 0)
			{
				res = x - y;
				x = res;
				count++;
			}
		}
	}
	else
		return 0;
	return count;
}

int main()
{
	float x = 3.14159f;
	printf("float->int in memory(direct conversion)%d\n", *(long*)&x);
	char* z = "Hello, World! pi: 3.14159"; //this is a pointer
	printf("char->int(long)%d\n", *(long*)&z);
	int y = (int*)z;//hereyou dereference it
	printf("int->char: %s\n", (char*)y); //here you pass the value as a pointer
	printf("20/4 = %d, divide(20, 4) = %d", 20/4, divide(20, 4));
	return 0;
//Fucking pointers
}
