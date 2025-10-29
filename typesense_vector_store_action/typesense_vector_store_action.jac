import os;
import json;
import yaml;
import logging;
import traceback;
import typesense;
import from typing { Any }
import from .modules.langchain_typesense { Typesense }
import from langchain_openai { OpenAIEmbeddings }
import from langchain_core.vectorstores.base { VectorStore }
import from langchain_core.documents.base { Document }
import from logging { Logger }
import from jivas.agent.action.vector_store_action { VectorStoreAction }

node TypesenseVectorStoreAction(VectorStoreAction) {
    # Action for managing a Typesense vector store

    static has logger:Logger = logging.getLogger(__name__);
    has host:str = os.environ.get('TYPESENSE_HOST','typesense');
    has port:str = os.environ.get('TYPESENSE_PORT','8108');
    has protocol:str = os.environ.get('TYPESENSE_PROTOCOL','http');
    has api_key:str = os.environ.get('TYPESENSE_API_KEY','');
    has connection_timeout:int = int(os.environ.get('TYPESENSE_CONNECTION_TIMEOUT_SECONDS','2'));
    has collection_name:str = "";
    has vector_dims:int = 1024;  # Default dimensions for embedding model
    has per_page:int = 100;

    def on_register() {
        if not self.collection_name {
            self.collection_name = self.get_agent().id;
        }
    }

    def on_enable() {
        if not self.collection_name {
            self.collection_name = self.get_agent().id;
        }
    }

    def get_client() -> Union[typesense.Client, None] {
        try {
            required = [self.host, self.port, self.protocol, self.api_key];
            if not all(required) {
                raise ValueError("Missing Typesense configuration");
            }
            return typesense.Client({
                'api_key': self.api_key,
                'nodes': [{
                    'host': self.host,
                    'port': self.port,
                    'protocol': self.protocol
                }],
                'connection_timeout_seconds': self.connection_timeout
            });
        } except Exception as e {
            self.logger.error(f"Client initialization failed: {traceback.format_exc()}");
            return None;
        }
    }

    def get_collection(collection_name: str) -> Union[typesense.collection.Collection, None] {

        try {
            client = self.get_client();
            if not client {
                return None;
            }

            # Try to retrieve existing collection
            try {
                collection = client.collections[collection_name].retrieve();
                return client.collections[collection_name];
            } except typesense.exceptions.ObjectNotFound {

                if(vector_store := self.get_vectorstore()) {
                    # Create new collection with vector schema
                    self.get_vectorstore()._create_collection(num_dim=self.vector_dims);
                    return client.collections[collection_name];
                }

            }

        } except typesense.exceptions.TypesenseClientError as e {
            self.logger.error(f"Typesense error: {e}");
        } except Exception as e {
            self.logger.error(f"Unexpected error: {traceback.format_exc()}");
        }
        return None;
    }

    def get_vectorstore() -> Union[Typesense, None] {
        try {
            if not (embedding := self.get_embedding_model()) {
                raise ValueError("Embedding model unavailable");
            }
            if not self.collection_name {
                raise ValueError("Missing collection name");
            }
            if client := self.get_client() {
                return Typesense(
                    typesense_client=client,
                    embedding=embedding,
                    typesense_collection_name=self.collection_name,
                    text_key="text",
                    per_page=self.per_page
                );
            }
        } except Exception as e {
            self.logger.error(f"Vectorstore failed: {traceback.format_exc()}");
        }
        return None;
    }

    def list_documents(page:int=1, per_page:int=10, with_embeddings:bool=False, filter_by:str="") -> dict {
        try {
            if collection := self.get_collection(self.collection_name) {
                query = {
                    'q': '*',
                    'per_page': per_page,
                    'page': page,
                    'filter_by': filter_by
                };

                if not with_embeddings {
                    query['exclude_fields'] = 'vec';
                }

                results = collection.documents.search(query);
                documents = [hit['document'] for hit in results.get('hits', [])];
                return {
                    'page': page,
                    'per_page': per_page,
                    'total': results.get('found', 0),
                    'documents': documents
                };
            }
        } except Exception as e {
            self.logger.error(f"Listing failed: {traceback.format_exc()}");
        }
        return {
            'page': page,
            'per_page': per_page,
            'total': 0,
            'documents': []
        };
    }

    def get_document(id:str) -> Union[dict, None] {
        try {
            if collection := self.get_collection(self.collection_name) {
                document = collection.documents[id].retrieve();
                document.pop('vec', None);
                return document;
            }
        } except typesense.exceptions.ObjectNotFound {
            return None;
        } except Exception as e {
            self.logger.error(f"Get document failed: {traceback.format_exc()}");
        }
        return None;
    }

    def metadata_search(metadata:dict, k:int=10, **kwargs:Any) -> List[Document] {
        try {
            filter_str = " && ".join([f"metadata.{k}:={v}" for (k,v) in metadata.items()]);
            return self.similarity_search(query="*", k=k, filter=filter_str, **kwargs);
        } except Exception as e {
            self.logger.error(f"Metadata search failed: {str(e)}");
            return [];
        }
    }

    def update_document(id:str, data:dict) -> Union[dict, None] {
        try {
            if collection := self.get_collection(self.collection_name) {
                return collection.documents[id].update(data);
            }
        } except Exception as e {
            self.logger.error(f"Update failed: {traceback.format_exc()}");
        }
        return None;
    }

    def delete_document(id:str) -> Union[dict, None] {
        try {
            if collection := self.get_collection(self.collection_name) {
                return collection.documents[id].delete();
            }
        } except Exception as e {
            self.logger.error(f"Delete failed: {traceback.format_exc()}");
        }
        return None;
    }

    def delete_collection() -> bool {
        try {
            if collection := self.get_collection(self.collection_name) {
                result = collection.delete();
                return result;
            }
        } except Exception as e {
            self.logger.error(f"Collection deletion failed: {traceback.format_exc()}");
        }
        return False;
    }
}