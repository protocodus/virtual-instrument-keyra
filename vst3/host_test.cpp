#include "keyra/Piano.h"
#include "pluginterfaces/base/ipluginbase.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivstmidicontrollers.h"
#include "public.sdk/source/common/memorystream.h"
#include "public.sdk/source/vst/hosting/eventlist.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <iostream>
#include <stdexcept>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <filesystem>
#else
#include <dlfcn.h>
#endif

using namespace Steinberg;
using namespace Steinberg::Vst;
void require(bool good,const char* message) {if(!good)throw std::runtime_error(message);}
class PartialStream:public MemoryStream {
public:
  tresult PLUGIN_API read(void* data,int32 count,int32* done) override {return MemoryStream::read(data,std::min(count,3),done);}
  tresult PLUGIN_API write(void* data,int32 count,int32* done) override {return MemoryStream::write(data,std::min(count,5),done);}
};
int main(int argc,char** argv) {
  try {
    require(argc==2,"Expect plugin binary path");
#if defined(_WIN32)
    HMODULE library=LoadLibraryW(std::filesystem::u8path(argv[1]).wstring().c_str());
    require(library,"LoadLibrary VST3 module failed");
    auto symbol=[&](const char* name){return GetProcAddress(library,name);};
    auto entry=reinterpret_cast<bool(PLUGIN_API*)()>(symbol("InitDll"));
#else
    void* library=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);require(library,"dlopen VST3 module failed");
    auto symbol=[&](const char* name){return dlsym(library,name);};
    auto entry=reinterpret_cast<bool(*)(void*)>(symbol("ModuleEntry"));
#endif
    auto exit=reinterpret_cast<bool(PLUGIN_API*)()>(symbol(
#if defined(_WIN32)
      "ExitDll"
#else
      "ModuleExit"
#endif
    ));
    auto create=reinterpret_cast<IPluginFactory*(PLUGIN_API*)()>(symbol("GetPluginFactory"));
#if defined(_WIN32)
    require(entry&&exit&&create&&entry(),"VST3 entry points");
#else
    require(entry&&exit&&create&&entry(library),"VST3 entry points");
#endif
    auto* factory=create();require(factory&&factory->countClasses()==2,"Processor/controller factory");
    FUID processorId(0x97D620A8,0x42AE4E2D,0xA6B9E95F,0x6B793103);
    FUID controllerId(0x91D5F761,0xBA5B4B83,0x8A6D4ADB,0xF6BF8A1E);
    IComponent* component=nullptr;IAudioProcessor* processor=nullptr;IEditController* controller=nullptr;
    require(factory->createInstance(processorId,IComponent::iid,reinterpret_cast<void**>(&component))==kResultOk,"Create component");
    require(component->queryInterface(IAudioProcessor::iid,reinterpret_cast<void**>(&processor))==kResultOk,"Audio processor interface");
    require(factory->createInstance(controllerId,IEditController::iid,reinterpret_cast<void**>(&controller))==kResultOk,"Create controller");
    HostApplication host;
    require(component->initialize(&host)==kResultOk&&controller->initialize(&host)==kResultOk,"Initialize");
    require(controller->getParameterCount()==58,"Ten sound controls plus per-channel MIDI mappings");
    IMidiMapping* mapping=nullptr;
    require(controller->queryInterface(IMidiMapping::iid,reinterpret_cast<void**>(&mapping))==kResultOk,"MIDI mapping interface");
    ParamID sustain=0;
    require(mapping->getMidiControllerAssignment(0,3,kCtrlSustainOnOff,sustain)==kResultOk&&sustain==1003,"Channel sustain mapping");
    ParamID dummy=0;require(mapping->getMidiControllerAssignment(1,0,kCtrlSustainOnOff,dummy)!=kResultOk,"Reject invalid MIDI bus");
    mapping->release();
    ProcessSetup setup{};setup.processMode=kRealtime;setup.symbolicSampleSize=kSample32;setup.sampleRate=48000;setup.maxSamplesPerBlock=512;
    require(processor->setupProcessing(setup)==kResultOk,"Setup processing");
    require(processor->canProcessSampleSize(kSample64)!=kResultOk,"Do not advertise unsupported 64-bit process");
    require(component->setActive(true)==kResultOk&&processor->setProcessing(true)==kResultOk,"Activate");
    std::array<float,512> left{},right{},expectedL{},expectedR{};
    float* channels[]={left.data(),right.data()};AudioBusBuffers output{};output.numChannels=2;output.channelBuffers32=channels;
    EventList events;
    Event on{};on.busIndex=0;on.sampleOffset=32;on.type=Event::kNoteOnEvent;on.noteOn.channel=3;on.noteOn.pitch=60;on.noteOn.velocity=.7f;on.noteOn.noteId=42;events.addEvent(on);
    Event off{};off.busIndex=0;off.sampleOffset=160;off.type=Event::kNoteOffEvent;off.noteOff.channel=3;off.noteOff.pitch=60;off.noteOff.noteId=42;events.addEvent(off);
    ParameterChanges changes(4);int32 index=0;
    auto* gain=changes.addParameterData(9,index);gain->addPoint(64,.5,index);
    auto* pedal=changes.addParameterData(sustain,index);pedal->addPoint(128,1,index);
    ProcessData data{};data.symbolicSampleSize=kSample32;data.processMode=kRealtime;data.numSamples=512;data.numOutputs=1;data.outputs=&output;data.inputEvents=&events;data.inputParameterChanges=&changes;
    require(processor->process(data)==kResultOk,"Process sample-accurate notes and automation");
    keyra::Piano expected;expected.prepare(48000);
    expected.process(expectedL.data(),expectedR.data(),32);
    expected.noteOn(60,double(.7f),3,42);expected.process(expectedL.data()+32,expectedR.data()+32,32);
    expected.setParameter(keyra::ParamId::Gain,-21);expected.process(expectedL.data()+64,expectedR.data()+64,64);
    expected.sustain(1,3);expected.process(expectedL.data()+128,expectedR.data()+128,32);
    expected.noteOff(60,3,42);expected.process(expectedL.data()+160,expectedR.data()+160,352);
    double energy=0;
    for(size_t i=0;i<left.size();++i) {
      require(std::isfinite(left[i])&&std::isfinite(right[i]),"Finite stereo output");
      require(std::abs(left[i]-expectedL[i])<1e-7&&std::abs(right[i]-expectedR[i])<1e-7,"Sample-accurate output differs from core");
      if(i<32)require(left[i]==0&&right[i]==0,"Note began before scheduled offset");
      energy+=double(left[i])*left[i]+double(right[i])*right[i];
    }
    require(energy>1e-8,"Audible note");
    changes.clearQueue();events.clear();
    auto* panic=changes.addParameterData(1203,index);panic->addPoint(0,0,index);
    require(processor->process(data)==kResultOk,"Zero-valued CC120 channel-mode command");
    expected.allSoundOff(3);expected.process(expectedL.data(),expectedR.data(),512);
    for(size_t i=0;i<left.size();++i)require(std::abs(left[i]-expectedL[i])<1e-7&&std::abs(right[i]-expectedR[i])<1e-7,"CC120 did not clear channel voices");
    PartialStream saved;require(component->getState(&saved)==kResultOk&&saved.getSize()==132,"Partial-write state stream");
    saved.seek(0,IBStream::kIBSeekSet,nullptr);require(controller->setComponentState(&saved)==kResultOk,"Controller loads partial-read component state");
    require(std::abs(controller->getParamNormalized(9)-.5)<1e-12,"Automation saved to state");
    saved.seek(0,IBStream::kIBSeekSet,nullptr);require(component->setState(&saved)==kResultOk,"Load partial-read state stream");
    saved.getData()[0]='!';saved.seek(0,IBStream::kIBSeekSet,nullptr);require(component->setState(&saved)!=kResultOk,"Reject malformed state header");
    saved.getData()[0]='K';saved.setSize(12);saved.seek(0,IBStream::kIBSeekSet,nullptr);require(component->setState(&saved)!=kResultOk,"Reject truncated state");
    ProcessData flush{};flush.symbolicSampleSize=kSample32;flush.numSamples=0;require(processor->process(flush)==kResultOk,"Zero-frame flush");
    processor->setProcessing(false);component->setActive(false);
    controller->terminate();component->terminate();controller->release();processor->release();component->release();factory->release();
    require(exit(),"Module exit");
#if defined(_WIN32)
    require(FreeLibrary(library)!=0,"FreeLibrary VST3 module failed");
#else
    dlclose(library);
#endif
    std::cout<<"VST3 factory, MIDI mapping, sample offsets, automation, partial-stream state and malformed-state checks passed\n";
  }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
