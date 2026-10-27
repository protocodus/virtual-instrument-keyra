#include <cmath>
#include <cstddef>
#include <vector>

// Offline infrastructure only. Exact existing HP24 arithmetic, zero state.
extern "C" int keyra_hp24(const double* input, double* output,
                           std::size_t frames, unsigned columns, double pole) {
  if (!input || !output || !columns || !std::isfinite(pole)) return 1;
  std::vector<double> previous(columns, 0.0), state(columns, 0.0);
  for (std::size_t frame=0; frame<frames; ++frame) {
    for (unsigned ch=0; ch<columns; ++ch) {
      const auto index=frame*columns+ch;
      const double value=input[index];
      state[ch]=pole*(state[ch]+value-previous[ch]);
      previous[ch]=value;
      if (!std::isfinite(state[ch])) return 2;
      output[index]=state[ch];
    }
  }
  return 0;
}
