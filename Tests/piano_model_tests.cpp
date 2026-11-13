// The physical model's own contracts (PianoModel.h), below the engine: what
// a key is built as, the stiff strings' partials, the hammer's blow, the
// knocks under a note, the strings' decay, the dampers, the open strings and
// the bridge. The keys, pedals and controls as a front end meets them are in
// engine_tests.cpp.
#include "DSP/PianoModel.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
#include <vector>

namespace {
using keyra::model::Body;using keyra::model::Controls;using keyra::model::Piano;
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
constexpr double pi=3.14159265358979323846,rate=48000;
struct Take {
  std::vector<float> left,right;
  std::size_t at(double seconds) const {return std::min(left.size(),static_cast<std::size_t>(std::lround(seconds*rate)));}
  // RMS level of both channels over a span, dB re 1 Pa.
  double db(double from,double to) const {
    double sum=0;const std::size_t a=at(from),b=at(to);
    for(std::size_t i=a;i<b;++i)sum+=static_cast<double>(left[i])*left[i]+static_cast<double>(right[i])*right[i];
    return 10*std::log10(sum/std::max<std::size_t>(1,2*(b-a))+1e-30);
  }
  // The level of one frequency in the left channel over a span (Hann window), dB.
  double tone(double hz,double from,double to) const {
    const std::size_t a=at(from),n=at(to)-a;double re=0,im=0;
    for(std::size_t i=0;i<n;++i){const double x=left[a+i]*(.5-.5*std::cos(2*pi*i/(n-1))),w=2*pi*hz*i/rate;
      re+=x*std::cos(w);im+=x*std::sin(w);}
    return 20*std::log10(4*std::hypot(re,im)/n+1e-15);
  }
  // The strongest frequency within `cents` of `hz`, to a tenth of a cent.
  double pitch(double hz,double from,double to,double cents=40) const {
    double best=hz,top=-400;
    for(double step:{4.,.4,.1}){const double centre=best,span=step==4.?cents:step*10;
      for(double c=-span;c<=span;c+=step){const double f=centre*std::pow(2.,c/1200),level=tone(f,from,to);
        if(level>top){top=level;best=f;}}}
    return best;
  }
  // The share of a span's power above `hz` (a first difference twice over
  // would do for a tone; a piano's spectrum needs a real high-pass:
  // fourth-order Butterworth, two state-variable sections), dB.
  double above(double hz,double from,double to) const {
    const double g=std::tan(pi*hz/rate);double high=0,all=0;
    for(const auto* channel:{&left,&right}){double state[2][2]{};
      for(std::size_t i=at(from);i<at(to);++i){double x=(*channel)[i];all+=x*x;
        for(int stage=0;stage<2;++stage){const double r=stage?.765367:1.847759;double* s=state[stage];
          const double hp=(x-(r+g)*s[0]-s[1])/(1+r*g+g*g),bp=g*hp+s[0],lp=g*bp+s[1];
          s[0]=g*hp+bp;s[1]=g*bp+lp;x=hp;}
        high+=x*x;}}
    return 10*std::log10((high+1e-30)/(all+1e-30));
  }
  bool finite() const {return std::all_of(left.begin(),left.end(),[](float x){return std::isfinite(x);})
                             &&std::all_of(right.begin(),right.end(),[](float x){return std::isfinite(x);});}
};
// One piano, designed once: prepare() builds every body.
struct Bench {
  Piano piano;Take take;
  Bench(){piano.prepare(rate);}
  void start(const Controls& controls){piano.setControls(controls);piano.reset();take=Take{};}
  void run(double seconds){
    std::array<float,256> l{},r{};int left=static_cast<int>(std::lround(seconds*rate));
    while(left>0){const int n=std::min(256,left);piano.process(l.data(),r.data(),n);
      take.left.insert(take.left.end(),l.begin(),l.begin()+n);take.right.insert(take.right.end(),r.begin(),r.begin()+n);left-=n;}
  }
  double now() const {return take.left.size()/rate;}
};
// The strings alone: no room, no open strings or duplex scales to answer.
Controls bare(){Controls c;c.room=0;c.sympathetic=0;c.duplex=0;return c;}
int keyOf(int midi){return midi-21;}
}

