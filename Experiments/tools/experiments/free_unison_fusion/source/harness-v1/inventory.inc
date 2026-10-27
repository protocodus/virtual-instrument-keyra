#include <cstdio>
extern "C" bool keyra_fusion_prepare_report(const keyra::FullInstrument* piano,const char* path) {
  if(!piano||!piano->impl_||!piano->impl_->model)return false;
  const auto& model=*piano->impl_->model;
  if(model.modeCount()!=17778||model.strings.size()!=230||model.board.size()!=475)return false;
  FILE* file=std::fopen(path,"wb");if(!file)return false;
#if KEYRA_FUSION_CANDIDATE
  const auto& i=model.freeUnisonInventory;
  const bool valid=i.valid&&i.modeCount==17778&&i.fusedModes+i.fallbackModes==i.modeCount&&i.originalRows==i.scheduledRows&&i.keysOwned==88&&i.stringsOwned==230&&i.uniqueModeUpdates&&i.uniqueRowMembership&&i.originalGroupedRowsExact;
  std::fprintf(file,"{\"candidate\":true,\"valid\":%s,\"mode_count\":%zu,\"fused_modes\":%zu,\"fallback_modes\":%zu,\"original_rows\":%zu,\"scheduled_rows\":%zu,\"group_count\":%zu,\"keys_owned\":%zu,\"strings_owned\":%zu,\"unique_mode_updates\":%s,\"unique_row_membership\":%s,\"original_grouped_rows_exact\":%s,\"added_cache_bytes\":%zu}\n",valid?"true":"false",size_t(i.modeCount),size_t(i.fusedModes),size_t(i.fallbackModes),size_t(i.originalRows),size_t(i.scheduledRows),size_t(i.groupCount),size_t(i.keysOwned),size_t(i.stringsOwned),i.uniqueModeUpdates?"true":"false",i.uniqueRowMembership?"true":"false",i.originalGroupedRowsExact?"true":"false",model.freeUnisonExtraBytes());
  const bool closed=std::fclose(file)==0;return valid&&closed;
#else
  std::fprintf(file,"{\"candidate\":false,\"valid\":true,\"mode_count\":%zu,\"strings\":%zu,\"board_modes\":%zu,\"group_count\":%zu}\n",model.modeCount(),model.strings.size(),model.board.size(),model.unisonGroups.size());
  return std::fclose(file)==0;
#endif
}
