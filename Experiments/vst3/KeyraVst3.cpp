#include "keyra/Piano.h"
#include "keyra/Parameters.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/base/ustring.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstmidicontrollers.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include "public.sdk/source/main/pluginfactory.h"
#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace keyra::vst3 {
using namespace Steinberg;
using namespace Steinberg::Vst;
const FUID processorId(0x97D620A8,0x42AE4E2D,0xA6B9E95F,0x6B793103);
const FUID controllerId(0x91D5F761,0xBA5B4B83,0x8A6D4ADB,0xF6BF8A1E);
constexpr ParamID sustainBase=1000, notesOffBase=1100, soundOffBase=1200;
using Values=std::array<double,10>;
static_assert(std::atomic<double>::is_always_lock_free,"Keyra VST3 requires lock-free double parameter slots");

double bounded(size_t index,double value) noexcept {
  const auto& p=kParameters[index];
  if(!std::isfinite(value)) return p.defaultValue;
  value=std::clamp(value,p.min,p.max);
  return p.stepped?std::round(value):value;
}
double plain(size_t index,double normalized) noexcept {
  const auto& p=kParameters[index];
  return bounded(index,p.min+std::clamp(normalized,0.,1.)*(p.max-p.min));
}
double normalized(size_t index,double value) noexcept {
  const auto& p=kParameters[index]; return (bounded(index,value)-p.min)/(p.max-p.min);
}
bool transfer(IBStream* stream,void* buffer,int32 count,bool write) {
  if(!stream) return false;
  auto* bytes=static_cast<uint8_t*>(buffer);
  while(count>0) {
    int32 done=0;
    auto result=write?stream->write(bytes,count,&done):stream->read(bytes,count,&done);
    if(result!=kResultOk||done<=0||done>count) return false;
    count-=done; bytes+=done;
  }
  return true;
}
void put32(uint8_t* p,uint32_t n) { for(unsigned i=0;i<4;++i) p[i]=uint8_t(n>>(8*i)); }
uint32_t get32(const uint8_t* p) { uint32_t n=0;for(unsigned i=0;i<4;++i)n|=uint32_t(p[i])<<(8*i);return n; }
bool state(IBStream* stream,Values& values,bool write) {
  // Fixed little-endian encoding. Parse a complete state before changing any
  // parameter; truncated, nonfinite or unknown-version states are rejected.
  std::array<uint8_t,132> bytes{};
  if(write) {
    std::memcpy(bytes.data(),"KYV3",4);put32(bytes.data()+4,1);put32(bytes.data()+8,10);
    for(size_t i=0;i<10;++i) {
      put32(bytes.data()+12+12*i,uint32_t(i));
      uint64_t bits=0;std::memcpy(&bits,&values[i],8);
      for(unsigned j=0;j<8;++j) bytes[16+12*i+j]=uint8_t(bits>>(8*j));
    }
    return transfer(stream,bytes.data(),int32(bytes.size()),true);
  }
  if(!transfer(stream,bytes.data(),int32(bytes.size()),false)||std::memcmp(bytes.data(),"KYV3",4)||get32(bytes.data()+4)!=1||get32(bytes.data()+8)!=10) return false;
  Values pending{};std::array<bool,10> seen{};
  for(size_t i=0;i<10;++i) {
    auto id=get32(bytes.data()+12+12*i);if(id>=10||seen[id])return false;seen[id]=true;
    uint64_t bits=0;for(unsigned j=0;j<8;++j)bits|=uint64_t(bytes[16+12*i+j])<<(8*j);
    double value;std::memcpy(&value,&bits,8);if(!std::isfinite(value))return false;
    pending[id]=bounded(id,value);
  }
  values=pending;return true;
}

