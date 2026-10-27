// Included once inside namespace grand, after the unchanged UnisonGroup.
// Private scheduling experiment: no coefficient, mode or physical operator change.
struct FreeModeRun {
  int stringIndex=0;size_t firstMode=0,count=0;
  float *q=nullptr,*p=nullptr;
  const float *c=nullptr,*s=nullptr,*damp=nullptr;
  void step(){
    float *__restrict yq=q,*__restrict yp=p;
    const float *__restrict yc=c,*__restrict ys=s,*__restrict yd=damp;
    for(size_t i=0;i<count;++i){
      float v=yp[i]*yd[i],y=yq[i];
      yq[i]=yc[i]*y+ys[i]*v;
      float rotated=yc[i]*v-ys[i]*y;yp[i]=rotated*yd[i];
    }
  }
};
struct FreeUnisonGroup:UnisonGroup {
  std::array<int,3> stringIndex{};
  std::array<size_t,3> firstMode{};
  std::array<float*,3> position{};
  std::array<const float*,3> cosine{},sine{},damping{};
  std::vector<size_t> sourceRows;
  template<int N> void fusedStep(){
    float *__restrict q0=position[0],*__restrict p0=velocity[0];
    float *__restrict q1=position[1],*__restrict p1=velocity[1];
    float *__restrict q2=position[2],*__restrict p2=velocity[2];
    const float *__restrict c0=cosine[0],*__restrict s0=sine[0],*__restrict d0=damping[0];
    const float *__restrict c1=cosine[1],*__restrict s1=sine[1],*__restrict d1=damping[1];
    const float *__restrict c2=cosine[2],*__restrict s2=sine[2],*__restrict d2=damping[2];
    const float *__restrict w0=omega[0].data(),*__restrict w1=omega[1].data(),*__restrict w2=omega[2].data();
    const float *__restrict r0=inverse[0].data(),*__restrict r1=inverse[1].data(),*__restrict r2=inverse[2].data();
    const float *__restrict coefficientData=coefficient.data();
    for(size_t i=0;i<coefficient.size();++i){
      float v0=p0[i]*d0[i],y0=q0[i];q0[i]=c0[i]*y0+s0[i]*v0;
      float rotated0=c0[i]*v0-s0[i]*y0;float next0=rotated0*d0[i];
      float next1=0,next2=0;
      if constexpr(N>1){float v1=p1[i]*d1[i],y1=q1[i];q1[i]=c1[i]*y1+s1[i]*v1;
        float rotated1=c1[i]*v1-s1[i]*y1;next1=rotated1*d1[i];}
      if constexpr(N>2){float v2=p2[i]*d2[i],y2=q2[i];q2[i]=c2[i]*y2+s2[i]*v2;
        float rotated2=c2[i]*v2-s2[i]*y2;next2=rotated2*d2[i];}
      float sum=w0[i]*next0;
      if constexpr(N>1)sum+=w1[i]*next1;
      if constexpr(N>2)sum+=w2[i]*next2;
      float impulse=coefficientData[i]*sum;
      p0[i]=next0-impulse*r0[i];
      if constexpr(N>1)p1[i]=next1-impulse*r1[i];
      if constexpr(N>2)p2[i]=next2-impulse*r2[i];
    }
  }
};
struct FreeUnisonInventory {
  bool valid=false;
  size_t modeCount=0,fusedModes=0,fallbackModes=0,originalRows=0,scheduledRows=0,groupCount=0;
  size_t stringsOwned=0,keysOwned=0;
  bool uniqueModeUpdates=false,uniqueRowMembership=false,originalGroupedRowsExact=false;
};
