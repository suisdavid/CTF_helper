#include <iostream>
using namespace std;

int a[16]={126, 255, 149, 88, 179, 128, 201, 174, 82, 170, 177, 197, 4, 87, 21, 228};
int s[16]={119, 101, 108, 99, 111, 109, 101, 95, 116, 111, 95, 48, 111, 112, 115, 33};
int key[256];
char ans[17];
int x,y;
int main()
{
	for (int i=0;i<256;i++){key[i]=i;}
	x=0;
	for (int i=0;i<256;i++)
    {
		x=(x+key[i]+s[i%16])%256;
    	swap(key[i],key[x]);
	}
	x=0;y=0;
	for (int i=0;i<16;i++)
    {
		x++;
    	y=(y+key[x])%256;
    	swap(key[x],key[y]);
    	ans[i]=(key[(key[x]+key[y])%256]^a[i]);
	}
	cout<<ans<<endl;
}

