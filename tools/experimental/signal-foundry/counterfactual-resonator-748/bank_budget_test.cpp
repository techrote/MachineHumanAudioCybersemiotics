#include "bank_budget.hpp"
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <tuple>
#include <string>
using namespace mhac::counterfactual;
static unsigned checks=0;
static void require(bool ok){++checks;if(!ok){std::cerr<<"budget failure "<<checks<<'\n';std::exit(1);}}
static bool equal(BudgetPlan a,BudgetPlan b){return a.mask==b.mask&&a.cost==b.cost&&a.count==b.count&&a.energy==b.energy;}
// Independent recursive subset oracle, lexicographic signed score.
static BudgetPlan oracle(const std::array<BudgetCandidate,4>& c,unsigned budget,BudgetObjective objective){
    BudgetPlan best{};
    const auto score=[&](BudgetPlan p){return std::make_tuple(objective==BudgetObjective::energy?int(p.energy):int(p.count),objective==BudgetObjective::energy?int(p.count):int(p.energy),-int(p.cost),-int(p.mask));};
    const auto visit=[&](const auto& self,unsigned i,BudgetPlan p)->void{
        if(i==4){if(score(p)>score(best))best=p;return;}
        self(self,i+1,p);
        if(c[i].cost&&p.cost+c[i].cost<=budget){p.mask|=1u<<i;p.cost+=c[i].cost;p.energy+=c[i].energy;++p.count;self(self,i+1,p);}
    };
    visit(visit,0,{});return best;
}
static void planner(){
    for(unsigned code=0;code<625;++code)for(unsigned variant=0;variant<5;++variant){
        auto n=code;std::array<BudgetCandidate,4> c{};
        for(unsigned i=0;i<4;++i){const unsigned cost=n%5;n/=5;c[i]={cost,cost?1+(code*17+i*43+variant*101)%1024:0};}
        for(unsigned b=0;b<=16;++b)for(auto objective:{BudgetObjective::count,BudgetObjective::energy})
            require(equal(chooseBudget(c,b,objective),oracle(c,b,objective)));
    }
    const std::array<BudgetCandidate,4> c{{{2,10},{2,11},{4,300},{0,0}}};
    require(chooseBudget(c,4,BudgetObjective::count).mask==3);
    require(chooseBudget(c,4,BudgetObjective::energy).mask==4);
    require(chooseBudget(c,17,BudgetObjective::energy).mask==0);
}
static void excite(HarmonicBank& bank,double rate){
    require(bank.prepare(rate));auto cfg=bank.config();cfg.wet=1000;
    for(auto& b:cfg.bands){b.excite=true;b.peakMix=1000;b.gain=800;}
    require(bank.set(cfg));bank.reset();
    for(unsigned i=0;i<unsigned(rate/4);++i)bank.process(0.85,-0.55);
    for(auto& b:cfg.bands)b.excite=false;
    require(bank.set(cfg));
    for(unsigned i=0;i<unsigned(rate/10);++i)bank.process(0,0);
}
static void engine(){
    for(double rate:{44100.,48000.,96000.})for(unsigned budget=0;budget<=16;++budget)
        for(auto objective:{BudgetObjective::count,BudgetObjective::energy}){
            HarmonicBank bank;excite(bank,rate);auto reference=bank;
            std::array<BudgetCandidate,4> c{};
            for(unsigned i=0;i<4;++i){c[i]=budgetCandidate(bank,i);require(c[i].cost>0);}
            const auto plan=beginBudgetedEscape(bank,budget,objective);
            require(equal(plan,oracle(c,budget,objective)));require(plan.cost<=budget);
            for(unsigned i=0;i<4;++i)if(plan.mask&(1u<<i))require(reference.beginOptimalEscape(i));
            for(unsigned j=0;j<unsigned(rate/4);++j){
                const auto s=bank.process(0,0),r=reference.process(0,0);
                require(s.left==r.left&&s.right==r.right&&std::abs(s.left)<=1&&std::abs(s.right)<=1);
            }
            unsigned spent=0;
            for(unsigned i=0;i<4;++i){const auto used=bank.interventions(i);spent+=unsigned(used);
                if(plan.mask&(1u<<i)){require(used==c[i].cost);require(magnitude(bank.lattice(i,0))==0&&magnitude(bank.lattice(i,1))==0);}
                else require(used==0&&(magnitude(bank.lattice(i,0))||magnitude(bank.lattice(i,1))));
            }
            require(spent==plan.cost);
        }
    HarmonicBank bank;excite(bank,48000);auto cfg=bank.config();cfg.bands[0].excite=true;cfg.bands[1].erase=true;require(bank.set(cfg));
    require(bank.pulse(2));require(bank.beginOptimalEscape(3));
    require(beginBudgetedEscape(bank,16,BudgetObjective::count).mask==0);
    require(bank.optimalEscapeActive(3));
    excite(bank,48000);require(beginBudgetedEscape(bank,16,BudgetObjective::count,5).mask==5);
    require(beginBudgetedEscape(bank,16,BudgetObjective::count,16).mask==0);
}
static void word(std::ofstream& f,unsigned value,unsigned size){for(unsigned i=0;i<size;++i)f.put(char((value>>(8*i))&255u));}
static void render(const std::string& prefix,unsigned budget){
    constexpr unsigned rate=48000,frames=rate*2;HarmonicBank bank;excite(bank,rate);
    const auto plan=beginBudgetedEscape(bank,budget,BudgetObjective::energy);
    std::ofstream f(prefix+std::to_string(budget)+".wav",std::ios::binary);
    f.write("RIFF",4);word(f,36+frames*4,4);f.write("WAVEfmt ",8);word(f,16,4);word(f,1,2);word(f,2,2);word(f,rate,4);word(f,rate*4,4);word(f,4,2);word(f,16,2);f.write("data",4);word(f,frames*4,4);
    double peak=0;
    for(unsigned i=0;i<frames;++i){const auto s=bank.process(0,0);const double fade=std::min({1.,double(i)/480.,double(frames-1-i)/2400.});
        for(double x:{s.left,s.right}){const double y=x*fade*0.5;peak=std::max(peak,std::abs(y));word(f,unsigned(int(std::round(y*32767))),2);}}
    require(bool(f));std::cout<<"budget="<<budget<<" mask="<<plan.mask<<" spent="<<plan.cost<<" energy="<<plan.energy<<" peak="<<peak<<'\n';
}
int main(int argc,char** argv){planner();engine();if(argc==2)for(unsigned b:{0u,4u,8u,16u})render(argv[1],b);std::cout<<"BANK_BUDGET_PASS checks="<<checks<<'\n';}