int main(){
  auto bench=std::make_unique<Bench>();auto& b=*bench;auto& piano=b.piano;
  {
    // What each piano's keys are built as.
    for(int body=0;body<keyra::model::bodyCount;++body){
      bool ordered=true,built=true;
      for(int key=0;key<keyra::model::keyCount;++key){const auto k=piano.report(static_cast<Body>(body),key);
        built=built&&k.strings>=1&&k.strings<=3&&k.partials>=1&&k.length>.04&&k.length<2.8&&k.tension>200&&k.tension<2500
              &&k.inharmonicity>0&&k.inharmonicity<.05&&k.hammerMass>.0015&&k.hammerMass<.012;
        if(key){const auto under=piano.report(static_cast<Body>(body),key-1);
          ordered=ordered&&k.hertz>under.hertz&&k.length<=under.length&&k.strings>=under.strings&&k.hammerMass<=under.hammerMass;}
      }
      const auto a0=piano.report(static_cast<Body>(body),0),a4=piano.report(static_cast<Body>(body),48),c8=piano.report(static_cast<Body>(body),87);
      std::cout<<"body "<<body<<": A0 "<<a0.length<<" m, "<<a0.tension<<" N, B "<<a0.inharmonicity<<", "<<a0.partials<<" partials; A4 "
               <<a4.length<<" m, "<<a4.tension<<" N, B "<<a4.inharmonicity<<"; C8 "<<c8.length<<" m, B "<<c8.inharmonicity
               <<", stretch "<<a0.stretchCents<<" to "<<c8.stretchCents<<" cents\n";
      check(built,"every key is a piano's: one to three strings of a piano's length and tension, a hammer of a piano's weight");
      check(ordered,"up the keyboard the strings shorten, the unisons grow and the hammers lighten");
      check(a0.strings==1&&a4.strings==3&&c8.strings==3,"the lowest key has one string and the middle and top three");
      check(c8.inharmonicity>10*a4.inharmonicity,"the short treble strings are the stiffest");
      check(std::abs(a4.stretchCents)<.01&&c8.stretchCents>5&&a0.stretchCents<-2,"the tuner's stretch flattens the bass and sharpens the treble from A4");
    }
    // A longer piano's bass strings are longer, and less inharmonic.
    const auto concert=piano.report(Body::concertGrand,3),baby=piano.report(Body::babyGrand,3),upright=piano.report(Body::upright,3);
    check(concert.length>baby.length&&concert.inharmonicity<baby.inharmonicity&&concert.length>upright.length,
          "the concert grand's bass strings are the longest and the least stiff");
  }
  {
    // A stiff string's partials: n f1 sqrt((1 + B n^2) / (1 + B)). A wound
    // string's stray from it on purpose, 1.5 cents for one deviation each
    // (KeyData::stray): C2's are held within twice that, the plain strings'
    // to the law. (Reading a plain string's partials here strays 1.3 cents
    // rms of itself.)
    for(const int midi:{36,60,84}){
      Controls c=bare();c.detune=0;c.stretch=0;b.start(c);piano.strike(keyOf(midi),.6f);piano.holdDamper(keyOf(midi),true);b.run(1.5);
      const auto k=piano.report(Body::concertGrand,keyOf(midi));
      // The strike's own sound: in the treble the aftersound, which the
      // bridge does not move, takes over within half a second, a few cents
      // under it.
      const double to=midi<72?1.5:.4;
      const double f1=b.take.pitch(440*std::pow(2.,(midi-69)/12.),.03,to);
      double worst=0,square=0;int heard=0;
      for(int n=2;n<=std::min(12,k.partials);++n){
        const double expected=n*f1*std::sqrt((1+k.inharmonicity*n*n)/(1+k.inharmonicity));
        if(expected>.4*rate)break;
        const double f=b.take.pitch(expected,.03,to,25);
        // A partial the hammer's place on the string leaves out is not there to read.
        if(b.take.tone(f,.03,to)<b.take.tone(f1,.03,to)-55)continue;
        const double cents=1200*std::log2(f/expected);
        worst=std::max(worst,std::abs(cents));square+=cents*cents;++heard;
      }
      const double rms=std::sqrt(square/std::max(1,heard));
      std::cout<<"MIDI "<<midi<<": first partial "<<f1<<" Hz, B "<<k.inharmonicity<<", "<<heard<<" partials within "<<worst<<" cents of the stiff string's, "<<rms<<" rms\n";
      check(std::abs(1200*std::log2(f1/(440*std::pow(2.,(midi-69)/12.))))<1.5,"without stretch a key's first partial is equal-tempered");
      if(midi<41)check(heard>=3&&rms<3,"a wound string's partials stray about a stiff string's");
      else check(heard>=3&&worst<3,"the partials are a stiff string's");
    }
  }
  {
    // The hammer: a harder blow is louder, and brighter, since the felt
    // stiffens as it is pressed.
    double level[5],bright[5];const float velocity[5]{.1f,.3f,.5f,.75f,1};
    Controls c=bare();
    for(int i=0;i<5;++i){b.start(c);piano.holdDamper(keyOf(60),true);piano.strike(keyOf(60),velocity[i]);b.run(.5);
      level[i]=b.take.db(.01,.4);bright[i]=b.take.above(2000,.01,.4);}
    std::cout<<"C4 by velocity:";for(int i=0;i<5;++i)std::cout<<' '<<velocity[i]<<": "<<level[i]<<" dB, above 2 kHz "<<bright[i]<<" dB;";std::cout<<'\n';
    bool louder=true,brighter=true;for(int i=1;i<5;++i){louder=louder&&level[i]>level[i-1]+1;brighter=brighter&&bright[i]>bright[i-1]+.5;}
    check(louder,"a harder blow is louder");
    check(brighter&&bright[4]>bright[0]+8,"a harder blow is brighter");
    // The same blow on the same piano is the same sound.
    b.start(c);piano.strike(keyOf(60),.5f);b.run(.2);const Take once=b.take;
    b.start(c);piano.strike(keyOf(60),.5f);b.run(.2);
    check(once.left==b.take.left&&once.right==b.take.right,"a blow repeats exactly after a reset");
    // No blow at all plays nothing, and the limits of a blow are bounded.
    b.start(c);piano.strike(keyOf(60),0);piano.strike(-1,.8f);piano.strike(88,.8f);b.run(.1);
    check(b.take.db(0,.1)<-250,"no velocity, or a key off the keyboard, plays nothing");
    b.start(c);for(const float v:{2.f,-1.f,1e9f})piano.strike(keyOf(48),v);b.run(.2);
    check(b.take.finite()&&b.take.db(0,.2)<60,"a blow outside 0 to 1 is bounded");
    // A string struck again while it rings takes the new blow on top.
    b.start(c);piano.holdDamper(keyOf(48),true);
    for(int k=0;k<12;++k){piano.strike(keyOf(48),.9f);b.run(.08);}
    check(b.take.finite()&&b.take.db(.88,.96)<b.take.db(0,.08)+12,"a repeated key stays a piano's");
  }
  {
    // The two knocks under a note. What a span holds under `hz`, dB re 1 Pa.
    const auto under=[&](double hz,double from,double to){
      return b.take.db(from,to)+10*std::log10(std::max(1e-30,1-std::pow(10.,b.take.above(hz,from,to)/10)));};
    Controls c=bare();
    // The thump: the action catches the hammer well after the blow, later
    // the softer it was. When what C7 holds under 120 Hz (four one-pole
    // low-passes, which the knock above 180 Hz does not pass) peaks, ms.
    const auto thump=[&](float velocity){b.start(c);piano.strike(keyOf(96),velocity);b.run(.1);
      const double pole=1-std::exp(-2*pi*120/rate);double state[4]{},most=0;std::size_t at=0;
      for(std::size_t i=0;i<b.take.left.size();++i){double x=b.take.left[i]+b.take.right[i];
        for(double& z:state){z+=pole*(x-z);x=z;}
        if(std::abs(x)>most){most=std::abs(x);at=i;}}
      return 1000.*static_cast<double>(at)/rate;};
    const double hard=thump(.9f),soft=thump(.25f);
    std::cout<<"under 120 Hz C7 peaks "<<hard<<" ms after a forte blow, "<<soft<<" ms after a piano one\n";
    check(hard>12,"the thump comes after the blow");
    check(soft>hard+3,"and later after a soft one");
    // The knock: a top key's blow leans on the capo bar and is heard at
    // once; a bass key's strings end on agraffes, and nothing is heard of it
    // before the strings' own sound has reached the bridge.
    b.start(c);piano.strike(keyOf(102),.6f);b.run(.1);
    const double knock=under(1500,0,.006)-b.take.db(.01,.1);
    b.start(c);piano.strike(keyOf(24),.6f);b.run(.2);
    const double before=b.take.db(0,.004)-b.take.db(.02,.2);
    std::cout<<"under 1.5 kHz in its first 6 ms F#7 holds "<<knock<<" dB re the note; C1's first 4 ms hold "<<before<<" dB re the note\n";
    check(knock>-12,"a top key's blow knocks");
    // No knock reaches C1 (knockArm is nil below capoFrom), so what these
    // 4 ms hold is the strings' own modes summed before their wave has
    // reached the bridge: 50.4 dB under the note in 2.10.0, 49.98 with the
    // wound strings' stray as drawn and 51.7 under another draw of it. A
    // knock stands tens of dB higher (F#7's, above, 3 dB under its note).
    check(before<-48,"nothing precedes a bass string");
    // No two catches are alike once a strike carries its chance, and the
    // same chance is the same catch.
    const auto caught=[&](std::uint32_t chance){b.start(c);piano.strike(keyOf(96),.6f,0,chance);b.run(.1);return b.take;};
    const Take one=caught(1),two=caught(2),oneAgain=caught(1);
    check(one.left==oneAgain.left,"a strike's chance repeats exactly");
    check(one.left!=two.left&&std::abs(one.db(0,.1)-two.db(0,.1))<1.5,"another chance is another catch of the same note");
    // The top strings, which the bridge holds hardest, only lose energy.
    for(const float soundboard:{0.f,1.f}){Controls d;d.soundboard=soundboard;b.start(d);piano.setPedal(1);
      for(int key=76;key<keyra::model::keyCount;++key)piano.strike(key,1);
      b.run(4);
      bool falling=true;for(double t=.5;t<3.5;t+=.5)falling=falling&&b.take.db(t+.5,t+1)<b.take.db(t,t+.5)+.5;
      check(b.take.finite()&&falling,"the top octave rings down at either end of Soundboard");}
  }
  {
    // The strings lose their energy and gain none: once the blow is over a
    // key's level only falls, a unison's faster at first (its strings move
    // the bridge together) than later (they have fallen out of step, and
    // the sideways motion the bridge hardly takes is what is left).
    Controls c=bare();b.start(c);piano.holdDamper(keyOf(60),true);piano.strike(keyOf(60),.7f);b.run(8);
    double early=(b.take.db(.1,.3)-b.take.db(.9,1.1))/.8,late=(b.take.db(4,4.5)-b.take.db(7,7.5))/3;
    std::cout<<"C4 falls "<<early<<" dB/s at first, "<<late<<" dB/s after four seconds\n";
    check(early>1.4*late&&late>.5,"a unison decays twice: fast, then slowly");
    // Higher partials die sooner, so the sound darkens as it rings.
    check(b.take.above(2000,3,4)<b.take.above(2000,.05,.5)-6,"the upper partials die first");
    // Strings out of tune with each other beat, and a microphone hears the
    // beat swell; tuned pure, what it hears only falls.
    c.detune=0;b.start(c);piano.holdDamper(keyOf(60),true);piano.strike(keyOf(60),.7f);b.run(8);
    bool falling=true;
    for(double t=.5;t<7;t+=.5){falling=falling&&b.take.db(t+.5,t+1)<b.take.db(t,t+.5)+.5;}
    check(falling,"a ringing key gains no energy");
    c.detune=.3f;
    // The bass rings longer than the treble.
    const auto fall=[&](int midi){b.start(c);piano.holdDamper(keyOf(midi),true);piano.strike(keyOf(midi),.7f);b.run(3);
      return (b.take.db(.2,.6)-b.take.db(2.4,2.8))/2.2;};
    const double low=fall(33),middle=fall(60),high=fall(96);
    std::cout<<"decay: A1 "<<low<<" dB/s, C4 "<<middle<<" dB/s, C7 "<<high<<" dB/s\n";
    check(low<middle&&middle<high,"the bass rings longer than the treble");
  }
  {
    // The damper: off while the key is held, and when it falls the strings
    // stop, the bass's heavier strings more slowly.
    const auto stop=[&](int midi){Controls c=bare();b.start(c);piano.holdDamper(keyOf(midi),true);piano.strike(keyOf(midi),.7f);b.run(.5);
      piano.holdDamper(keyOf(midi),false);b.run(.6);return b.take.db(.3,.5)-b.take.db(.9,1.1);};
    const double bass=stop(33),middle=stop(60);
    std::cout<<"the damper takes "<<bass<<" dB from A1 and "<<middle<<" dB from C4 in half a second\n";
    check(middle>40&&bass>20,"a fallen damper stops its strings");
    check(bass<middle,"the bass's strings take longer to stop");
    // Above the last damper a key rings whether held or not.
    Controls c=bare();b.start(c);piano.strike(keyOf(100),.7f);b.run(.5);const Take let=b.take;
    b.start(c);piano.holdDamper(keyOf(100),true);piano.strike(keyOf(100),.7f);b.run(.5);
    check(let.left==b.take.left,"the top keys have no dampers");
    // The pedal lifts every damper.
    b.start(c);piano.setPedal(1);piano.strike(keyOf(60),.7f);b.run(.5);piano.holdDamper(keyOf(60),false);b.run(.5);
    // C4's own first fall is 17 dB a second, so 8.5 dB over this half second.
    check(b.take.db(.8,1)>b.take.db(.3,.5)-12,"the pedal holds the dampers off");
    piano.setPedal(0);b.run(.5);
    check(b.take.db(1.3,1.5)<b.take.db(.8,1)-40,"and lets them fall");
  }
  {
    // The open strings answer through the bridge: a key held down silently
    // rings at the partials it shares with a struck one, and only then.
    const auto answer=[&](bool held,float sympathetic){Controls c;c.room=0;c.duplex=0;c.sympathetic=sympathetic;b.start(c);
      if(held)piano.holdDamper(keyOf(48),true);
      piano.holdDamper(keyOf(60),true);piano.strike(keyOf(60),.9f);b.run(.3);piano.holdDamper(keyOf(60),false);b.run(1.2);
      const double f=b.take.pitch(261.63,.7,1.5,30);return b.take.tone(f,.7,1.5);};
    const double alone=answer(false,.5f),with=answer(true,.5f),off=answer(true,0),more=answer(true,1);
    std::cout<<"after a staccato C4, its pitch rings on at "<<alone<<" dB; with C3 held "<<with<<" dB, Sympathetic 0 "<<off<<" dB, 1 "<<more<<" dB\n";
    check(with>alone+20,"a held key's strings answer a struck one");
    check(off<with-20&&more>with+3,"Sympathetic sets how strongly");
  }
  {
    // The bridge and the board: a knock on the bridge is the soundboard's
    // own sound, with no string in it, and it dies in a moment.
    Controls c=bare();b.start(c);
    check(piano.silent(),"a piano at rest is silent");
    b.run(.05);check(b.take.db(0,.05)<-250,"and plays nothing");
    piano.knockBridge(keyOf(48),.01f);check(!piano.silent(),"a knock wakes it");
    b.run(1.5);
    std::cout<<"a 10 mN s knock on the bridge: "<<b.take.db(.05,.1)<<" dB, after a second "<<b.take.db(1.05,1.55)<<" dB\n";
    check(b.take.db(.05,.1)>-60&&b.take.db(1.05,1.55)<b.take.db(.05,.1)-50,"the soundboard answers a knock and falls still");
    // Livelier, it rings longer.
    const auto ring=[&](float soundboard){Controls d=bare();d.soundboard=soundboard;b.start(d);piano.knockBridge(keyOf(48),.01f);b.run(.5);
      return b.take.db(.2,.4)-b.take.db(0,.05);};
    check(ring(1)>ring(0)+6,"a livelier soundboard rings longer");
    // Let go, a key falls silent and the piano sleeps: exactly nothing.
    b.start(c);piano.holdDamper(keyOf(60),true);piano.strike(keyOf(60),.8f);b.run(.3);piano.holdDamper(keyOf(60),false);
    double asleep=-1;for(int k=0;k<120&&asleep<0;++k){b.run(.5);if(piano.silent())asleep=b.now();}
    std::cout<<"a staccato C4 leaves the piano asleep after "<<asleep<<" s\n";
    check(asleep>0,"the piano sleeps once a note has died");
    const double t=b.now();b.run(.1);
    bool nothing=true;for(std::size_t i=b.take.at(t);i<b.take.left.size();++i)nothing=nothing&&b.take.left[i]==0&&b.take.right[i]==0;
    check(nothing,"asleep, it writes exact silence");
  }
  {
    // Every key at once, again and again: more than the voices there are.
    Controls c;b.start(c);piano.setPedal(1);
    for(int round=0;round<3;++round){for(int key=0;key<keyra::model::keyCount;++key)piano.strike(key,1);b.run(.1);}
    check(b.take.finite()&&b.take.db(0,.3)<60,"every key at once stays bounded");
    // The bend and the tuning move what sounds.
    b.start(bare());piano.holdDamper(keyOf(69),true);piano.strike(keyOf(69),.6f);b.run(.6);piano.setBend(1);b.run(1);
    check(std::abs(1200*std::log2(b.take.pitch(440*std::pow(2.,1/12.),.9,1.6)/440)-100)<3,"the bend moves sounding strings");
    // And how strongly the open strings and the duplex scales answer, which
    // the plug-in's reach test cannot hear under its chord: turned up half a
    // second into a note, they answer what is left of it (the difference
    // from the note left alone: -15.5 dB of C3 and -28.4 dB of C6 as built).
    const auto answering=[&](int midi,bool duplex,float later){Controls c=bare();b.start(c);piano.setPedal(1);piano.strike(keyOf(midi),.9f);b.run(.5);
      (duplex?c.duplex:c.sympathetic)=later;piano.setControls(c);b.run(1);return b.take;};
    const auto apart=[&](const Take& plain,const Take& other){double sum=0,all=0;
      for(std::size_t i=plain.at(.6);i<plain.left.size();++i){const double d=other.left[i]-plain.left[i];sum+=d*d;all+=static_cast<double>(plain.left[i])*plain.left[i];}
      return 10*std::log10((sum+1e-30)/(all+1e-30));};
    const Take plain=answering(48,false,0),open=answering(48,false,1),high=answering(84,true,0),sheen=answering(84,true,1);
    std::cout<<"turned up at 0.5 s: the open strings "<<apart(plain,open)<<" dB of C3, the duplex scales "<<apart(high,sheen)<<" dB of C6\n";
    check(apart(plain,open)>-21,"Sympathetic reaches a sounding note");
    check(apart(high,sheen)>-34,"Duplex reaches a sounding note");
    // Another sample rate is the same piano.
    piano.prepare(96000);
    Controls d=bare();piano.setControls(d);piano.reset();piano.holdDamper(keyOf(69),true);piano.strike(keyOf(69),.6f);
    std::vector<float> l(96000),r(96000);piano.process(l.data(),r.data(),96000);
    double re=0,im=0;for(int i=0;i<96000;++i){const double w=2*pi*440.*i/96000;re+=l[i]*std::cos(w);im+=l[i]*std::sin(w);}
    piano.prepare(rate);piano.setControls(d);piano.reset();piano.holdDamper(keyOf(69),true);piano.strike(keyOf(69),.6f);
    std::vector<float> l48(48000),r48(48000);piano.process(l48.data(),r48.data(),48000);
    double re48=0,im48=0;for(int i=0;i<48000;++i){const double w=2*pi*440.*i/48000;re48+=l48[i]*std::cos(w);im48+=l48[i]*std::sin(w);}
    const double difference=20*std::log10(std::hypot(re,im)/96000/(std::hypot(re48,im48)/48000));
    std::cout<<"A4's first partial at 96 kHz against 48 kHz: "<<difference<<" dB\n";
    check(std::abs(difference)<1,"the sample rate does not change the piano");
  }
  std::cout<<"piano_model_failures="<<failures<<'\n';
  return failures?1:0;
}
