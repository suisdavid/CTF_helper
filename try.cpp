#include <stdio.h>
#include <time.h>
#include <stdlib.h>

char tab[4]={'W','A','S','D'};
int main()
{
	int t=time(0)/10;
	while (1)
	{
		int x=time(0)/10;
		if (x!=t)
		{
			t=x;srand(x);
			for (int i=0;i<10;i++)
			{
				printf("%c",tab[rand()%4]);
			}
			printf("\n");
		}
	}
} 
