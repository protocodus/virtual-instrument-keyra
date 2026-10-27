#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream force(argv[1],std::ios::binary),proof(argv[2],std::ios::binary);if(!force||!proof)return 3;uint64_t badHash=0,badRow=0,badForce=0,rows=0;
for(uint64_t i=0;i<432000;++i){std::array<double,91>x{};std::array<uint64_t,3>h{};force.read((char*)x.data(),sizeof(x));proof.read((char*)h.data(),sizeof(h));if(!force||!proof)return 4;uint64_t v=14695981039346656037ull;const auto*b=(const unsigned char*)x.data();for(size_t k=0;k<sizeof(x);++k){v^=b[k];v*=1099511628211ull;}badHash+=v!=h[1]||v!=h[2];badRow+=h[0]!=i;for(size_t k=0;k<x.size();++k)badForce+=!std::isfinite(x[k])||(k<88&&x[k]<0);++rows;}char c;if(force.read(&c,1)||proof.read(&c,1))return 5;
std::cout<<"{\"rows\":"<<rows<<",\"hash_mismatches\":"<<badHash<<",\"row_mismatches\":"<<badRow<<",\"invalid_forces\":"<<badForce<<"}\n";return badHash||badRow||badForce?6:0;}
