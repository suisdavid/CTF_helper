#include <stdio.h>
#include <stdlib.h>
typedef unsigned long long ull;
int main()
{
	ull *p1=(ull *)malloc(3000),*p2=(ull *)malloc(3000),*p3=(ull *)malloc(3000);
	free(p3);free(p2);free(p1);
	printf("%p %p %p\n",p1,p2,p3);
	for (int i=-4;i<=4;i++)
	{
		printf("%x\n",*(p2+i));
	}
	
} 
