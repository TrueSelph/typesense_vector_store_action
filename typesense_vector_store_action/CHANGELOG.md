## 0.0.1
- Initialized package using jvcli

## 0.0.2
- Fixed langchain schema initialization of metadata field which prevented it from being used in filtering results. This patch will require the typesense collection to be rebuilt for it to take effect.
- Added metadata_search implementation

## 0.0.3
- Updated for compatibility with updated VectorStoreAction in JIVAS alpha.51
- Updated to gracefully handle the creation of the collection if it does not exist
- Improved document listing and editing controls in action app


## 0.1.0
- Updated to support Jivas 2.1.0