#include <cmath>
#include <cstddef>

// Streaming postprocessor only. All state persists across arbitrary blocks.
// No piano state, source force, gain, onset or microphone channel is changed.
extern "C" int keyra_protect_counter(const double* old, const double* fast,
  double* out, std::size_t frames, double* state) {
  const double pi=std::acos(-1.0), k=std::tan(pi*200/48000);
  const double a=(1-k)/(1+k),b=1/(1+k),pole=std::exp(-2*pi*24/48000);
  for(std::size_t n=0;n<frames;++n)for(int ch=0;ch<2;++ch){
    const double x=old[2*n+ch],z=fast[2*n+ch];
    state[ch]=a*state[ch]+b*(z-state[2+ch]);state[2+ch]=z;
    const double h=state[ch],candidate=x-h;
    state[4+ch]=pole*(state[4+ch]+x-state[6+ch]);state[6+ch]=x;
    state[8+ch]=pole*(state[8+ch]+candidate-state[10+ch]);state[10+ch]=candidate;
    state[12+ch]=pole*(state[12+ch]+h-state[14+ch]);state[14+ch]=h;
    out[10*n+ch]=h;out[10*n+2+ch]=state[4+ch];out[10*n+4+ch]=state[8+ch];out[10*n+6+ch]=state[12+ch];out[10*n+8+ch]=candidate;
    if(!std::isfinite(x)||!std::isfinite(z)||!std::isfinite(h)||!std::isfinite(candidate)||!std::isfinite(state[8+ch]))return 1;
  }
  return 0;
}
