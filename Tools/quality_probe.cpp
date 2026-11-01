// Public-engine quality observations; no fitted data, reference audio or DSP edits.
// See quality_audit.py for the frozen protocol and the distinction between
// numerical contracts and acoustic diagnostics. Metrics use latency-compensated
// output, a symmetric Hann window and a zero-padded radix-2 FFT. The padding
// refines the frequency grid; it does not increase observation resolution.
#include "DSP/KeyraEngine.h"
#include "DSP/OutputStage.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr double pi=3.14159265358979323846;
using Complex=std::complex<double>;
struct Window {double begin,end;};
struct Event {double time;std::string kind,a;double b=0;int channel=1;};
struct Case {
  std::string id;int model=0,note=60,velocity=80,rate=48000,quality=0;
  double duration=2;int repeat=0;
  keyra::Parameters p{};std::vector<Window> windows;std::vector<Event> events;
};
keyra::Parameters parameters(int model) {
  keyra::Parameters p;p.build=keyra::measuredBuild(static_cast<keyra::Piano>(model));
  p.gain=.07f;p.brightness=.5f;p.resonance=.25f;p.width=.75f;p.tuning=440;
  p.mechanics=.175f;p.mute=p.sustain=p.sostenuto=p.soft=p.mic=0;
  p.quality=keyra::Quality::full;return p;
}
void parameter(keyra::Parameters& p,const std::string& name,double v) {
  if(!std::isfinite(v))throw std::runtime_error("nonfinite parameter");
  const float x=static_cast<float>(v);
  if(name=="gain")p.gain=x;else if(name=="brightness")p.brightness=x;
  else if(name=="resonance")p.resonance=x;else if(name=="width")p.width=x;
  else if(name=="tuning")p.tuning=x;else if(name=="mechanics")p.mechanics=x;
  else if(name=="mute")p.mute=x;else if(name=="sustain")p.sustain=x;
  else if(name=="sostenuto")p.sostenuto=x;else if(name=="soft")p.soft=x;
  else if(name=="mic")p.mic=x;else if(name=="stiffness")p.build.stiffness=x;
  else if(name=="unisons")p.build.unisons=x;else if(name=="ring")p.build.ring=x;
  else if(name=="quality") {if(v!=std::floor(v)||v<0||v>2)throw std::runtime_error("quality");p.quality=static_cast<keyra::Quality>(static_cast<int>(v));}
  else {
    bool found=false;const std::array<std::string,4> names{"strings","hammers","soundboard","action"};
    const std::array<keyra::Mix*,4> parts{&p.build.strings,&p.build.hammers,&p.build.soundboard,&p.build.action};
    for(int j=0;j<4;++j)for(int i=0;i<keyra::pianoCount;++i)
      if(name==names[j]+std::to_string(i+1)){(*parts[j])[i]=x;found=true;}
    if(!found)throw std::runtime_error("unknown parameter "+name);
  }
}
void fft(std::vector<Complex>& a) {
  const std::size_t n=a.size();
  for(std::size_t i=1,j=0;i<n;++i){std::size_t bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;if(i<j)std::swap(a[i],a[j]);}
  for(std::size_t len=2;len<=n;len<<=1){const Complex step=std::polar(1.,-2*pi/static_cast<double>(len));
    for(std::size_t i=0;i<n;i+=len){Complex w=1;
      for(std::size_t j=0;j<len/2;++j){const auto u=a[i+j],v=a[i+j+len/2]*w;a[i+j]=u+v;a[i+j+len/2]=u-v;w*=step;}}}
}
struct Stat {
  std::size_t n=0,bad=0,nfft=0;double ll=0,rr=0,lr=0,diff2=0,sl=0,sr=0,peak=0,jump=0;
  std::size_t jumpAt=0;double spectral=0,centroidNumerator=0;
  std::array<double,6> relative{};std::array<double,5> absolute{};
  double bandL=0,bandR=0,bandCrossRe=0,bandCrossIm=0;
  void measure(const std::vector<float>& audio,std::size_t begin,std::size_t end,int rate,double f0) {
    n=end-begin;double pl=begin?audio[2*(begin-1)]:0,pr=begin?audio[2*(begin-1)+1]:0;
    for(std::size_t i=begin;i<end;++i){const double l=audio[2*i],r=audio[2*i+1];
      if(!std::isfinite(l)||!std::isfinite(r)){++bad;continue;}
      ll+=l*l;rr+=r*r;lr+=l*r;sl+=l;sr+=r;
      const double dl=l-pl,dr=r-pr;diff2+=dl*dl+dr*dr;const double j=std::max(std::abs(dl),std::abs(dr));
      if(j>jump){jump=j;jumpAt=i;}peak=std::max({peak,std::abs(l),std::abs(r)});pl=l;pr=r;
    }
    if(n<3||bad)return;
    nfft=1;while(nfft<n)nfft<<=1;std::vector<Complex> a(nfft);double w2=0;
    for(std::size_t i=0;i<n;++i){const double w=.5-.5*std::cos(2*pi*i/static_cast<double>(n-1));w2+=w*w;a[i]=Complex(audio[2*(begin+i)]*w,audio[2*(begin+i)+1]*w);}
    fft(a);const double norm=1./(static_cast<double>(nfft)*w2);
    const std::array<double,5> edges{.5,2,4,8,16};
    for(std::size_t k=0;k<=nfft/2;++k){const auto z=a[k],mirror=std::conj(a[(nfft-k)%nfft]);
      const auto l=.5*(z+mirror),r=Complex(0,-.5)*(z-mirror);
      const double weight=(k==0||k==nfft/2?1.:2.)*norm;
      const double el=std::norm(l)*weight,er=std::norm(r)*weight,power=.5*(el+er);
      const double hz=static_cast<double>(k)*rate/static_cast<double>(nfft);
      spectral+=power;centroidNumerator+=power*hz;std::size_t band=0;while(band<edges.size()&&hz>=edges[band]*f0)++band;relative[band]+=power;
      if(hz>=4000)absolute[0]+=power;if(hz>=8000)absolute[1]+=power;
      if(hz>=50&&hz<150)absolute[2]+=power;if(hz>=150&&hz<250)absolute[3]+=power;
      if(hz>=500&&hz<1000){absolute[4]+=power;bandL+=el;bandR+=er;const auto cross=l*std::conj(r)*weight;bandCrossRe+=cross.real();bandCrossIm+=cross.imag();}
    }
  }
  void write(std::ostream& out) const {
    out<<','<<n<<','<<bad<<','<<ll<<','<<rr<<','<<lr<<','<<diff2<<','<<sl<<','<<sr<<','<<peak<<','<<jump<<','<<jumpAt<<','<<nfft<<','<<spectral<<','<<centroidNumerator;
    for(double x:relative)out<<','<<x;for(double x:absolute)out<<','<<x;
    out<<','<<bandL<<','<<bandR<<','<<bandCrossRe<<','<<bandCrossIm;
  }
};
std::uint64_t hash(const std::vector<float>& x) {
  std::uint64_t h=14695981039346656037ull;for(float f:x){std::uint32_t bits;std::memcpy(&bits,&f,sizeof(bits));for(int i=0;i<4;++i){h^=(bits>>(i*8))&255;h*=1099511628211ull;}}return h;
}
void header(std::ostream& o) {
  o<<"case_id,model,note,velocity,rate,quality,frames,f0,whole_bad,whole_peak,hash_fnv1a64,repeat_equal,rise10_frame,rise90_frame,rise_peak_frame,rise_peak_edge";
  for(int w=0;w<6;++w){o<<",w"<<w<<"_begin,w"<<w<<"_end";
    for(const auto* n:{"n","bad","ll","rr","lr","diff2","suml","sumr","peak","jump","jump_frame","nfft","spectral_power","spectral_hz_power","f0_0_05","f0_05_2","f0_2_4","f0_4_8","f0_8_16","f0_16_up","above4000","above8000","band50_150","band150_250","band500_1000","band500_1000_l","band500_1000_r","band500_1000_cross_re","band500_1000_cross_im"})o<<",w"<<w<<'_'<<n;
  }o<<'\n';
}
bool observe(const Case& c,const std::vector<float>& audio,int repeatEqual,std::ostream& out) {
  const std::size_t frames=audio.size()/2;std::size_t bad=0;double peak=0;
  for(float x:audio)if(!std::isfinite(x))++bad;else peak=std::max(peak,std::abs(static_cast<double>(x)));
  const double f0=c.p.tuning*std::pow(2.,(c.note-69)/12.);const std::size_t count=std::min(frames,static_cast<std::size_t>(std::llround(.15*c.rate))),smooth=static_cast<std::size_t>(std::llround(.005*c.rate));
  std::vector<double> power(count);double sum=0,maximum=0;std::size_t imax=0;
  for(std::size_t i=0;i<count;++i){sum+=.5*(double(audio[2*i])*audio[2*i]+double(audio[2*i+1])*audio[2*i+1]);if(i>=smooth)sum-=.5*(double(audio[2*(i-smooth)])*audio[2*(i-smooth)]+double(audio[2*(i-smooth)+1])*audio[2*(i-smooth)+1]);power[i]=sum/static_cast<double>(smooth);if(power[i]>maximum){maximum=power[i];imax=i;}}
  long t10=-1,t90=-1;if(maximum>0&&bad==0)for(std::size_t i=0;i<count;++i){if(t10<0&&power[i]>=.01*maximum)t10=static_cast<long>(i);if(t90<0&&power[i]>=.81*maximum)t90=static_cast<long>(i);}
  out<<std::setprecision(17)<<c.id<<','<<c.model<<','<<c.note<<','<<c.velocity<<','<<c.rate<<','<<c.quality<<','<<frames<<','<<f0<<','<<bad<<','<<peak<<','<<hash(audio)<<','<<repeatEqual<<','<<t10<<','<<t90<<','<<(maximum>0?static_cast<long>(imax):-1)<<','<<(maximum>0&&imax+1==count);
  for(std::size_t w=0;w<6;++w){Stat s;const Window window=w<c.windows.size()?c.windows[w]:Window{0,0};
    const auto begin=static_cast<std::size_t>(std::llround(window.begin*c.rate)),end=static_cast<std::size_t>(std::llround(window.end*c.rate));
    if(end>frames||begin>end)throw std::runtime_error("window exceeds render");
    if(end>begin)s.measure(audio,begin,end,c.rate,f0);out<<','<<window.begin<<','<<window.end;s.write(out);
  }out<<'\n';
  return bad==0&&repeatEqual!=0&&peak<=protocodus::OutputStage<2>::kCeiling*(1.+1.e-6);
}
#ifndef KEYRA_QUALITY_METRICS_ONLY
std::vector<float> render(keyra::Engine& engine,const Case& c) {
  auto p=c.p;p.quality=static_cast<keyra::Quality>(c.quality);engine.setParameters(p);engine.setSteadyStrikesForMeasurement(false);engine.reset();
  const auto frames=static_cast<std::size_t>(std::llround(c.duration*c.rate)),latency=static_cast<std::size_t>(engine.outputLatencySamples());std::vector<float> audio(frames*2);
  std::array<float,256> l{},r{};std::size_t frame=0,next=0;
  while(frame<frames+latency){
    while(next<c.events.size()&&std::llround(c.events[next].time*c.rate)<=static_cast<long long>(frame)){
      const auto& e=c.events[next++];const int a=e.kind=="p"?0:std::stoi(e.a);
      if(e.kind=="on")engine.noteOn(a,static_cast<float>(e.b)/127.f,e.channel);
      else if(e.kind=="off")engine.noteOff(a,e.channel);else if(e.kind=="cc")engine.controlChange(a,static_cast<int>(e.b),e.channel);
      else if(e.kind=="bend")engine.pitchBend(static_cast<float>(e.b),e.channel);else if(e.kind=="reset")engine.reset();
      else if(e.kind=="p"){parameter(p,e.a,e.b);engine.setParameters(p);}else throw std::runtime_error("event kind");
    }
    auto count=std::min<std::size_t>(256,frames+latency-frame);
    if(next<c.events.size())count=std::min(count,static_cast<std::size_t>(std::max<long long>(1,std::llround(c.events[next].time*c.rate)-static_cast<long long>(frame))));
    engine.process(l.data(),r.data(),static_cast<int>(count));
    for(std::size_t i=0;i<count;++i)if(frame+i>=latency){const auto at=frame+i-latency;audio[2*at]=l[i];audio[2*at+1]=r[i];}frame+=count;
  }return audio;
}
bool execute(keyra::Engine& engine,const Case& c,std::ostream& out,const std::string& dump={}) {
  const auto x=render(engine,c);int equal=-1;if(c.repeat){const auto y=render(engine,c);equal=x.size()==y.size()&&std::memcmp(x.data(),y.data(),x.size()*sizeof(float))==0;}
  if(!dump.empty()){std::ofstream f(dump,std::ios::binary);f.write(reinterpret_cast<const char*>(x.data()),static_cast<std::streamsize>(x.size()*sizeof(float)));if(!f)throw std::runtime_error("dump write");}
  return observe(c,x,equal,out);
}
int grid(int argc,char** argv) {
  if(argc!=10)throw std::runtime_error("--grid MODEL CSV LOW HIGH VLOW VHIGH DURATION RELEASE");
  const int model=std::stoi(argv[2]),low=std::stoi(argv[4]),high=std::stoi(argv[5]),vlow=std::stoi(argv[6]),vhigh=std::stoi(argv[7]);
  if(model<0||model>=6||low<21||high>108||low>high||vlow<1||vhigh>127||vlow>vhigh)throw std::runtime_error("grid range");
  const double duration=std::stod(argv[8]),release=std::stod(argv[9]);if(duration<2||release!=1.5)throw std::runtime_error("v1 grid duration/release");
  std::ofstream out(argv[3]);if(!out)throw std::runtime_error("csv open");header(out);keyra::Engine engine(48000);bool pass=true;
  for(int note=low;note<=high;++note){for(int velocity=vlow;velocity<=vhigh;++velocity){Case c;c.id="g_"+std::to_string(model)+"_"+std::to_string(note)+"_"+std::to_string(velocity);c.model=model;c.note=note;c.velocity=velocity;c.duration=duration;c.p=parameters(model);c.repeat=note==low&&velocity==vlow;
    c.windows={{0,.05},{.05,.3},{.3,.75},{.75,1.5},{1.5,2}};c.events={{0,"on",std::to_string(note),double(velocity),1},{release,"off",std::to_string(note),0,1}};pass=execute(engine,c,out)&&pass;
  }out.flush();std::cerr<<model<<' '<<note<<'\n';}return pass?0:3;
}
int cases(int argc,char** argv) {
  if(argc<4||argc>5)throw std::runtime_error("--cases SPEC CSV [DUMP_SINGLE_F32]");std::ifstream input(argv[2]);std::ofstream out(argv[3]);if(!input||!out)throw std::runtime_error("case file");header(out);
  Case c;std::string line;bool open=false,pass=true;int rate=0,count=0;std::unique_ptr<keyra::Engine> engine;
  while(std::getline(input,line)){if(line.empty()||line[0]=='#')continue;std::istringstream row(line);std::string kind;row>>kind;
    if(kind=="case"){if(open)throw std::runtime_error("nested case");c=Case{};row>>c.id>>c.model>>c.note>>c.velocity>>c.rate>>c.quality>>c.duration>>c.repeat;
      if(!row||c.model<0||c.model>=6)throw std::runtime_error("case model");c.p=parameters(c.model);open=true;}
    else if(kind=="p"){if(!open)throw std::runtime_error("parameter outside case");std::string name;double v;row>>name>>v;if(!row)throw std::runtime_error("parameter fields");parameter(c.p,name,v);}
    else if(kind=="w"){if(!open)throw std::runtime_error("window outside case");Window w;row>>w.begin>>w.end;c.windows.push_back(w);}
    else if(kind=="e"){if(!open)throw std::runtime_error("event outside case");Event e;row>>e.time>>e.kind>>e.a>>e.b>>e.channel;c.events.push_back(e);}
    else if(kind=="end"){if(!open||c.note<21||c.note>108||c.velocity<1||c.velocity>127||c.quality<0||c.quality>2||c.rate<8000||c.rate>192000||!std::isfinite(c.duration)||c.duration<=0||c.windows.empty()||c.windows.size()>6)throw std::runtime_error("invalid case");
      for(const auto& w:c.windows)if(!std::isfinite(w.begin)||!std::isfinite(w.end)||w.begin<0||w.end<=w.begin||w.end>c.duration)throw std::runtime_error("invalid observation window");
      for(const auto& e:c.events){if(!std::isfinite(e.time)||!std::isfinite(e.b)||e.time<0||e.time>=c.duration||e.channel<1||e.channel>16)throw std::runtime_error("invalid event");
        if(e.kind=="on"||e.kind=="off"||e.kind=="cc"){const int a=std::stoi(e.a);if(a<0||a>127||e.b<0||e.b>127)throw std::runtime_error("invalid MIDI event");}}
      if(argc==5&&count!=0)throw std::runtime_error("dump mode accepts one case only");
      std::stable_sort(c.events.begin(),c.events.end(),[](const Event& a,const Event& b){return a.time<b.time;});
      if(!engine||rate!=c.rate){engine=std::make_unique<keyra::Engine>(c.rate);rate=c.rate;}
      pass=execute(*engine,c,out,argc==5?argv[4]:"")&&pass;open=false;++count;out.flush();
    }else throw std::runtime_error("unknown line "+line);
    if(!row)throw std::runtime_error("invalid line "+line);
  }if(open||count==0||(argc==5&&count!=1))throw std::runtime_error("case count");return pass?0:3;
}
#endif
int analyze(int argc,char** argv) {
  if(argc!=7)throw std::runtime_error("--analyze RAW CSV RATE NOTE SECONDS");Case c;c.id="analysis";c.rate=std::stoi(argv[4]);c.note=std::stoi(argv[5]);c.duration=std::stod(argv[6]);c.p=parameters(0);c.windows={{0,c.duration}};
  std::ifstream input(argv[2],std::ios::binary|std::ios::ate);if(!input)throw std::runtime_error("raw input");const auto bytes=input.tellg();if(bytes<0||bytes%8!=0)throw std::runtime_error("raw stereo frames");std::vector<float> x(static_cast<std::size_t>(bytes)/sizeof(float));input.seekg(0);input.read(reinterpret_cast<char*>(x.data()),bytes);if(!input)throw std::runtime_error("raw read");std::ofstream out(argv[3]);header(out);observe(c,x,-1,out);return 0;
}
} // namespace
int main(int argc,char** argv) {try {
  if(argc<2)throw std::runtime_error("mode required");const std::string mode=argv[1];
  if(mode=="--analyze")return analyze(argc,argv);
#ifndef KEYRA_QUALITY_METRICS_ONLY
  if(mode=="--grid")return grid(argc,argv);if(mode=="--cases")return cases(argc,argv);
#endif
  throw std::runtime_error("unknown mode");
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}}
