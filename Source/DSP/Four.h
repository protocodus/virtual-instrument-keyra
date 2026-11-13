#pragma once
// Four floats abreast. The plug-in's compilers take a plain loop four floats
// at a time on their own; Reason's (the Jukebox SDK's) takes it one at a time
// unless the source says four, and a sounding piano cost about twice there
// what it costs here. Each lane does what the one-float loop did, in its
// order, so the sound is the same to the bit.
//
// Packed, and aligned as a float is: the Rack's allocator promises 8 bytes,
// and a member that asks for 16 is read there with an instruction that faults
// off a 16-byte boundary on x86 (Retra 0.7.0f1 on Reason's servers,
// 2026-11-11; never on arm64 or under Rosetta, so a Mac does not show it).
// A typedef with a lowered alignment is forgotten behind a reference by the
// SDK's Clang 15, so it is a struct. Nothing in the engine asks the heap for
// more than a double's alignment.
namespace keyra {
#if (defined(__clang__) || defined(__GNUC__)) && !defined(KEYRA_FORCE_SCALAR)
struct Four {
  typedef float Lanes __attribute__((vector_size(16)));
  Lanes v;
  static Four all(float x) noexcept {return {Lanes{x,x,x,x}};}
  static Four at(const float* p) noexcept {Four f;__builtin_memcpy(&f,p,sizeof(f));return f;}
  void to(float* p) const noexcept {__builtin_memcpy(p,this,sizeof(*this));}
  float operator[](int lane) const noexcept {return v[lane];}
  void set(int lane,float x) noexcept {Lanes w=v;w[lane]=x;v=w;}
  Four operator+(Four o) const noexcept {return {v+o.v};}
  Four operator-(Four o) const noexcept {return {v-o.v};}
  Four operator*(Four o) const noexcept {return {v*o.v};}
  Four& operator+=(Four o) noexcept {v=v+o.v;return *this;}
} __attribute__((packed,aligned(4)));
#else
struct Four {
  float v[4];
  static Four all(float x) noexcept {return {{x,x,x,x}};}
  static Four at(const float* p) noexcept {return {{p[0],p[1],p[2],p[3]}};}
  void to(float* p) const noexcept {p[0]=v[0];p[1]=v[1];p[2]=v[2];p[3]=v[3];}
  float operator[](int lane) const noexcept {return v[lane];}
  void set(int lane,float x) noexcept {v[lane]=x;}
  Four operator+(Four o) const noexcept {return {{v[0]+o.v[0],v[1]+o.v[1],v[2]+o.v[2],v[3]+o.v[3]}};}
  Four operator-(Four o) const noexcept {return {{v[0]-o.v[0],v[1]-o.v[1],v[2]-o.v[2],v[3]-o.v[3]}};}
  Four operator*(Four o) const noexcept {return {{v[0]*o.v[0],v[1]*o.v[1],v[2]*o.v[2],v[3]*o.v[3]}};}
  Four& operator+=(Four o) noexcept {*this=*this+o;return *this;}
};
#endif
// The numbers, not alignof(float): the SDK also builds for targets where a
// double is aligned to 4.
static_assert(alignof(Four)==4&&sizeof(Four)==16,"four floats, aligned as one");
}
