#include <algorithm>
#include <iostream>
#include <vector>
#include <iterator>
#include <math.h>  
#include <deque> 
#include <set>


using namespace std;

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

//local-history predicor parameters (nbit ang global-history are special cases of it)
#define n_bits 2 
#define l_bits 1 /* last l_bits of PC used */
#define p_bits 1 /* length of bhr */

//memory parameters 
#define block_size 16 /*(in bytes)*/
#define set_num 1 /*number os sets in cache*/
#define bl_num 2 /*number os blocks in cache*/
#define num_len 8 /* length of numbers stored in arrays (in bytes) */
#define num_of_arrays 2 /*number of arrays used in the given code*/
#define num_of_elems 4 /*length of these arrays (total number of elements accessed while executing the given code)*/

#define initial_address 0x00448408  /*PC of the first command in the given code*/
#define num_of_cmds 15 /*number of commands in the given code*/


#define paris 2 /*number of parallel issues/commits supported */
#define cdb 1 /*number of cdbs*/

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

/*length of commands in bytes*/
#define cmd_len 4 

//fixed
#define com_num 11 
#define rs_num 6
#define fu_num 4




struct block
{
    bool dirty;
    int tag, lru;
};

int t, tot_cost;
block Cache[bl_num];

void init()
{
    for (int j = 0; j < bl_num; j++)
    {
        Cache[j].tag = -1;
        Cache[j].dirty = false;
    }
}

bool L(int bl)
{
    bool hit=false;
    t++;
    int tmp_cost = 1;
    int tag = bl / set_num;
    int idx = bl % set_num;
    int ass = bl_num / set_num;
    int pos = -1;
    bool wb = false;
    for (int i = idx * ass; i < (idx + 1) * ass; i++)
    {
        if (Cache[i].tag == tag)
        {
            hit=true;
            pos = i;
            break;
        }
    }
    if (pos == -1)
    {
        int mn_idx = idx * ass, mn_lru = Cache[mn_idx].lru;
        for (int i = idx * ass; i < (idx + 1) * ass; i++)
        {
            if (Cache[i].tag == -1)
            {
                mn_idx = i;
                break;
            }
            if (Cache[i].lru < mn_lru)
            {
                mn_idx = i;
                mn_lru = Cache[i].lru;
            }
        }
        pos = mn_idx;
    }
    Cache[pos].tag = tag;
    Cache[pos].lru = t;
    Cache[pos].dirty = false;
    return hit;
}

bool S(int bl)
{
    t++;
    bool hit=false;
    int tmp_cost = 1;
    int tag = bl / set_num;
    int idx = bl % set_num;
    int ass = bl_num / set_num;
    int pos = -1;
    bool wb = false;
    for (int i = idx * ass; i < (idx + 1) * ass; i++)
    {
        if (Cache[i].tag == tag)
        {
            hit=true;
            pos = i;
            break;
        }
    }
    if (pos == -1)
    {
        int mn_idx = idx * ass, mn_lru = Cache[mn_idx].lru;
        for (int i = idx * ass; i < (idx + 1) * ass; i++)
        {
            if (Cache[i].tag == -1)
            {
                mn_idx = i;
                break;
            }
            if (Cache[i].lru < mn_lru)
            {
                mn_idx = i;
                mn_lru = Cache[i].lru;
            }
        }
        
        pos = mn_idx;
    }
    Cache[pos].tag = tag;
    Cache[pos].lru = t;
    Cache[pos].dirty = true;
    return hit;
}


bool HCHECK(int bl)
{
    bool hit=false;
    int tag = bl / set_num;
    int idx = bl % set_num;
    int ass = bl_num / set_num;
    int pos = -1;
    bool wb = false;
    for (int i = idx * ass; i < (idx + 1) * ass; i++)
    {
        if (Cache[i].tag == tag)
        {
            hit=true;
            pos = i;
            break;
        }
    }
    return hit;
}



//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

//BHR And PHT Initialization
int BHR=1;
vector<vector<int> >PHT {  
        {0,1},  
        {3,2}
    };
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

