#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#define TF_LOBBY_MAX_AI_SLOTS 16
#define TF_LOBBY_MAX_CANDIDATES 24
struct { int diff[TF_LOBBY_MAX_AI_SLOTS+1]; } TF_LobbyCands[TF_LOBBY_MAX_CANDIDATES];

/* ---- verbatim copy of the DLL resolver logic ---- */
static bool TF_Cand_Same_Vec(int a,int b,unsigned roster){
  for(int n=1;n<=TF_LOBBY_MAX_AI_SLOTS;n++)
    if((roster&(1u<<n))&&TF_LobbyCands[a].diff[n]!=TF_LobbyCands[b].diff[n]) return false;
  return true;
}
static char TF_Resolve_Lobby_Ambiguity(const int*refeq,const int*refwin,int ncand,unsigned roster,int*out){
  int rep=-1; bool conflict=false;
  for(int c=0;c<ncand;c++) if(refeq[c]>0){ if(rep<0)rep=c; else if(!TF_Cand_Same_Vec(rep,c,roster))conflict=true; }
  if(rep>=0&&!conflict){ for(int n=1;n<=TF_LOBBY_MAX_AI_SLOTS;n++)out[n]=TF_LobbyCands[rep].diff[n]; return 'R'; }
  int minrw=0x7fffffff; for(int c=0;c<ncand;c++) if(refwin[c]<minrw)minrw=refwin[c];
  int thresh=minrw*4+2; int frep=-1; bool fconf=false;
  for(int c=0;c<ncand;c++) if(refwin[c]<=thresh){ if(frep<0)frep=c; else if(!TF_Cand_Same_Vec(frep,c,roster))fconf=true; }
  if(frep>=0&&!fconf){ for(int n=1;n<=TF_LOBBY_MAX_AI_SLOTS;n++)out[n]=TF_LobbyCands[frep].diff[n]; return 'F'; }
  int bestc=-1,bestn=0;
  for(int c=0;c<ncand;c++){ int cnt=0; for(int d=0;d<ncand;d++) if(TF_Cand_Same_Vec(c,d,roster))cnt++; if(cnt>bestn){bestn=cnt;bestc=c;} }
  if(bestc>=0){ bool tie=false;
    for(int c=0;c<ncand&&!tie;c++){ if(TF_Cand_Same_Vec(bestc,c,roster))continue; int cnt=0;
      for(int d=0;d<ncand;d++) if(TF_Cand_Same_Vec(c,d,roster))cnt++; if(cnt>=bestn)tie=true; }
    if(!tie){ for(int n=1;n<=TF_LOBBY_MAX_AI_SLOTS;n++)out[n]=TF_LobbyCands[bestc].diff[n]; return 'M'; } }
  return 'U';
}
/* ---- test driver: parse batch results, run resolver per ambiguous cycle ---- */
int main(int argc,char**argv){
  int pass=0,wrong=0,undec=0,total=0; int R=0,F=0,M=0;
  for(int f=1;f<argc;f++){
    FILE*fp=fopen(argv[f],"r"); if(!fp)continue; char line[512];
    char gt[16]={0}; int nc=0; int refeq[TF_LOBBY_MAX_CANDIDATES],refwin[TF_LOBBY_MAX_CANDIDATES];
    char cdiff[TF_LOBBY_MAX_CANDIDATES][16]; unsigned roster=6; int inblock=0;
    void(*flush)()=0; // placeholder
    #define RUN() do{ if(nc>0){ total++; \
      for(int c=0;c<nc;c++){ /* map cdiff string to slots (2-AI: slots 1,2) */ \
        TF_LobbyCands[c].diff[1]=cdiff[c][0]-'0'; TF_LobbyCands[c].diff[2]=cdiff[c][1]-'0'; } \
      int out[TF_LOBBY_MAX_AI_SLOTS+1]={0}; \
      char br=TF_Resolve_Lobby_Ambiguity(refeq,refwin,nc,roster,out); \
      if(br=='R')R++; else if(br=='F')F++; else if(br=='M')M++; \
      char dec[16]; if(br=='U'){undec++; strcpy(dec,"U");} \
      else{ snprintf(dec,sizeof(dec),"%d%d",out[1],out[2]); \
        if(strcmp(dec,gt)==0)pass++; else {wrong++; printf("WRONG %s: got %s exp %s (branch %c)\n",argv[f],dec,gt,br);} } \
      } nc=0; }while(0)
    while(fgets(line,sizeof(line),fp)){
      char*p;
      if((p=strstr(line,"gt="))){ RUN(); sscanf(p,"gt=%15s",gt); inblock=0; continue; }
      if(strstr(line,"LOBBYCAND")){ if(strstr(line,"site=0")) {RUN(); inblock=0;} else inblock=1; continue; }
      if(inblock && (p=strstr(line,"diff="))){ int eq=0,rw=0; char d[16];
        sscanf(p,"diff=%15s refs=%d refwin=%d",d,&eq,&rw);
        if(nc<TF_LOBBY_MAX_CANDIDATES){ strncpy(cdiff[nc],d,15); refeq[nc]=eq; refwin[nc]=rw; nc++; } }
    }
    RUN(); fclose(fp);
  }
  printf("\nCOMPILED-C RESOLVER: total=%d PASS=%d WRONG=%d UNDECIDED=%d | R=%d F=%d M=%d\n",total,pass,wrong,undec,R,F,M);
  return wrong?1:0;
}
