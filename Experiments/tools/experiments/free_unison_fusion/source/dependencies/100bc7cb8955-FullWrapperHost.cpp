#include "Keyra.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <limits>
#include <memory>
#include <new>
#include <string>
#include <vector>

namespace {
#ifndef KEYRA_EXPECT_FULL_STRING_MODES
#define KEYRA_EXPECT_FULL_STRING_MODES 17778
#endif
unsigned testSampleRate=48000;
bool watchAllocations = false;
size_t audioAllocations = 0;
void check(bool value, const char* text) { if (!value) { std::cerr << text << '\n'; std::exit(1); } }
constexpr const char* names[] = {"dynamics","humanization","mechanicalLevel","width","gain"};
constexpr double defaults[] = {.5,.65,.025,.5,.75};
TJBox_Value num(double x) { return {kJBox_Number,x,0}; }
TJBox_Value flag(bool x) { return {kJBox_Boolean,x ? 1.0 : 0.0,0}; }
struct Host {
    std::map<std::string,uint32_t> objects, properties;
    std::map<uint64_t,TJBox_Value> mom;
    std::array<std::array<float,64>,2> output{};
    std::array<bool,2> written{};
    std::array<uint32_t,2> outputObjects{};
    bool constructing = false;
    int constructorReads = 0;
    double reset = 0;
};
Host* current = nullptr;
uint64_t key(TJBox_PropertyRef ref) { return (uint64_t(ref.object)<<32)|ref.property; }
void set(const char* object, const char* name, TJBox_Value value) {
    current->mom[key(JBox_MakePropertyRef(JBox_GetMotherboardObjectRef(object),name))] = value;
}
TJBox_PropertyDiff change(const char* object, const char* name, TJBox_Value value, int frame) {
    const auto ref = JBox_MakePropertyRef(JBox_GetMotherboardObjectRef(object),name);
    const auto old = current->mom[key(ref)]; current->mom[key(ref)] = value;
    return {ref.object,ref,0,old,value,static_cast<uint16_t>(frame)};
}
TJBox_PropertyDiff note(int pitch, double value, int frame, double previous = 0) {
    const auto obj = JBox_GetMotherboardObjectRef("/note_states");
    return {obj,{},static_cast<uint32_t>(pitch),num(previous),num(value),static_cast<uint16_t>(frame)};
}
void setup(Host& host, bool left = true, bool right = true) {
    current = &host;
    for (int i=0;i<5;++i) set("/custom_properties",names[i],num(defaults[i]));
    set("/custom_properties","sustainPedal",num(0));
    set("/audio_outputs/left","connected",flag(left));
    set("/audio_outputs/right","connected",flag(right));
    host.outputObjects={JBox_GetMotherboardObjectRef("/audio_outputs/left"),JBox_GetMotherboardObjectRef("/audio_outputs/right")};
}
std::unique_ptr<CKeyra> device(Host& host, double rate = testSampleRate) {
    current=&host; host.constructing=true;
    auto result=std::make_unique<CKeyra>(rate);
    host.constructing=false;
    check(host.constructorReads==0,"constructor must not read MOM");
    return result;
}
void render(Host& host,CKeyra& device,const std::vector<TJBox_PropertyDiff>& diffs={}) {
    current=&host;host.written.fill(false);
    for(auto& channel:host.output)channel.fill(123.f); // Host ignores unsubmitted buffers.
    watchAllocations=true;
    device.RenderBatch(diffs.empty()?nullptr:diffs.data(),static_cast<uint32_t>(diffs.size()));
    watchAllocations=false;
    for(int c=0;c<2;++c){
        if(!host.written[c])host.output[c].fill(0);
        for(float x:host.output[c])check(std::isfinite(x),"finite host samples");
    }
}
// The host mock is authored test code, not a licensed SDK ABI implementation.
using Values=std::array<double,5>;
Values initialValues() { Values out{};std::copy(std::begin(defaults),std::end(defaults),out.begin());return out; }
void install(const Values& values) { for(int i=0;i<5;++i)set("/custom_properties",names[i],num(values[i])); }
keyra::FullInstrumentParameters controls(const Values& values) {
    keyra::FullInstrumentParameters p;
    p.dynamics=values[0];p.humanization=values[1];p.mechanicalLevel=values[2];
    p.stereoWidth=2*values[3];p.gainDb=-60+72*values[4];return p;
}
void configure(keyra::FullInstrument& piano,const Values& values) {
    check(piano.prepare(testSampleRate),"full reference prepare");
    check(piano.setParameters(controls(values)),"full reference controls");piano.reset();
}
void process(keyra::FullInstrument& piano,float* l,float* r,unsigned count) {
    check(piano.process(l,r,count),"full reference process");
}
void equal(const Host& host,const float* l,const float* r,const char* message) {
    check(std::memcmp(host.output[0].data(),l,64*sizeof(float))==0&&
          std::memcmp(host.output[1].data(),r,64*sizeof(float))==0,message);
}
double energy(const Host& host) { double sum=0;for(const auto& c:host.output)for(float x:c)sum+=double(x)*x;return sum; }
void healthy(const CKeyra& piano) {
    const auto d=piano.FullDiagnostics();
    check(d.faultFlags==0&&d.bridgeFaults==0&&d.contactFaults==0&&d.nonfiniteOutputFaults==0&&d.unsafeLaunches==0,"full wrapper solver fault");
    check(d.stringCount==230&&d.stringModes==KEYRA_EXPECT_FULL_STRING_MODES&&d.boardModes==475,"full wrapper changed selected profile topology");
}
void startupAutomationAndReset() {
    Host host;setup(host);auto values=initialValues();
    values[0]=.65;values[1]=.4;values[2]=0;install(values);
    auto instance=device(host);
    // MOM contains the final values before the first callback; the adapter
    // must recover the initial image and apply both changes at their offsets.
    auto dynamics=change("/custom_properties","dynamics",num(.8),23);
    auto gain=change("/custom_properties","gain",num(.7),41);
    const std::vector<TJBox_PropertyDiff> events{note(48,87,7),note(67,93,23),dynamics,gain};
    render(host,*instance,events);
    keyra::FullInstrument reference;configure(reference,values);
    float l[64]{},r[64]{};
    process(reference,l,r,7);check(reference.noteOn(48,87./127),"reference first request");
    process(reference,l+7,r+7,16);values[0]=.8;check(reference.setParameters(controls(values)),"reference dynamics automation");
    check(reference.noteOn(67,93./127),"reference second request");process(reference,l+23,r+23,18);
    values[4]=.7;check(reference.setParameters(controls(values)),"reference output automation");process(reference,l+41,r+41,23);
    equal(host,l,r,"full sample-offset note/control and initial MOM parity");
    for(int i=0;i<7;++i)check(host.output[0][i]==0&&host.output[1][i]==0,"clear full pre-onset prefix");
    check(energy(host)>1e-10,"audible full parity fixture");healthy(*instance);
    const auto original=host.output;
    values[0]=.65;values[4]=.75;install(values);host.reset=1;
    auto repeatDynamics=change("/custom_properties","dynamics",num(.8),23);
    auto repeatGain=change("/custom_properties","gain",num(.7),41);
    render(host,*instance,{note(48,87,7),note(67,93,23),repeatDynamics,repeatGain});
    check(host.output==original,"transport reset did not reproduce full seeded performance");
    check(instance->FullDiagnostics().frames==64&&instance->FullDiagnostics().requests==2,"transport reset retained full frame/request state");
    render(host,*instance);check(instance->FullDiagnostics().frames==128,"repeated reset counter reset the full core again");
}
void activeRepeatCancellationAndRecovery() {
    Host host;setup(host);auto values=initialValues();values[2]=0;install(values);
    auto instance=device(host);
    render(host,*instance,{note(60,100,0),note(60,40,24,100),note(60,0,40,40)});
    auto d=instance->FullDiagnostics();
    check(d.requests==2&&d.launches==1&&d.cancelled==1&&d.coalesced==0,"active repeat did not queue and cancel on release");
    // An unlaunched, cancelled request must not change the contact trajectory
    // or ringing strings. Silence independent mechanism sources for this check.
    keyra::FullInstrument reference;configure(reference,values);
    float l[64]{},r[64]{};
    check(reference.noteOn(60,100./127),"reference cancellation strike");process(reference,l,r,40);
    check(reference.noteOff(60),"reference cancellation release");process(reference,l+40,r+40,24);
    equal(host,l,r,"queued request reset an active hammer or ringing strings");
    for(int i=0;i<8;++i){render(host,*instance);process(reference,l,r,64);equal(host,l,r,"cancelled repeat changed subsequent ringing state");}
    healthy(*instance);
    host.reset=2;
    auto pedal=change("/custom_properties","sustainPedal",num(1),0);
    std::vector<TJBox_PropertyDiff> repeats{pedal,note(60,90,0)};
    for(int i=0;i<12;++i)repeats.push_back(note(60,40+i,0,90));
    render(host,*instance,repeats);
    d=instance->FullDiagnostics();
    check(d.requests==13&&d.launches==1&&d.deferred>=12&&d.coalesced==11,"full wrapper lost bounded rapid-repeat requests");
    double tailEnergy=0;
    const unsigned tailBatches=(64u*testSampleRate+47999u)/48000u;
    for(unsigned i=1;i<tailBatches;++i){render(host,*instance);tailEnergy+=energy(host);}
    d=instance->FullDiagnostics();
    check(d.frames==64u*tailBatches&&d.launches==2&&d.expired==0&&d.activeHammers<=1,"coalesced full repeat failed to launch safely after recovery");
    check(d.pedal>.99&&d.pedalTarget==1&&tailEnergy>0,"pedal or ringing strings did not survive full repeat");healthy(*instance);
}
void touchingRepeatCase(unsigned offset) {
    Host host;setup(host);auto values=initialValues();values[2]=0;install(values);
    auto instance=device(host);
    keyra::FullInstrument reference;configure(reference,values);
    // Preserve the physical 100/200 ms spacing and at least 8 ms after the last
    // press. The default 48 kHz invocation still advances exactly 9984 frames.
    const unsigned totalFrames=(((208u*testSampleRate+999u)/1000u+63u)/64u)*64u;
    constexpr std::array<unsigned,4> partitions{{1,3,17,64}};
    const std::array<unsigned,3> times{{offset,testSampleRate/10+offset,testSampleRate/5+offset}};
    std::array<uint64_t,2> referenceAdmissionUpper{},wrapperAdmissionUpper{};
    unsigned partition=0,event=0;
    double sounded=0;
    for(unsigned start=0;start<totalFrames;start+=64) {
        std::vector<TJBox_PropertyDiff> events;
        const bool hasEvent=event<times.size()&&times[event]<start+64;
        const unsigned local=hasEvent?times[event]-start:64;
        if(hasEvent) {
            if(event==0)events.push_back(change("/custom_properties","sustainPedal",num(1),static_cast<int>(local)));
            else events.push_back(note(60,0,static_cast<int>(local),90));
            events.push_back(note(60,90,static_cast<int>(local)));
        }
        render(host,*instance,events);
        auto d=instance->FullDiagnostics();
        if(hasEvent&&event>0) {
            // A callback ends at most64 samples after a touching pair. The
            // request must still be waiting for finite key lift, with the
            // old inactive hammer undisturbed, rather than an instant reset.
            check(d.requests==event+1&&d.launches==event&&d.activeHammers==0,
                  "touching Reason pair did not defer the physical strike");
            check(d.deferred==event&&d.coalesced==0&&d.cancelled==0&&d.expired==0,
                  "touching Reason request was lost or misclassified");
        }
        for(unsigned index=0;index<2;++index)if(d.launches>=index+2&&wrapperAdmissionUpper[index]==0)
            wrapperAdmissionUpper[index]=d.frames-times[index+1];
        float l[64]{},r[64]{};
        auto advance=[&](unsigned first,unsigned last) {
            while(first<last) {
                const unsigned count=std::min(partitions[partition++%partitions.size()],last-first);
                process(reference,l+first,r+first,count);first+=count;
                const auto rd=reference.diagnostics();
                for(unsigned index=0;index<2;++index)if(rd.launches>=index+2&&referenceAdmissionUpper[index]==0)
                    referenceAdmissionUpper[index]=rd.frames-times[index+1];
            }
        };
        advance(0,local);
        if(hasEvent) {
            if(event==0)check(reference.sustain(1),"touching reference pedal request");
            else check(reference.noteOff(60),"touching reference release");
            check(reference.noteOn(60,90./127),"touching reference press");
            const auto immediate=reference.diagnostics();
            check(immediate.frames==times[event]&&immediate.requests==event+1,"touching event timestamp drift");
            if(event>0)check(immediate.launches==event&&immediate.activeHammers==0&&immediate.deferred==event,
                             "touching reference pair launched before finite lift");
            ++event;
        }
        advance(local,64);
        equal(host,l,r,"touching Reason event offsets/fragmented canonical output differ");
        check(reference.diagnostics().frames==start+64,"fragmented touching reference clock drift");
        sounded+=energy(host);healthy(*instance);
    }
    const auto result=instance->FullDiagnostics();
    const auto direct=reference.diagnostics();
    check(event==3&&result.frames==totalFrames&&result.requests==3&&result.launches==3&&result.expired==0&&
          result.cancelled==0&&result.coalesced==0&&result.deferred==2&&result.pedal>.99,
          "touching Reason repeats failed to launch all three physical strikes");
    check(direct.requests==result.requests&&direct.launches==result.launches&&direct.deferred==result.deferred&&
          direct.expired==0&&direct.faultFlags==0&&direct.unsafeLaunches==0&&sounded>0,
          "touching canonical request/state parity failed");
    for(unsigned i=0;i<2;++i) {
        // Diagnostics observe admission at a process endpoint. Different
        // partitions bound the same roughly4ms authored lift without implying
        // sample-exact audible contact at that endpoint.
        const unsigned lowerFrames=180u*testSampleRate/48000u;
        const unsigned upperFrames=(193u*testSampleRate+47999u)/48000u+63u;
        check(referenceAdmissionUpper[i]>=lowerFrames&&referenceAdmissionUpper[i]<=upperFrames,
              "touching canonical lift did not complete within its finite timing bound");
        check(wrapperAdmissionUpper[i]>=referenceAdmissionUpper[i]&&wrapperAdmissionUpper[i]<=upperFrames+64u,
              "touching Reason lift did not complete within its callback observation bound");
    }
    std::cout<<"Touching full Reason repeats rate="<<testSampleRate<<" offset="<<offset
             <<" reference admission upper bounds="<<referenceAdmissionUpper[0]<<','<<referenceAdmissionUpper[1]
             <<" frames; callback upper bounds="<<wrapperAdmissionUpper[0]<<','<<wrapperAdmissionUpper[1]<<" frames\n";
}
void touchingRepeatsAndPartitionParity() {
    touchingRepeatCase(0);
    touchingRepeatCase(7); // Same relative100/200ms pairs inside Reason batches.
}
void sustainDisconnectedAndReconnect() {
    Host host;setup(host,false,false);auto instance=device(host);
    keyra::FullInstrument reference;configure(reference,initialValues());
    auto pedal=change("/custom_properties","sustainPedal",num(1),3);
    render(host,*instance,{pedal,note(60,100,9),note(60,0,39,100)});
    float l[64]{},r[64]{};process(reference,l,r,3);check(reference.sustain(1),"reference pedal down");process(reference,l+3,r+3,6);
    check(reference.noteOn(60,100./127),"reference disconnected strike");process(reference,l+9,r+9,30);
    check(reference.noteOff(60),"reference disconnected release");process(reference,l+39,r+39,25);
    check(!host.written[0]&&!host.written[1],"full wrapper wrote disconnected output");
    for(int i=0;i<15;++i){render(host,*instance);process(reference,l,r,64);}
    auto left=change("/audio_outputs/left","connected",flag(true),17);
    auto right=change("/audio_outputs/right","connected",flag(true),17);
    render(host,*instance,{left,right});process(reference,l,r,64);
    for(int i=0;i<17;++i)l[i]=r[i]=0;
    equal(host,l,r,"full disconnected chronology/reconnect offset changed ringing state");
    auto release=change("/custom_properties","sustainPedal",num(0),27);
    render(host,*instance,{release});process(reference,l,r,27);check(reference.sustain(0),"reference pedal release");process(reference,l+27,r+27,37);
    equal(host,l,r,"full pedal-release offset mismatch");healthy(*instance);
}
void monoAndInstanceIsolation() {
    Host stereo,mono,other;setup(stereo);auto stereoDevice=device(stereo);
    setup(mono,false,true);auto monoDevice=device(mono);
    setup(other);auto otherDevice=device(other);
    current=&stereo;render(stereo,*stereoDevice,{note(84,105,0)});
    current=&mono;render(mono,*monoDevice,{note(84,105,0)});
    for(int i=0;i<64;++i)check(mono.output[1][i]==.5f*(stereo.output[0][i]+stereo.output[1][i]),"full single-jack mono fold mismatch");
    check(!mono.written[0]&&mono.written[1],"full mono routing wrote wrong jack");
    render(other,*otherDevice);check(energy(other)==0&&otherDevice->FullDiagnostics().requests==0,"full instances share state");
    healthy(*stereoDevice);healthy(*monoDevice);healthy(*otherDevice);
    check(JBox_Export_CreateNativeObject("no-op",nullptr,0)==nullptr,"full unknown native operation accepted");
    JBox_Export_RenderRealtime(nullptr,nullptr,5);
}
void malformedAndRateRejection() {
    for(double rate:{std::numeric_limits<double>::quiet_NaN(),0.,8000.,45000.,192000.,48000.5})
        check(CKeyra::SanitizeSampleRate(rate)==0,"full unsupported sample rate did not reject preparation");
    for(double rate:{44100.,48000.,88200.,96000.})check(CKeyra::SanitizeSampleRate(rate)==rate,"supported full sample rate changed");
    Host inactive;setup(inactive);auto inactiveDevice=device(inactive,192000);
    check(inactiveDevice->FullDiagnostics().stringCount==0,"unsupported full rate prepared a different-rate piano");
    render(inactive,*inactiveDevice,{note(60,100,0)});
    check(energy(inactive)==0&&inactiveDevice->FullDiagnostics().requests==0&&inactiveDevice->FullDiagnostics().frames==0,
          "unsupported full rate produced audio or advanced a mismatched clock");
    check(JBox_Export_CreateNativeObject("no-op",nullptr,0)==nullptr,"invalid full create operation accepted");
    auto* defaultRate=static_cast<CKeyra*>(JBox_Export_CreateNativeObject("Instance",nullptr,0));
    check(defaultRate!=nullptr&&defaultRate->FullDiagnostics().stringCount==230,"missing sample-rate parameter lost explicit44100default");delete defaultRate;
    TJBox_Value nonnumeric{};
    auto* defaultType=static_cast<CKeyra*>(JBox_Export_CreateNativeObject("Instance",&nonnumeric,1));
    check(defaultType!=nullptr&&defaultType->FullDiagnostics().stringCount==230,"nonnumeric sample-rate parameter lost explicit44100default");delete defaultType;
    Host host;setup(host);auto instance=device(host);
    auto invalid=change("/custom_properties","humanization",num(std::numeric_limits<double>::quiet_NaN()),0);
    render(host,*instance,{note(-1,127,0),note(200,127,0),note(60,std::numeric_limits<double>::quiet_NaN(),0),invalid});
    check(energy(host)==0&&instance->FullDiagnostics().requests==0,"invalid full notes/control produced a strike");
    render(host,*instance,{note(60,90,500)});
    for(int i=0;i<63;++i)check(host.output[0][i]==0&&host.output[1][i]==0,"full legacy frame index was not clamped to63");
    host.reset=1;render(host,*instance);
    render(host,*instance,{note(60,90,30),note(62,90,10)});
    check(instance->FullDiagnostics().requests==1,"descending malformed full event was not ignored");
    healthy(*instance);
}
}
void* operator new(std::size_t size) { if(watchAllocations)++audioAllocations;if(void* p=std::malloc(size?size:1))return p;std::abort(); }
void* operator new[](std::size_t size) { return ::operator new(size); }
void* operator new(std::size_t size,const std::nothrow_t&) noexcept { if(watchAllocations)++audioAllocations;return std::malloc(size?size:1); }
void* operator new[](std::size_t size,const std::nothrow_t& tag) noexcept { return ::operator new(size,tag); }
void operator delete(void* pointer,const std::nothrow_t&) noexcept { std::free(pointer); }
void operator delete[](void* pointer,const std::nothrow_t&) noexcept { std::free(pointer); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
void operator delete(void* pointer,std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer,std::size_t) noexcept { std::free(pointer); }
TJBox_ObjectRef JBox_GetMotherboardObjectRef(const char* path) {
    auto found=current->objects.find(path);if(found!=current->objects.end())return found->second;
    const auto id=static_cast<uint32_t>(current->objects.size()+1);current->objects[path]=id;return id;
}
TJBox_PropertyRef JBox_MakePropertyRef(TJBox_ObjectRef object,const char* name) {
    auto found=current->properties.find(name);uint32_t id;
    if(found==current->properties.end()){id=static_cast<uint32_t>(current->properties.size()+1);current->properties[name]=id;}else id=found->second;
    return {object,id};
}
TJBox_Value JBox_LoadMOMProperty(TJBox_PropertyRef ref) {
    if(current->constructing)++current->constructorReads;
    auto it=current->mom.find(key(ref));return it==current->mom.end()?TJBox_Value{}:it->second;
}
TJBox_Value JBox_LoadMOMPropertyByTag(TJBox_ObjectRef object,TJBox_Tag tag) {
    if(current->constructing)++current->constructorReads;
    if(tag==kJBox_AudioOutputBuffer)for(unsigned i=0;i<2;++i)if(current->outputObjects[i]==object)return {kJBox_DSPBuffer,0,i};
    return {};
}
double JBox_LoadMOMPropertyAsNumber(TJBox_ObjectRef,TJBox_Tag tag) { return tag==kJBox_TransportRequestResetAudio?current->reset:0; }
TJBox_Bool JBox_IsReferencingSameProperty(TJBox_PropertyRef a,TJBox_PropertyRef b) { return a==b; }
TJBox_ValueType JBox_GetType(TJBox_Value value) { return value.type; }
double JBox_GetNumber(TJBox_Value value) { return value.number; }
bool JBox_GetBoolean(TJBox_Value value) { return value.number!=0; }
void JBox_SetDSPBufferData(TJBox_Value value,int first,int last,const float* samples) {
    check(value.type==kJBox_DSPBuffer&&value.buffer<2&&first==0&&last==64,"every submitted output writes all 64 frames");
    std::copy(samples,samples+64,current->output[value.buffer].begin());current->written[value.buffer]=true;
}
int main(int argc,char** argv) {
    check(argc<=2,"usage: keyra_rack_full_host [44100|48000|88200|96000]");
    if(argc==2) {
        char* end=nullptr;const unsigned long rate=std::strtoul(argv[1],&end,10);
        check(end&&end!=argv[1]&&*end=='\0'&&(rate==44100||rate==48000||rate==88200||rate==96000),"unsupported mock test sample rate");
        testSampleRate=static_cast<unsigned>(rate);
    }
    startupAutomationAndReset();activeRepeatCancellationAndRecovery();touchingRepeatsAndPartitionParity();sustainDisconnectedAndReconnect();
    monoAndInstanceIsolation();malformedAndRateRejection();
    check(audioAllocations==0,"full RenderBatch allocated ordinary C++ new/new[] (malloc/aligned APIs not instrumented)");
    std::cout<<"Keyra full physical authored mock Reason adapter: passed; rate="<<testSampleRate<<" modes="<<KEYRA_EXPECT_FULL_STRING_MODES<<"; six groups, zero ordinary C++ audio allocations\n";
}
