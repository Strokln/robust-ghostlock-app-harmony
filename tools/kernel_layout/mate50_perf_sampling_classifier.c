/*
 * DCO-AL00 ARM64 perf sampling classifier. READ-ONLY RESEARCH ONLY.
 * Two short CPU-clock perf runs; only sample counts and cpumodes printed.
 * No address or register contents read, retained or printed.
 */
typedef unsigned long long u64;
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef unsigned long usize;
struct attr {
 u32 type,size; u64 config,sample_period,sample_type,read_format,flags;
 u32 wakeup_events,bp_type; u64 bp_addr,bp_len,branch_sample_type,sample_regs_user;
 u32 sample_stack_user,clockid; u64 sample_regs_intr;
 u32 aux_watermark; u16 sample_max_stack,reserved;
};
_Static_assert(sizeof(struct attr)==112,"perf ABI mismatch");
struct ts {long sec,nsec;};
#define NR_WRITE 64
#define NR_CLOSE 57
#define NR_PERF_EVENT_OPEN 241
#define NR_EXIT_GROUP 94
#define NR_MMAP 222
#define NR_MUNMAP 215
#define NR_IOCTL 29
#define NR_CLOCK_GETTIME 113
#define NR_GETPID 172
#define PERF_SAMPLE_IP (1ULL<<0)
#define PERF_SAMPLE_REGS_INTR (1ULL<<18)
#define PERF_FLAG_DISABLED (1ULL<<0)
#define PERF_FLAG_EXCLUDE_USER (1ULL<<4)
#define PERF_FLAG_EXCLUDE_HV (1ULL<<6)
#define PROT_READ 1
#define PROT_WRITE 2
#define MAP_SHARED 1
#define PERF_EVENT_IOC_ENABLE 0x2400
#define PERF_EVENT_IOC_DISABLE 0x2401
#define PERF_EVENT_IOC_RESET 0x2403
#define PERF_RECORD_SAMPLE 9
#define PERF_RECORD_LOST 2
#define PAGE 4096
#define PAGES 64
#define RING_SIZE (PAGES*PAGE)
static inline long sys6(long nr,long a0,long a1,long a2,long a3,long a4,long a5){
 register long x0 asm("x0")=a0,x1 asm("x1")=a1,x2 asm("x2")=a2;
 register long x3 asm("x3")=a3,x4 asm("x4")=a4,x5 asm("x5")=a5;
 register long x8 asm("x8")=nr;
 asm volatile("svc #0":"+r"(x0):"r"(x1),"r"(x2),"r"(x3),"r"(x4),"r"(x5),"r"(x8):"memory");
 return x0;
}
static void p(const char*s){usize n=0;while(s[n])n++;(void)sys6(NR_WRITE,1,(long)s,n,0,0,0);}
static void num(u64 v){
 char s[32];usize i=sizeof(s);
 do{s[--i]=(char)('0'+v%10);v/=10;}while(v);
 (void)sys6(NR_WRITE,1,(long)(s+i),sizeof(s)-i,0,0,0);
}
static void err(long result){p("FAIL errno=");num((u64)-result);p("\n");}
static u64 ms(void){
 struct ts t={0};if(sys6(NR_CLOCK_GETTIME,1,(long)&t,0,0,0,0)<0)return 0;
 return (u64)t.sec*1000ULL+(u64)t.nsec/1000000ULL;
}
static u8 byte_at(const u8*buf,u64 pos){return buf[pos&(RING_SIZE-1)];}
static u16 read16(const u8*buf,u64 pos){return (u16)byte_at(buf,pos)|((u16)byte_at(buf,pos+1)<<8);}
static u32 read32(const u8*buf,u64 pos){return (u32)read16(buf,pos)|((u32)read16(buf,pos+2)<<16);}
static u64 read64(const u8*buf,u64 pos){return (u64)read32(buf,pos)|((u64)read32(buf,pos+4)<<32);}
static u64 load64(const u8*base,usize offset){return __atomic_load_n((const u64 *)(base+offset),__ATOMIC_ACQUIRE);}
static volatile u64 activity;
static void run(const char*name,int kernel_only){
 p(name);p("\n");
 struct attr a={0};a.type=1;a.size=sizeof(a);a.config=0;a.sample_period=1000000;
 a.sample_type=PERF_SAMPLE_IP|PERF_SAMPLE_REGS_INTR;a.sample_regs_intr=1;
 a.flags=PERF_FLAG_DISABLED|PERF_FLAG_EXCLUDE_HV|(kernel_only?PERF_FLAG_EXCLUDE_USER:0);
 a.wakeup_events=1;
 long fd=sys6(NR_PERF_EVENT_OPEN,(long)&a,0,-1,-1,0,0);
 if(fd<0){err(fd);return;}
 long map=sys6(NR_MMAP,0,PAGE+RING_SIZE,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
 if(map<0){p("mmap: ");err(map);sys6(NR_CLOSE,fd,0,0,0,0,0);return;}
 u8*base=(u8*)map;
 u64 dataoff=load64(base,1040),datasize=load64(base,1048);
 if(dataoff!=PAGE||datasize!=RING_SIZE){p("Unexpected perf ring geometry\n");goto closeit;}
 if(sys6(NR_IOCTL,fd,PERF_EVENT_IOC_RESET,0,0,0,0)<0){p("reset failed\n");goto closeit;}
 if(sys6(NR_IOCTL,fd,PERF_EVENT_IOC_ENABLE,0,0,0,0)<0){p("enable failed\n");goto closeit;}
 u64 start=ms();
 if(!start){p("clock_gettime unavailable; stopping safely\n");(void)sys6(NR_IOCTL,fd,PERF_EVENT_IOC_DISABLE,0,0,0,0);goto closeit;}
 for(int cycle=0;cycle<1000&&ms()-start<1200;cycle++){
  for(int i=0;i<5000;i++)activity+=(u64)sys6(NR_GETPID,0,0,0,0,0,0)&1;
 }
 (void)sys6(NR_IOCTL,fd,PERF_EVENT_IOC_DISABLE,0,0,0,0);
 {
  const u8*ring=base+PAGE;u64 head=load64(base,1024),tail=load64(base,1032);
  u64 samples=0,user=0,kernel=0,hyper=0,guest=0,others=0,regs64=0,regsnone=0,lost=0;
  if(head-tail>RING_SIZE){p("ring overflow; older records lost\n");tail=head-RING_SIZE;}
  for(u64 n=0;tail+8<=head&&n<30000;n++){
   u32 type=read32(ring,tail);u16 misc=read16(ring,tail+4),size=read16(ring,tail+6);
   if(size<8||tail+size>head){p("invalid record boundary\n");break;}
   if(type==PERF_RECORD_SAMPLE){
    samples++;
    switch(misc&7){case 1:kernel++;break;case 2:user++;break;case 3:hyper++;break;case 4:case 5:guest++;break;default:others++;}
    if(size>=24){u64 abi=read64(ring,tail+16);if(abi==2)regs64++;else if(abi==0)regsnone++;}
   }else if(type==PERF_RECORD_LOST)lost++;
   tail+=size;
  }
  p("samples=");num(samples);p(" user=");num(user);p(" kernel=");num(kernel);
  p(" hypervisor=");num(hyper);p(" guest=");num(guest);p(" other=");num(others);
  p(" regs_abi64=");num(regs64);p(" regs_none=");num(regsnone);
  p(" lost_records=");num(lost);p("\n");
  p("ALL IP AND REGISTER VALUES DISCARDED (not printed or stored)\n");
 }
closeit:
 sys6(NR_MUNMAP,(long)base,PAGE+RING_SIZE,0,0,0,0);
 sys6(NR_CLOSE,fd,0,0,0,0,0);
}
void _start(void){
 p("MATE50 PERF SAMPLE CLASSIFIER v1 | no root | redacted\n");
 run("mixed_user_and_kernel",0);
 run("kernel_only",1);
 p("DONE: kernel samples here do not imply a working GhostLock exploit.\n");
 sys6(NR_EXIT_GROUP,0,0,0,0,0,0);
 __builtin_unreachable();
}
