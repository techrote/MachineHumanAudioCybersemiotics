#pragma once
// Included by the native and actual SDK replay executables after check().
template<class T,class Engine> static void budgetReplay(Engine& host,double rate,unsigned block,bool energy,bool mono){
    MemoryConfig c{};c.wet=1000;
    for(auto& b:c.bands){b.peakMix=1000;b.gain=800;}
    HarmonicBank ref;
    check(ref.set(c)&&ref.prepare(rate)&&host.request(c)&&host.prepare(rate));
    const unsigned gate=unsigned(rate/4)+1,held=gate+unsigned(rate/8),rearm=held+unsigned(rate/8),end=rearm+unsigned(rate/4);
    std::array<T,257> l{},r{},ol{},orr{};
    bool heard=false;
    for(unsigned start=0;start<end;){
        const unsigned n=std::min(block,end-start);bh::EventBatch batch;batch.clear(n);
        const auto point=[&](unsigned t,double value){if(t>=start&&t<start+n)check(batch.point(t-start,value));};
        // Command queue precedes config queues: same-offset settings must win.
        check(batch.queue(bh::AdmitBudget));point(gate,1);point(held,1);point(rearm,0);point(rearm+1,1);
        check(batch.queue(bh::Budget));point(gate,.25);point(held,1);
        check(batch.queue(bh::Objective));point(gate,energy?1.:0.);
        for(unsigned b=0;b<4;++b){check(batch.queue(bh::FirstBand+b*bh::Stride+bh::Excite));point(gate,0);}
        check(batch.finish());
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;l[i]=t<gate?T(.85):T(0);r[i]=mono?T(0):t<gate?T(-.55):T(0);}
        check(host.processOptional(l.data(),mono?nullptr:r.data(),ol.data(),mono?nullptr:orr.data(),n,batch.data(),batch.size()));
        for(unsigned i=0;i<n;++i){const unsigned t=start+i;
            if(t==gate){for(auto& b:c.bands)b.excite=false;c.budget=4;c.energyFirst=energy;check(ref.set(c));
                const auto p=beginBudgetedEscape(ref,4,energy?BudgetObjective::energy:BudgetObjective::count);check(p.count>0&&p.count<4&&p.cost<=4);}
            if(t==held){c.budget=16;check(ref.set(c));} // repeated high must not admit
            if(t==rearm+1){const auto p=beginBudgetedEscape(ref,16,energy?BudgetObjective::energy:BudgetObjective::count);check(p.count>0);}
            const auto s=ref.process(l[i],r[i]);check(ol[i]==T(s.left)&&(mono||orr[i]==T(s.right)));
            if(t>=held&&t<rearm&&(ol[i]!=0||(!mono&&orr[i]!=0)))heard=true;
            if(t>=end-1024)check(ol[i]==0&&(mono||orr[i]==0));
        }
        start+=n;
    }
    check(heard&&host.save()==bh::encode(c));
}
static void budgetStateTests(){
    MemoryConfig c{};c.wet=321;c.budget=9;c.energyFirst=true;
    auto state=bh::encode(c);MemoryConfig decoded{};check(bh::decode(state,decoded)&&bh::encode(decoded)==state);
    for(unsigned i=0;i<state.size();++i)check(!bh::decode(state.data(),i,decoded));
    for(unsigned i=0;i<17;++i)for(bool energy:{false,true}){c.budget=i;c.energyFirst=energy;state=bh::encode(c);check(bh::decode(state,decoded)&&bh::encode(decoded)==state);}
    auto legacy=state;legacy[3]='1';check(bh::decode(legacy.data(),bh::LegacyStateSize,decoded)&&decoded.budget==0&&!decoded.energyFirst&&decoded.wet==321);
    check(!bh::decode(legacy,decoded));state[43]=17;check(!bh::decode(state,decoded));state[43]=0;state[44]=2;check(!bh::decode(state,decoded));
}