bool predict(int address){
    std::cout << "TEST Address: " << address << "l buts: " << l_bits << endl;
    return PHT[address%(int)round(pow(2, l_bits))][BHR]>=(int)round(pow(2, n_bits-1));
}

void update(int address, bool outcome){
    PHT[address%(int)round(pow(2, l_bits))][BHR]=max(min(PHT[address%(int)round(pow(2, l_bits))][BHR]-1+2*outcome,(int)round(pow(2, n_bits))-1),0);
    BHR=(2*BHR+outcome)%(int)round(pow(2, p_bits));
}

struct command {
        int op,IS,EXs, EXf ,WR,CMT, addr;
        command(){};
        command(int op1, int IS1,int EXs1,int EXf1,int WR1,int CMT1, int addr1){
           op=op1;
           IS=IS1;
           EXs=EXs1;
           EXf=EXf1;
           WR=WR1;
           CMT=CMT1; 
           addr=addr1;
           
        }
};

int* R=(int*) malloc(16*sizeof(int));
int* Rcp=(int*) malloc(16*sizeof(int));
int* F=(int*) malloc(16*sizeof(int));
int* Fcp=(int*) malloc(16*sizeof(int));
int** A = (int **)malloc(sizeof(int *) * num_of_arrays);
int** Acp= new int *[num_of_elems];


int RS[rs_num]={0,0,0,0,0,0};
int FU[fu_num]={0,0,0,0};
int ROB=0;

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

//Supposing there are 6 groups of reservation stations. Each one for a different type of command (ld,  sd,  adi, mli, add and mld command types).
//Define how many RSs each group of RSs contains .
////////////           ld  sd  adi mli add mld
int RScapacity[rs_num]={2,  2,  3,  1,  3,  2};

//Supposing there are 4 groups of functional units. Each one for a different type of command (mem, int, add and mld command types).
//Define how many FUs each group of FUs contains and how many cycles are required for each command type. Also, define whether each group of FUs is pipelined or not.
////////////           mem int add mld
int FUcapacity[fu_num]={1,  3,  1,  1};
int FUcycles[fu_num]=  {1,  2,  3,  5};
bool FUpipelined[fu_num]= {true, true, false, false};

int miss_penalty=3; /*cache miss penalty in cycles*/
int rob_capacity=9;

//A set of 11 operations is supported {ld,  sd,  adi, sbi, ani, mli, add, mld, sbd, bnz, bne}
//Map each one of them to its corresponding FU and RS group.
////////////////       ld  sd  adi sbi ani mli add mld sbd bnz bne
int rsmap[com_num]=    {0,  1,  2,  2,  2,  3,  4,  5,  4,  2,  2}; /* 0:ld, 1:sd, 2:adi, 3:mli, 4:add, 5:mld */
int fumap[com_num]=    {0,  0,  1,  1,  1,  1,  2,  3,  2,  1,  1}; /* 0:mem, 1:int, 2:add, 3:mld */

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

//For each operation define what kind of result it has. '0' means no result stored in register, 'f' means result stored in some F-register, 'r' means result stored in some R-register
char res_reg[com_num]={'f','0','r','r','r','r','f','f','f','0','0'};


