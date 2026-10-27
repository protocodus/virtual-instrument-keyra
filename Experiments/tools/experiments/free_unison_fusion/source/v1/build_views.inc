  bool buildFreeUnisonViews(){
    freeUnisonInventory={};freeUnisonInventory.originalRows=unisonPorts.size();
    for(auto& groups:freeUnisonGroupIndices)groups.clear();
    for(auto& runs:freeModeRuns)runs.clear();
    std::vector<int> owner(strings.size(),-1);
    std::vector<std::vector<unsigned char>> covered(strings.size()),updates(strings.size());
    for(size_t si=0;si<strings.size();++si){covered[si].resize(strings[si].m.size());updates[si].resize(strings[si].m.size());freeUnisonInventory.modeCount+=strings[si].m.size();}
    for(size_t ki=0;ki<keys.size();++ki){++freeUnisonInventory.keysOwned;
      for(int si:keys[ki].strings){if(si<0||size_t(si)>=strings.size()||owner[si]!=-1||strings[si].note!=int(ki)+21)return false;owner[si]=int(ki);++freeUnisonInventory.stringsOwned;}}
    for(int key:owner)if(key<0)return false;
    const auto sameFloat=[](float a,float b){return std::memcmp(&a,&b,sizeof(float))==0;};
    // Attach views to the EXISTING float groups. No coefficient/omega/inverse
    // array is duplicated or recomputed. Grouped scalar fixtures remain usable.
    size_t originalRow=0;
    for(size_t gi=0;gi<unisonGroups.size();++gi){auto& group=unisonGroups[gi];group.firstSourceRow=originalRow;
      if(group.coefficient.empty()||group.count<1||group.count>3)return false;
      int key=-1;
      for(size_t offset=0;offset<group.coefficient.size();++offset){
        if(originalRow>=unisonPorts.size())return false;const auto& port=unisonPorts[originalRow++];
        if(port.count<1||port.count>3||port.modes.size()!=size_t(port.count)||group.count!=port.count||!sameFloat(group.coefficient[offset],port.coefficient))return false;
        for(int lane=0;lane<port.count;++lane){const auto [si,mi]=port.modes[lane];
          if(si<0||size_t(si)>=strings.size()||mi<0||size_t(mi)>=strings[si].m.size()||covered[si][mi])return false;
          if(key<0)key=owner[si];if(owner[si]!=key)return false;
          auto& m=strings[si].m;
          if(group.omega[lane].size()!=group.coefficient.size()||group.inverse[lane].size()!=group.coefficient.size()||
             port.velocityState[lane]!=&m.p[mi]||!sameFloat(port.omega[lane],m.omega[mi])||
             group.velocity[lane]+offset!=port.velocityState[lane]||!sameFloat(group.omega[lane][offset],port.omega[lane])||!sameFloat(group.inverse[lane][offset],port.inverseOmega[lane]))return false;
          if(offset==0){group.stringIndex[lane]=si;group.firstMode[lane]=size_t(mi);
            group.position[lane]=m.q.data()+mi;group.cosine[lane]=m.c.data()+mi;group.sine[lane]=m.s.data()+mi;group.damping[lane]=m.damp.data()+mi;}
          if(group.stringIndex[lane]!=si||group.firstMode[lane]+offset!=size_t(mi)||
             group.position[lane]+offset!=m.q.data()+mi||group.cosine[lane]+offset!=m.c.data()+mi||
             group.sine[lane]+offset!=m.s.data()+mi||group.damping[lane]+offset!=m.damp.data()+mi)return false;
          covered[si][mi]=1;
        }
      }
      if(key<0)return false;freeUnisonGroupIndices[key].push_back(gi);
    }
    if(originalRow!=unisonPorts.size())return false;freeUnisonInventory.originalGroupedRowsExact=true;
    // Uncovered modes include the complete secondary polarization and any
    // truncated/nonmember primary tail. Each keeps the original free arithmetic.
    for(size_t si=0;si<strings.size();++si){auto& m=strings[si].m;size_t first=0;
      while(first<m.size()){if(covered[si][first]){++first;continue;}size_t end=first+1;while(end<m.size()&&!covered[si][end])++end;
        FreeModeRun run;run.stringIndex=int(si);run.firstMode=first;run.count=end-first;run.q=m.q.data()+first;run.p=m.p.data()+first;
        run.c=m.c.data()+first;run.s=m.s.data()+first;run.damp=m.damp.data()+first;freeModeRuns[owner[si]].push_back(run);first=end;}}
    std::vector<unsigned char> rowUpdates(unisonPorts.size());
    for(size_t key=0;key<keys.size();++key){
      for(size_t gi:freeUnisonGroupIndices[key]){const auto& group=unisonGroups[gi];++freeUnisonInventory.groupCount;
        for(size_t offset=0;offset<group.coefficient.size();++offset){const size_t row=group.firstSourceRow+offset;if(row>=unisonPorts.size()||rowUpdates[row]++)return false;const auto& port=unisonPorts[row];
          if(group.count!=port.count||!sameFloat(group.coefficient[offset],port.coefficient))return false;
          ++freeUnisonInventory.scheduledRows;
          for(int lane=0;lane<group.count;++lane){const int si=group.stringIndex[lane];const size_t mi=group.firstMode[lane]+offset;
            if(owner[si]!=int(key)||mi>=strings[si].m.size()||port.modes[lane]!=std::make_pair(si,int(mi))||
               group.velocity[lane]+offset!=port.velocityState[lane]||!sameFloat(group.omega[lane][offset],port.omega[lane])||!sameFloat(group.inverse[lane][offset],port.inverseOmega[lane]))return false;
            ++updates[si][mi];++freeUnisonInventory.fusedModes;
          }
        }
      }
      for(const auto& run:freeModeRuns[key]){const auto& m=strings[run.stringIndex].m;
        if(owner[run.stringIndex]!=int(key)||run.firstMode+run.count>m.size()||
           run.q!=m.q.data()+run.firstMode||run.p!=m.p.data()+run.firstMode||run.c!=m.c.data()+run.firstMode||
           run.s!=m.s.data()+run.firstMode||run.damp!=m.damp.data()+run.firstMode)return false;
        for(size_t offset=0;offset<run.count;++offset){++updates[run.stringIndex][run.firstMode+offset];++freeUnisonInventory.fallbackModes;}}
    }
    for(const auto& cells:updates)for(unsigned char count:cells)if(count!=1)return false;
    for(unsigned char count:rowUpdates)if(count!=1)return false;
    freeUnisonInventory.uniqueModeUpdates=true;freeUnisonInventory.uniqueRowMembership=true;
    freeUnisonInventory.valid=freeUnisonInventory.modeCount==freeUnisonInventory.fusedModes+freeUnisonInventory.fallbackModes&&freeUnisonInventory.originalRows==freeUnisonInventory.scheduledRows;
    return freeUnisonInventory.valid;
  }
  size_t freeUnisonExtraBytes() const {
    size_t result=sizeof(freeUnisonGroupIndices)+sizeof(freeModeRuns)+sizeof(freeUnisonInventory);
    result+=unisonGroups.capacity()*(sizeof(FreeUnisonGroup)-sizeof(UnisonGroup));
    for(const auto& groups:freeUnisonGroupIndices)result+=groups.capacity()*sizeof(size_t);
    for(const auto& runs:freeModeRuns)result+=runs.capacity()*sizeof(FreeModeRun);
    return result;
  }
