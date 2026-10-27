#include "FrozenHarnessHelpers.h"

int main(int argc,char** argv){
  if(argc!=2)return 2;const std::string dir=argv[1];
  constexpr unsigned rate=48000,frames=48000;
  const std::array<int,5> notes{{21,36,60,84,108}};
  const std::array<const char*,5> names{{"A0","C2","C4","C6","C8"}};
  const std::array<int,2> velocities{{14,124}};
  std::printf("{\"sample_rate\":48000,\"cases\":[");unsigned index=0;
  for(size_t key=0;key<notes.size();++key)for(int velocity:velocities){
    const std::string name=std::string(names[key])+"v"+std::to_string(velocity);
    keyra::FullInstrument p;keyra::FullInstrumentConfig config;
    config.sampleRate=rate;config.seed=0x4b657972u;
    config.parameters.humanization=.65;config.parameters.dynamics=.5;
    config.parameters.stereoWidth=1;config.parameters.gainDb=0;
    config.parameters.mechanicalLevel=0;config.repetitionController=true;
    config.mechanismBodyCoupling=true;config.mechanismObservation=true;
    if(!p.prepare(config))return 3;
    if(!keyra_fusion_prepare_report(&p,(dir+"/"+name+".prepare.json").c_str()))return 4;
    const std::vector<Event> events{{0,'p',0,.75},{2400,'+',notes[key],velocity/127.},{31200,'-',notes[key],0}};
    std::vector<float> left(frames),right(frames);size_t next=0;unsigned position=0;
    keyra_fusion_capture::reset();
    while(position<frames){
      while(next<events.size()&&events[next].frame==position)if(!dispatch(p,events[next++]))return 5;
      unsigned end=std::min(frames,(position/64+1)*64);
      if(next<events.size())end=std::min(end,events[next].frame);
      if(end<=position||!p.process(left.data()+position,right.data()+position,end-position))return 6;
      position=end;
    }
    if(next!=events.size()||keyra_fusion_capture::overflow||keyra_fusion_capture::cursor!=frames)return 7;
    if(!keyra_pressure_snapshot(&p,(dir+"/"+name+"-final.state").c_str()))return 8;
    FILE* raw=std::fopen((dir+"/"+name+".f64le-pressure").c_str(),"wb");if(!raw)return 9;
    if(std::fwrite(keyra_fusion_capture::pressure.data(),sizeof(double),2*frames,raw)!=2*frames||std::fclose(raw))return 9;
    if(!writeAudio(dir+"/"+name+".f32le-planar",left,right))return 10;
    for(unsigned i=0;i<frames;++i)if(!std::isfinite(left[i])||!std::isfinite(right[i]))return 11;
    const auto d=p.diagnostics();
    if(d.frames!=frames||d.requests!=1||d.launches!=1||d.faultFlags||d.unsafeLaunches||d.nonfiniteOutputFaults||d.rejectedInputs||d.stringCount!=230||d.stringModes!=17778||d.boardModes!=475)return 12;
    if(index++)std::printf(",");
    std::printf("{\"name\":\"%s\",\"note\":%d,\"velocity_MIDI\":%d,\"frames\":48000,\"events_dispatched\":%zu,\"requests\":%llu,\"launches\":%llu,\"faults\":%u,\"unsafe_launches\":%llu,\"nonfinite_output_faults\":%llu,\"rejected_inputs\":%llu}",name.c_str(),notes[key],velocity,next,(unsigned long long)d.requests,(unsigned long long)d.launches,d.faultFlags,(unsigned long long)d.unsafeLaunches,(unsigned long long)d.nonfiniteOutputFaults,(unsigned long long)d.rejectedInputs);
  }
  std::printf("]}\n");return 0;
}
