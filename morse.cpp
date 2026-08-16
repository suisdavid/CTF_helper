#include <iostream>
#include <string>
#include <vector>
using namespace std;

string s="-....-------------..-----.---------.-------------...-----------------..--....--.------.-----..---...-----------.--.-.--.-----.-.---..------.---------...------.---------...-....";
int n;
vector<pair<int,char> >dp[1024];
long long ans[1024];
char morse_code(string t)
{
	if(t==".-")
	{
		return 'A';
	}
	else if (t=="-...")
	{
		return 'B';
	}
	else if (t=="-.-.")
	{
		return 'C';
	}
	else if (t==".")
	{
		return 'E';
	}
	else if (t=="..-.")
	{
		return 'F';
	}
	else if (t=="--.")
	{
		return 'G';
	}
	else if (t=="....")
	{
		return 'H';
	}	
	else if (t=="..")
	{
		return 'I';
	}
	else if (t==".---")
	{
		return 'J';
	}
	else if (t=="-.-")
	{
		return 'K';
	}
	else if (t==".-..")
	{
		return 'L';
	}
	else if (t=="--")
	{
		return 'M';
	}
	else if (t=="-.")
	{
		return 'N';
	}
	else if (t=="---")
	{
		return 'O';
	}
	else if (t==".--.")
	{
		return 'P';
	}
	else if (t=="--.-")
	{
		return 'Q';
	}
	else if (t==".-.")
	{
		return 'R';
	}
	else if (t=="...")
	{
		return 'S';
	}
	else if (t=="-")
	{
		return 'T';
	}
	else if (t=="..-")
	{
		return 'U';
	}
	else if (t=="...-")
	{
		return 'V';
	}
	else if (t==".--")
	{
		return 'W';
	}
	else if (t=="-..-")
	{
		return 'X';
	}
	else if (t=="-.--")
	{
		return 'Y';
	}
	else if (t=="--..")
	{
		return 'Z';
	}
	else if (t==".----")
	{
		return '1';
	}
	else if (t=="..---")
	{
		return '2';
	}
	else if (t=="...--")
	{
		return '3';
	}
	else if (t=="....-")
	{
		return '4';
	}
	else if (t==".....")
	{
		return '5';
	}
	else if (t=="-....")
	{
		return '6';
	}
	else if (t=="--...")
	{
		return '7';
	}
	else if (t=="---..")
	{
		return '8';
	}
	else if (t=="----.")
	{
		return '9';
	}
	else if (t=="-----")
	{
		return '0';
	}
	else if (t=="..--..")
	{
		return '?';
	}
	else if (t=="-..-.")
	{
		return '/';
	}
	return 'a';//bad
}
void search(int id,string t)
{
	if (id==n){cout<<t<<endl;return;}
	int sz=dp[id].size();
	for(int i=0;i<sz;i++)
	{
		if ((dp[id][i].second>='0' &&dp[id][i].second<='9')||(dp[id][i].second>='A' &&dp[id][i].second<='F'))
		{
			search(dp[id][i].first,t+dp[id][i].second); 
		}
	}
}
int main()
{
	n=s.length();
	dp[n].push_back(make_pair(n,'a'));
	ans[n]=1;
	for (int i=n-1;i>=0;i--)
	{
		ans[i]=-1;
		for (int j=1;j<=6&&i+j<=n;j++)
		{
			if (dp[i+j].size()==0){continue;}
			char c=morse_code(s.substr(i,j));
			if (c=='a'){continue;}
			dp[i].push_back(make_pair(i+j,c));
		}
	}
	for (int i=0;i<n;i++)
	{
		int sz=dp[i].size();
		cout<<i<<" : "<<endl<<endl;;
		for (int j=0;j<sz;j++)
		{
			cout<<dp[i][j].second<<" "<<dp[i][j].first<<endl;
		}
		cout<<"----------------------------"<<endl<<endl;
	}
	search(0,"");
} 
