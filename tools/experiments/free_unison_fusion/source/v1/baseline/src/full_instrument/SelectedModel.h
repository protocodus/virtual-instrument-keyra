#pragma once
// Build-time engineering profile. No runtime model/recording loading or UI control.
#ifndef KEYRA_FULL_MODEL_PROFILE
#define KEYRA_FULL_MODEL_PROFILE 0
#endif
#if KEYRA_FULL_MODEL_PROFILE == 0
#include "PreparedModel.h"
#elif KEYRA_FULL_MODEL_PROFILE == 1
#include "profiles/confidence_grand/PreparedModel.h"
#else
#error Unsupported KEYRA_FULL_MODEL_PROFILE: use0 OriginalControl or1 FrozenConfidenceGrand
#endif