class Processor final:public AudioEffect {
public:
  Processor() { setControllerClass(controllerId);for(size_t i=0;i<10;++i)values_[i].store(kParameters[i].defaultValue,std::memory_order_relaxed); }
  static FUnknown* create(void*) { return static_cast<IAudioProcessor*>(new Processor); }
  tresult PLUGIN_API initialize(FUnknown* context) override {
    auto result=AudioEffect::initialize(context);if(result!=kResultOk)return result;
    addEventInput(STR16("MIDI"),16);addAudioOutput(STR16("Stereo"),SpeakerArr::kStereo);return kResultOk;
  }
  tresult PLUGIN_API setBusArrangements(SpeakerArrangement*,int32 inputs,SpeakerArrangement* outputs,int32 count) override {
    if(inputs!=0||count!=1||!outputs||outputs[0]!=SpeakerArr::kStereo)return kResultFalse;
    return AudioEffect::setBusArrangements(nullptr,0,outputs,1);
  }
  tresult PLUGIN_API canProcessSampleSize(int32 size) override { return size==kSample32?kResultTrue:kResultFalse; }
  tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
    if(setup.symbolicSampleSize!=kSample32||!std::isfinite(setup.sampleRate)||setup.sampleRate<8000||setup.sampleRate>384000||setup.maxSamplesPerBlock<0)return kInvalidArgument;
    try { piano_.prepare(setup.sampleRate); } catch(...) { return kResultFalse; }
    prepared_=true;return AudioEffect::setupProcessing(setup);
  }
  tresult PLUGIN_API setActive(TBool active) override { piano_.reset();return AudioEffect::setActive(active); }
  tresult PLUGIN_API setProcessing(TBool processing) override { if(!processing)piano_.reset();return kResultOk; }
  uint32 PLUGIN_API getTailSamples() override { return kInfiniteTail; }
  tresult PLUGIN_API getState(IBStream* stream) override {
    Values values{};for(size_t i=0;i<10;++i)values[i]=values_[i].load(std::memory_order_acquire);
    return state(stream,values,true)?kResultOk:kResultFalse;
  }
  tresult PLUGIN_API setState(IBStream* stream) override {
    Values values{};if(!state(stream,values,false))return kResultFalse;
    // State callbacks never touch the audio-owned piano. Slots are atomic, so
    // hosts loading state during playback cannot race the DSP parameter data.
    for(size_t i=0;i<10;++i)values_[i].store(values[i],std::memory_order_release);
    return kResultOk;
  }
  tresult PLUGIN_API process(ProcessData& data) override {
    if(data.numSamples<0||data.symbolicSampleSize!=kSample32)return kInvalidArgument;
    for(size_t i=0;i<10;++i)piano_.setParameter(static_cast<ParamId>(i),values_[i].load(std::memory_order_acquire));
    struct Cursor { IParamValueQueue* queue=nullptr;int32 index=0,count=0,offset=0;double value=0;bool valid=false; };
    std::array<Cursor,58> queues{};size_t used=0;
    auto recognized=[](ParamID id){return id<10||(id>=sustainBase&&id<sustainBase+16)||(id>=notesOffBase&&id<notesOffBase+16)||(id>=soundOffBase&&id<soundOffBase+16);};
    auto advance=[&](Cursor& cursor) {
      cursor.valid=false;
      while(cursor.index<cursor.count) {
        int32 offset=0;double value=0;
        if(cursor.queue->getPoint(cursor.index++,offset,value)!=kResultTrue||!std::isfinite(value))continue;
        cursor.offset=std::clamp(offset,0,data.numSamples);cursor.value=std::clamp(value,0.,1.);cursor.valid=true;break;
      }
    };
    if(data.inputParameterChanges)for(int32 i=0;i<data.inputParameterChanges->getParameterCount()&&used<queues.size();++i) {
      auto* queue=data.inputParameterChanges->getParameterData(i);if(!queue||!recognized(queue->getParameterId()))continue;
      auto& cursor=queues[used++];cursor.queue=queue;cursor.count=std::max(0,queue->getPointCount());advance(cursor);
    }
    auto apply=[&](Cursor& cursor) {
      auto id=cursor.queue->getParameterId();double value=cursor.value;
      if(id<10){double actual=plain(id,value);values_[id].store(actual,std::memory_order_release);piano_.setParameter(static_cast<ParamId>(id),actual);}
      else if(id>=sustainBase&&id<sustainBase+16)piano_.sustain(value,int(id-sustainBase));
      // MIDI channel-mode messages conventionally carry value zero. Their
      // presence, rather than a threshold on that value, is the command.
      else if(id>=notesOffBase&&id<notesOffBase+16)piano_.allNotesOff(int(id-notesOffBase));
      else if(id>=soundOffBase&&id<soundOffBase+16)piano_.allSoundOff(int(id-soundOffBase));
    };
    int32 eventIndex=0,eventCount=data.inputEvents?std::max(0,data.inputEvents->getEventCount()):0;
    Event nextEvent{};bool haveEvent=false;
    auto next=[&] {
      haveEvent=false;
      while(eventIndex<eventCount)if(data.inputEvents->getEvent(eventIndex++,nextEvent)==kResultTrue) {
        if(nextEvent.busIndex!=0)continue;
        nextEvent.sampleOffset=std::clamp(nextEvent.sampleOffset,0,data.numSamples);haveEvent=true;break;
      }
    };next();
    float* left=nullptr;float* right=nullptr;
    if(data.numOutputs>0&&data.outputs&&data.outputs[0].numChannels==2&&data.outputs[0].channelBuffers32) {
      left=data.outputs[0].channelBuffers32[0];right=data.outputs[0].channelBuffers32[1];
    }
    // A zero-buffer process call may flush automation without audio buffers.
    // Audio calls need the advertised stereo layout and setupProcessing first.
    if(data.numSamples>0&&(!prepared_||!left||!right))return kResultFalse;
    int32 cursor=0;
    for(;;) {
      for(size_t i=0;i<used;++i)while(queues[i].valid&&queues[i].offset<=cursor){apply(queues[i]);advance(queues[i]);}
      while(haveEvent&&nextEvent.sampleOffset<=cursor) {
        if(nextEvent.type==Event::kNoteOnEvent) {
          const auto& note=nextEvent.noteOn;
          if(note.channel>=0&&note.channel<16&&std::isfinite(note.velocity))piano_.noteOn(note.pitch,note.velocity,note.channel,note.noteId);
        }else if(nextEvent.type==Event::kNoteOffEvent) {
          const auto& note=nextEvent.noteOff;if(note.channel>=0&&note.channel<16)piano_.noteOff(note.pitch,note.channel,note.noteId);
        }
        next();
      }
      if(cursor>=data.numSamples)break;
      int32 stop=data.numSamples;
      for(size_t i=0;i<used;++i)if(queues[i].valid)stop=std::min(stop,queues[i].offset);
      if(haveEvent)stop=std::min(stop,nextEvent.sampleOffset);
      if(stop<=cursor)continue;
      piano_.process(left+cursor,right+cursor,uint32_t(stop-cursor));cursor=stop;
    }
    if(data.outputs&&data.numOutputs>0)data.outputs[0].silenceFlags=0;
    return kResultOk;
  }