int main()
{
    init();
    for(int pipis = 0; pipis < num_of_arrays; pipis++){
        A[pipis] = (int (*))malloc(sizeof(int) * num_of_elems);
    }
    
  
    init();
    
    //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    //Here we give the code we want to simulate in the form of a 2-d array. 
    //Each row corresponds to a particular command and each collumn to a command parameter.
    
    // The first collumn always represents the operation id.
    // operation:     LD  SD  ADDI SUBI ANDI MULI ADDD MULD SUBD BNEZ BNE
    // operation id:  0   1    2    3    4    5    6    7    8    9   10
    
    // The next 3 collumns have a different meaning for each operation.
    // Let {op_id, a, b, c} be one row of the commands array.
    // For load operations(op_id=0) this corresponds to LD Fa, b(Rc)
    // For store operations(op_id=1) this corresponds to SD Fa, b(Rc)
    // For ADDI operations(op_id=2) this corresponds to ADDI Ra, Rb, c
    // For SUBI operations(op_id=3) this corresponds to SUBI Ra, Rb, c
    // For ANDI operations(op_id=4) this corresponds to ANDI Ra, Rb, c
    // For MULI operations(op_id=5) this corresponds to MULI Ra, Rb, c
    // For ADDD operations(op_id=6) this corresponds to ADDD Fa, Fb, Fc
    // For MULD operations(op_id=7) this corresponds to MULD Fa, Fb, Fc
    // For SUBD operations(op_id=8) this corresponds to SUBD Fa, Fb, Fc
    // For BNEZ operations(op_id=9) this corresponds to BNEZ Ra, b     , where b is the index of the destination command in the commands array
    // For BNE operations(op_id=10) this corresponds to BNE Ra, Rb, c  , where c is the index of the destination command in the commands array
    
    //LD  SD  ADDI SUBI ANDI MULI ADDD MULD SUBD BNEZ BNE
    //0   1    2    3    4    5    6    7    8    9   10
    
    
    int commandstmp[num_of_cmds][4]={
       {0,0,0,1},  
       {6,4,4,0},
       {0,1,0,2},  
       {7,4,4,1},
       {4,9,8,2}, 
       
       {9,9,9,-1},  
       {0,2,16,2},
       {7,2,2,5},  
       {6,4,4,2},
       {0,5,8,1},
       
       {6,4,4,5},
       {2,1,1,8},  
       {3,8,8,1},
       {9,8,0,-1},
       {1,4,8,2}
       
    };
    
    //Initialize the registers
    R[8]=1;
    // R[3]=1;
    
    //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    cout << "Initial Command Address: " << initial_address<< endl;
    int commands[num_of_cmds][5];
    for(int i=0; i<num_of_cmds; i++){
        for(int j=0; j<4; j++){
            commands[i][j]=commandstmp[i][j];
        }
        commands[i][4]=(initial_address+cmd_len*i)/cmd_len;
        cout << "Command Address: " << commands[i][4] << endl;
    }
    
    vector<struct command> cmdlist;
    vector<struct command> complete_cmdlist;
    vector<string> comments;

    deque <int*> qrcp={}; 
    deque <int*> qfcp={};
    deque <int**> qacp={};
    deque <int> qbr_address={};
    deque <bool> qoutcome={};
    deque <int> qspec_end={};
    
    int tm=0;
    int cur_cmd=0;
    set<string> comment;
    int next_cmd=-1;
    int spec_end=-1;
    bool br_outcome;
    int br_address;
    vector<struct command>::iterator it;

    
    while(cur_cmd<num_of_cmds||!(qspec_end.empty())){ 
        tm++; /*time*/
        cout<<"cycle "<<tm<<'\n';
        if(!(cmdlist.empty())){
            for(it = cmdlist.end()-1; ; it--){
                if(it->WR+1==tm)RS[rsmap[commands[it->op][0]]]--;
                if(it->CMT+1==tm)ROB--;
                if(it==cmdlist.begin())break;
            }
        }
        
        for(int k=0; k<paris; k++){ /*parallel issue */
            
            if(paris>1)cout<<"  k ="<<k<<"\n";
            bool isb=true;
            int is_time,ex_time,wr_time,cmt_time;
     
            cout<<"     current op = "<<cur_cmd<<"\n";
            int ctype=commands[cur_cmd][0];
            if(RS[rsmap[ctype]]==RScapacity[rsmap[ctype]]){
                cout<<"      full rs\n"; isb=false;
                comment.insert("full rs");
                
            }
            else if(ROB==rob_capacity){
                cout<<"      full rob\n"; isb=false;
                comment.insert("full rob");
            }
            else{
                ROB++;
                RS[rsmap[ctype]]++;
            }
            is_time=tm;
            
            for(int i=tm+1; ; i++){
                bool ok=true;
                int a=i;
                int pen = 0;
                if((ctype==0||ctype==1)&&(!HCHECK((R[commands[cur_cmd][3]]+commands[cur_cmd][2])/num_len*num_len/block_size+10*commands[cur_cmd][3]*bl_num))){
                    pen=miss_penalty;
                }
                
                int b=a+FUcycles[fumap[ctype]]+pen-1;
                if(i==1000)break; 

                for(int j=a; j<=b; j++){
                    
                    if((FUpipelined[fumap[ctype]]==false)&&(!(cmdlist.empty()))){
                        int ex_cnt=0;
                        for(it = cmdlist.end()-1; ; it--){
                            int A=it->EXs;
                            int B=it->EXf; 
                            if((fumap[commands[it->op][0]]==fumap[ctype])&&(A<=j&&j<=B))ex_cnt++;
                            if(it==cmdlist.begin())break;
                        }
                        if(ex_cnt==FUcapacity[fumap[ctype]]){
                            comment.insert("FU busy");
                            ok=false;
                            break;
                        }
                    }
                    else if(!(cmdlist.empty())){
                        int ex_cnt=0;
                        for(it = cmdlist.end()-1; ; it--){
                            int A=it->EXs;
                            int B=it->EXf; 
                            if((fumap[commands[it->op][0]]==fumap[ctype])&&(A==j))ex_cnt++;
                            if(it==cmdlist.begin())break;
                        }
                        if(ex_cnt==FUcapacity[fumap[ctype]]){
                            comment.insert("FU busy");
                            ok=false;
                            break;
                        }
                        
                    }
                }
                
                // LD  SD  ADDI SUBI ANDI MULI ADDD MULD SUBD BNEZ BNE
                // 0   1    2    3    4    5    6    7    8    9   10
                if(!(cmdlist.empty())){
                    if(ctype==0||ctype==1){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='r')&&(commands[it->op][1]==commands[cur_cmd][3])&&(A>i)){
                                ok=false;
                                comment.insert("raw R"+to_string(commands[cur_cmd][3]));
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    else if(ctype==2||ctype==3||ctype==4||ctype==5){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='r')&&(commands[it->op][1]==commands[cur_cmd][2])&&(A>i)){
                                comment.insert("raw R"+to_string(commands[cur_cmd][2]));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    else if(ctype==6||ctype==7||ctype==8){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='f')&&((commands[it->op][1]==commands[cur_cmd][2])||(commands[it->op][1]==commands[cur_cmd][3]))&&(A>i)){
                                comment.insert("raw F"+to_string(commands[it->op][1]));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    else if(ctype==9){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='r')&&(commands[it->op][1]==commands[cur_cmd][1])&&(A>i)){
                                comment.insert("raw R"+to_string(commands[it->op][1]));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    else if(ctype==10){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='r')&&(commands[it->op][1]==commands[cur_cmd][1])&&(A>i)){
                                comment.insert("raw R"+to_string(commands[it->op][1]));
                                ok=false;
                                break;
                            }
                            if((res_reg[commands[it->op][0]]=='r')&&(commands[it->op][1]==commands[cur_cmd][2])&&(A>i)){
                                comment.insert("raw R"+to_string(commands[it->op][1]));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    
                    if(ctype==0){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->CMT+1;
                            if((commands[it->op][0]==1)&&(it->addr==R[commands[cur_cmd][3]]+commands[cur_cmd][2])&&(A>i)){
                                comment.insert("raw at address"+to_string(it->addr));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    
                    
                    if(ctype==1){
                       for(it = cmdlist.end()-1; ; it--){
                            int A=it->WR+1;
                            if((res_reg[commands[it->op][0]]=='f')&&(commands[it->op][1]==commands[cur_cmd][1])&&(A>i)){
                                comment.insert("raw F"+to_string(commands[it->op][1]));
                                ok=false;
                                break;
                            }
                            if(it==cmdlist.begin())break;
                        } 
                    }
                    if(ok){
                        ex_time=i;
                        break;
                    }
                }
                else ex_time=is_time+1;
               
            }
            
            int pen = 0;
            if((ctype==0||ctype==1)&&(!(HCHECK((R[commands[cur_cmd][3]]+commands[cur_cmd][2])/block_size+10*commands[cur_cmd][3]*bl_num))))pen=miss_penalty;
            if(!(cmdlist.empty())){

                for(int i=ex_time+FUcycles[fumap[ctype]]+pen; ; i++){  /////////////+penalty
                    
                    bool ok=true;
                    int wr_cnt=0;
                    for(it = cmdlist.end()-1; ; it--){
                        if(it->WR==i&&commands[it->op][0]!=9&&commands[it->op][0]!=10)wr_cnt++;
                        if(it==cmdlist.begin())break;
                    }
                    if(wr_cnt==cdb){
                        ok=false;   ////branch oxi !!!
                        if(isb&&commands[cur_cmd][0]!=9&&commands[cur_cmd][0]!=10){
                            cout<<"      cdb!\n";
                            comment.insert("cdb");
                        }
                    }
                    if(ok){
                        wr_time=i;
                        break;
                    }
                    
                }
            }
            else wr_time=ex_time+FUcycles[fumap[ctype]]+pen;
            if(commands[cur_cmd][0]==9||commands[cur_cmd][0]==10)wr_time=ex_time+FUcycles[fumap[ctype]]+pen;
            if(!(cmdlist.empty())){
                int cmt_cnt=0;
                int cmt_last=cmdlist[cmdlist.size()-1].CMT;
                bool cmt_par_ok=true;
                
                for(it = cmdlist.end()-1; ; it--){
                        if(it->CMT==cmt_last)cmt_cnt++;
                        else break;
                        if(cmt_cnt==paris){
                            cmt_par_ok=false;
                            break;
                        }
                        
                    }
                if(cmt_par_ok)cmt_time=max(cmt_last,wr_time+1);
                else cmt_time=max(cmt_last+1,wr_time+1);
            }
            else  cmt_time=wr_time+1;

            
            
            if((commands[cur_cmd][0]==9||commands[cur_cmd][0]==10)&&isb){
                bool outcm;
                string cmmnt="branch prediction: ";
                if(commands[cur_cmd][0]==9)outcm = (R[commands[cur_cmd][1]]!=0);
                else if(commands[cur_cmd][0]==10)outcm = (R[commands[cur_cmd][1]]!=R[commands[cur_cmd][2]]);

                if(outcm) cmmnt+="outcome = T, ";
                else cmmnt+="outcome = NT, ";

                
                if(predict(commands[cur_cmd][4])==true){
                    cmmnt+="prediction = T";
                    if(commands[cur_cmd][0]==9)next_cmd=commands[cur_cmd][2];
                    if(commands[cur_cmd][0]==10)next_cmd=commands[cur_cmd][3];

                }
                else{
                    cmmnt+="prediction = NT";
                    next_cmd=(cur_cmd+1);
                }
                for (int i=0; i<16; i++){
                    Rcp[i]=R[i];
                    Fcp[i]=F[i];
                }
                for(int i = 0; i <num_of_arrays; i++) Acp[i] = new int[num_of_elems];
                for (int i=0; i<num_of_arrays; i++)for(int j=0; j<num_of_elems; j++){
                    Acp[i][j]=A[i][j];
                }
                comment.insert(cmmnt);
                qrcp.push_back(Rcp);
                qfcp.push_back(Fcp); 
                qacp.push_back(Acp); 
                qbr_address.push_back(cur_cmd);
                qoutcome.push_back(outcm);
                qspec_end.push_back(wr_time);
                
            }
            else next_cmd=cur_cmd+1;
            
            
            if(isb){
                
                // LD  SD  ADDI SUBI ANDI MULI ADDD MULD SUBD BNEZ BNE
                // 0   1    2    3    4    5    6    7    8    9   10
                int type=commands[cur_cmd][0];
                int first=commands[cur_cmd][1];
                int second=commands[cur_cmd][2];
                int third=commands[cur_cmd][3];
                
                int addr=-1;
                int penalty=0;
                if(type==0){
                    int indx=(R[third]+second)/num_len;
                    //F[first]=A[third][indx]; 
                    if(L(indx*num_len/block_size+10*third*bl_num)==false){
                        cout<<"     cache miss\n";
                        comment.insert("cache miss");
                        penalty=miss_penalty;
                    }
                    else{
                        cout<<"     cache hit\n";
                        comment.insert("cache hit");
                    }
                    addr=indx+10*third*bl_num;
                }
                if(type==1){
                    int indx=(R[third]+second)/num_len;
                    //A[third][indx]=F[first];
                    if(S(indx*num_len/block_size+10*third*bl_num)==false){
                        cout<<"     cache miss\n";
                        comment.insert("cache miss");
                        penalty=miss_penalty;
                    }
                    else{
                        cout<<"     cache hit\n";
                        comment.insert("cache hit");
                    }
                    addr=indx+10*third*bl_num;
                }
                else if(type==2){
                    R[first]=R[second]+third;
                }
                else if(type==3){
                    R[first]=R[second]-third;
                }
                else if(type==4){
                    R[first]=R[second]&third;
                }
                else if(type==5){
                    R[first]=R[second]*third;
                }
                else if(type==6){
                    F[first]=F[second]+F[third];
                }
                else if(type==7){
                    F[first]=F[second]*F[third];
                }
                else if(type==8){
                    F[first]=F[second]-F[third];
                }
                else if(type==9){
                    
                }
                
                int ex_end=ex_time+FUcycles[fumap[type]]+penalty-1;
                cmdlist.push_back(command(cur_cmd,is_time,ex_time,ex_end,wr_time,cmt_time, addr));
                complete_cmdlist.push_back(command(cur_cmd,is_time,ex_time,ex_end,wr_time,cmt_time, addr));
                string comm;
                set<string>::iterator itc;
                for (itc = comment.begin(); itc != comment.end(); ++itc) {
                    comm += *itc; 
                    comm += ", "; 
                    
                }
                comm = comm.substr(0, comm.size()-2);
                comm += '\n';
                
                comments.push_back(comm);
                cur_cmd=next_cmd;
                comment.clear();
                cout<<"     command issued\n";
                
            }
            
            deque<int>::iterator itt = qspec_end.begin();
            while (itt != qspec_end.end()){
                if(tm==*itt)break;
                itt++;
            }
            
            if(itt!=qspec_end.end()){

                //an tm == me kapoio stoixeio tou qspec_end, tote :
                // an problepse swsta apla to bgazeis apo thn oura
                //an provlepse lathos petas auto kai ta epomena
                
                //////// mporei na teleiwse ki allo branch
                //////// to spec end se stoiva kai bgazeis kathe fora to front

                auto vi = qrcp.begin();
                advance(vi, distance(qspec_end.begin(),itt));
                int* rcp=*(vi);
                vi = qfcp.begin();
                advance(vi, distance(qspec_end.begin(),itt));
                int* fcp=*(vi); 
                auto vi1 = qacp.begin();
                advance(vi1, distance(qspec_end.begin(),itt));
                int** acp=*(vi1); 
                auto vi2 = qoutcome.begin();
                advance(vi2, distance(qspec_end.begin(),itt));
                bool outcome=*(vi2);
                auto vi3 = qbr_address.begin();
                advance(vi3, distance(qspec_end.begin(),itt));
                int br_address=*(vi3); 
                

                bool mispred=false;
                if(outcome!=predict(commands[br_address][4])){
                    mispred=true;
                    cout<<"     missprediction\n";
                    for (int i=0; i<16; i++){
                        R[i]=rcp[i];
                        F[i]=fcp[i];
                    }
                    for (int i=0; i<num_of_arrays; i++)for(int j=0; j<num_of_elems; j++){
                        A[i][j]=Acp[i][j];
                    }
                    
                    vi = qrcp.begin();
                    advance(vi, distance(qspec_end.begin(),itt));
                    qrcp.erase(vi,qrcp.end()); 
                    vi = qfcp.begin();
                    advance(vi, distance(qspec_end.begin(),itt));
                    qfcp.erase(vi,qfcp.end()); 
                    vi1 = qacp.begin();
                    advance(vi1, distance(qspec_end.begin(),itt));
                    qacp.erase(vi1,qacp.end()); 
                    vi2 = qoutcome.begin();
                    advance(vi2, distance(qspec_end.begin(),itt));
                    qoutcome.erase(vi2,qoutcome.end());
                    vi3 = qbr_address.begin();
                    advance(vi3, distance(qspec_end.begin(),itt));
                    qbr_address.erase(vi3,qbr_address.end()); 
                    qspec_end.erase(itt,qspec_end.end());

                    
                    
                    for(it = complete_cmdlist.end()-1; ; it--){
                        if((it->op!=br_address)||(it->WR!=tm)){
                            if(it->CMT>=tm)it->CMT=-1;
                            if(it->WR>=tm)it->WR=-1;
                            if(it->EXs>tm){
                                it->EXs=-1;
                                it->EXf=-1;
                            }
                            else{
                                if(it->EXf>tm){
                                    it->EXf=tm;
                                }
                            }
                            
                        }
                        else break;
                        if(it==cmdlist.begin())break;
                    }
                    
                    
                    for(it = cmdlist.end()-1; ; it--){
                        if((it->op!=br_address)||(it->WR!=tm)){
                            if((it->CMT+1)>tm)ROB--;
                            if((it->WR+1)>tm)RS[rsmap[commands[it->op][0]]]--;  
                            cmdlist.erase(it);
                            cout<<"     deleting operation";
                            cout<<" number " << it->op << "\n" ;
                        }
                        else break;
                        //meiwneis ROB, RS, FU!! 
                        if(it==cmdlist.begin())break;
                    }
                    //isws akurwnontai prgmata sthn cache
                    
                   
                }
                
                else{
                    cout<<"     correct prediction\n";
                    vi = qrcp.begin();
                    advance(vi, distance(qspec_end.begin(),itt));
                    qrcp.erase(vi); 
                    vi = qfcp.begin();
                    advance(vi, distance(qspec_end.begin(),itt));
                    qfcp.erase(vi);
                    vi1 = qacp.begin();
                    advance(vi1, distance(qspec_end.begin(),itt));
                    qacp.erase(vi1); 
                    vi2 = qoutcome.begin();
                    advance(vi2, distance(qspec_end.begin(),itt));
                    qoutcome.erase(vi2,qoutcome.end());
                    vi3 = qbr_address.begin();
                    advance(vi3, distance(qspec_end.begin(),itt));
                    qbr_address.erase(vi3); 
                    qspec_end.erase(itt);
                        
                }
               
                if((outcome==predict(commands[br_address][4]))&&isb){
                    next_cmd=cur_cmd+1;
                }
                else if((outcome==predict(commands[br_address][4]))&&!isb){
                    next_cmd=cur_cmd;
                }
                else if(outcome&&!predict(commands[br_address][4])){
                    if(commands[br_address][0]==9)next_cmd=commands[br_address][2];
                    if(commands[br_address][0]==10)next_cmd=commands[br_address][3];

                }
                else if(!outcome&&predict(commands[br_address][4])){
                    next_cmd=br_address+1;
                }

                update(commands[br_address][4],outcome);

                cur_cmd=next_cmd;
                comment.clear();
                
                if(mispred){
                    break; /*break from parallel issue for the current time*/
                }
                
            }
            

            if(cur_cmd==num_of_cmds)break;
        }

        if(cur_cmd==num_of_cmds)break;
        
        
    }
    cout<<"list of executed operations:\n"; 
    cout<<" OP,IS, EX, WR,CMT, COMMENTS\n";
    for (int ip = 0; ip < complete_cmdlist.size(); ip++) {
	    cout<<" "<< complete_cmdlist.at(ip).op <<", "<< complete_cmdlist.at(ip).IS <<", ";
	    cout<< complete_cmdlist.at(ip).EXs <<"-"<< complete_cmdlist.at(ip).EXf <<", "<< complete_cmdlist.at(ip).WR  <<", "<< complete_cmdlist.at(ip).CMT<<"  "<<comments.at(ip);
	}
    return(0);
}
