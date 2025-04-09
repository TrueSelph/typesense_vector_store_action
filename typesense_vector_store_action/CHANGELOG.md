## 0.0.1
- Initialized package using jvcli

## 0.0.2
- Fixed langchain schema initialization of metadata field which prevented it from being used in filtering results. This patch will require the typesense collection to be rebuilt for it to take effect.
- Added metadata_search implementation