private:
  Piano piano_;bool prepared_=false;
  std::array<std::atomic<double>,10> values_{};
};

class Controller final:public EditController,public IMidiMapping {
public:
  static FUnknown* create(void*) { return static_cast<IEditController*>(new Controller); }
  DELEGATE_REFCOUNT(EditController)
  tresult PLUGIN_API queryInterface(const char* iid,void** obj) override {
    QUERY_INTERFACE(iid,obj,IMidiMapping::iid,IMidiMapping)
    return EditController::queryInterface(iid,obj);
  }
  tresult PLUGIN_API initialize(FUnknown* context) override {
    auto result=EditController::initialize(context);if(result!=kResultOk)return result;
    for(size_t i=0;i<10;++i) {
      const auto& p=kParameters[i];String128 title{};UString(title,128).fromAscii(p.name);
      if(auto choices=parameterChoices(p.id)) {
        auto* parameter=new StringListParameter(title,ParamID(i));
        for(int choice=0;choice<=int(p.max);++choice){String128 label{};UString(label,128).fromAscii(choices[choice]);parameter->appendString(label);}
        parameter->getInfo().defaultNormalizedValue=normalized(i,p.defaultValue);parameter->setNormalized(normalized(i,p.defaultValue));parameters.addParameter(parameter);
      } else parameters.addParameter(new RangeParameter(title,ParamID(i),i==9?STR16("dB"):nullptr,p.min,p.max,p.defaultValue));
    }
    for(int channel=0;channel<16;++channel) {
      parameters.addParameter(STR16("Sustain"),nullptr,0,0,ParameterInfo::kCanAutomate|ParameterInfo::kIsHidden,sustainBase+channel);
      for(int kind=0;kind<2;++kind) {
        auto* parameter=new StringListParameter(kind?STR16("All sound off"):STR16("All notes off"),(kind?soundOffBase:notesOffBase)+channel,nullptr,ParameterInfo::kCanAutomate|ParameterInfo::kIsHidden);
        parameter->appendString(STR16("Off"));parameter->appendString(STR16("On"));parameters.addParameter(parameter);
      }
    }
    return kResultOk;
  }
  tresult PLUGIN_API setComponentState(IBStream* stream) override { return restore(stream); }
  tresult PLUGIN_API setState(IBStream* stream) override { return restore(stream); }
  tresult PLUGIN_API getState(IBStream* stream) override {
    Values values{};for(size_t i=0;i<10;++i)values[i]=plain(i,getParamNormalized(ParamID(i)));
    return state(stream,values,true)?kResultOk:kResultFalse;
  }
  tresult PLUGIN_API getMidiControllerAssignment(int32 bus,int16 channel,CtrlNumber cc,ParamID& id) override {
    if(bus!=0||channel<0||channel>=16)return kResultFalse;
    if(cc==kCtrlSustainOnOff)id=sustainBase+channel;
    else if(cc==kCtrlAllNotesOff)id=notesOffBase+channel;
    else if(cc==kCtrlAllSoundsOff)id=soundOffBase+channel;
    else return kResultFalse;
    return kResultTrue;
  }
private:
  tresult restore(IBStream* stream) {
    Values values{};if(!state(stream,values,false))return kResultFalse;
    for(size_t i=0;i<10;++i)setParamNormalized(ParamID(i),normalized(i,values[i]));return kResultOk;
  }
};
} // namespace keyra::vst3

using namespace Steinberg;
using namespace Steinberg::Vst;
BEGIN_FACTORY_DEF("Keyra","https://github.com/protocodus/virtual-instrument-keyra","")
DEF_CLASS2(INLINE_UID_FROM_FUID(keyra::vst3::processorId),PClassInfo::kManyInstances,kVstAudioEffectClass,"Keyra",Vst::kDistributable,"Instrument|Piano","0.2.0",kVstVersionString,keyra::vst3::Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(keyra::vst3::controllerId),PClassInfo::kManyInstances,kVstComponentControllerClass,"Keyra Controller",0,"","0.2.0",kVstVersionString,keyra::vst3::Controller::create)
END_FACTORY
