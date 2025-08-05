"""This module contains the Streamlit app for the Typesense Vector Store Action."""

import json
from io import BytesIO
from typing import Any, Dict, List

import streamlit as st
import yaml
from jvclient.lib.utils import call_api, jac_yaml_dumper
from jvclient.lib.widgets import app_controls, app_header, app_update_action
from streamlit_router import StreamlitRouter


def render(
    router: StreamlitRouter, agent_id: str, action_id: str, info: Dict[str, Any]
) -> None:
    """
    Renders a paginated list of documents.

    Args:
        router: The Streamlit router instance
        agent_id: The agent ID
        action_id: The action ID
        info: Additional information dictionary
    """
    (model_key, module_root) = app_header(agent_id, action_id, info)

    # Host Configuration
    with st.expander("Typesense Configuration"):
        # add app main controls
        app_controls(agent_id, action_id)

        # Add update button to apply changes
        app_update_action(agent_id, action_id)

    with st.expander("Import Knodes", False):
        _render_import_knodes(model_key, agent_id, module_root)

    with st.expander("Export Knodes", False):
        _render_export_knodes(model_key, agent_id, module_root)

    with st.expander("Purge Collection", False):
        _render_purge_collection(model_key, agent_id, module_root)

    # Paginated document display
    list_key = f"{model_key}_documents_list"
    if list_key not in st.session_state:
        st.session_state[list_key] = {}

    params = {
        "page": st.session_state[list_key].get("page", 1),
        "per_page": st.session_state[list_key].get("per_page", 10),
        "agent_id": agent_id,
    }
    response = call_api(endpoint="action/walker/typesense_vector_store_action/list_documents", json_data=params)

    if response:
        documents = response.get("documents", [])
        total_docs = response.get("total", 0)

        if documents:
            render_paginated_documents(
                agent_id=agent_id,
                list_key=list_key,
                module_root=module_root,
                documents=documents,
                total_docs=total_docs,
            )
        else:
            st.error("No documents found on this page.")
    else:
        st.error("Failed to fetch documents from the server.")


def render_paginated_documents(
    agent_id: str,
    list_key: str,
    module_root: str,
    documents: List[Dict[str, Any]],
    total_docs: int,
) -> None:
    """Render a paginated list of documents with edit/delete functionality.

    Args:
        agent_id: The agent ID
        list_key: The model key for session state
        module_root: The module root path
        documents: List of documents to display
        total_docs: Total number of documents in collection
    """
    # Initialize session state with proper key structure
    if list_key not in st.session_state:
        st.session_state[list_key] = {}
    if "page" not in st.session_state[list_key]:
        st.session_state[list_key]["page"] = 1
    if "per_page" not in st.session_state[list_key]:
        st.session_state[list_key]["per_page"] = 10
    if "edit_doc_id" not in st.session_state[list_key]:
        st.session_state[list_key]["edit_doc_id"] = None
    if "delete_doc_id" not in st.session_state[list_key]:
        st.session_state[list_key]["delete_doc_id"] = None
    if "editable_metadata" not in st.session_state[list_key]:
        st.session_state[list_key]["editable"] = {}

    # Items per page selection
    per_page_options = [10, 20, 30, 50, 100]
    new_per_page = st.selectbox(
        "Documents per page:",
        per_page_options,
        index=per_page_options.index(st.session_state[list_key]["per_page"]),
    )

    # Reset page if per_page changes
    if new_per_page != st.session_state[list_key]["per_page"]:
        st.session_state[list_key]["per_page"] = new_per_page
        st.session_state[list_key]["page"] = 1
        st.rerun()

    # Calculate pagination
    per_page = st.session_state[list_key]["per_page"]
    total_pages = max(1, (total_docs + per_page - 1) // per_page)
    current_page = min(st.session_state[list_key]["page"], total_pages)
    start_idx = (current_page - 1) * per_page + 1
    end_idx = min(start_idx + len(documents) - 1, total_docs)

    # Display documents
    for doc in documents:
        _render_document(
            doc=doc, agent_id=agent_id, list_key=list_key, module_root=module_root
        )

    # Pagination controls
    if total_docs > 0:
        _render_pagination_controls(
            list_key=list_key,
            current_page=current_page,
            total_pages=total_pages,
            start_idx=start_idx,
            end_idx=end_idx,
            total_docs=total_docs,
        )
    else:
        st.info("No documents found")


def _render_document(
    doc: Dict[str, Any], agent_id: str, list_key: str, module_root: str
) -> None:
    """Render a single document with edit/delete options.

    Args:
        doc: The document to render
        agent_id: The agent ID
        list_key: The model key for session state
        module_root: The module root path
    """
    doc_id = doc["id"]
    container = st.container(border=True)

    with container:
        # Handle delete confirmation
        if st.session_state[list_key].get("delete_doc_id") == doc_id:
            _render_delete_confirmation(
                doc_id=doc_id,
                agent_id=agent_id,
                list_key=list_key,
                module_root=module_root,
            )
            return

        # Edit mode
        if st.session_state[list_key].get("edit_doc_id") == doc_id:
            _render_edit_mode(
                doc=doc,
                doc_id=doc_id,
                agent_id=agent_id,
                list_key=list_key,
                module_root=module_root,
            )
        else:
            _render_view_mode(doc=doc, doc_id=doc_id, list_key=list_key)


def _render_delete_confirmation(
    doc_id: str, agent_id: str, list_key: str, module_root: str
) -> None:
    """Render the delete confirmation UI.

    Args:
        doc_id: The document ID to delete
        agent_id: The agent ID
        list_key: The model key for session state
        module_root: The module root path
    """
    st.warning(f"Are you sure you want to delete document {doc_id}?")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button(
            "✅ Confirm", key=f"confirm_delete_{doc_id}"
        ) and call_delete_document(agent_id, module_root, doc_id):
            st.session_state[list_key]["delete_doc_id"] = None
            st.rerun()
    with col2:
        if st.button("❌ Cancel", key=f"cancel_delete_{doc_id}"):
            st.session_state[list_key]["delete_doc_id"] = None
            st.rerun()


def _render_edit_mode(
    doc: Dict[str, Any], doc_id: str, agent_id: str, list_key: str, module_root: str
) -> None:
    """Render the document edit UI.

    Args:
        doc: The document being edited
        doc_id: The document ID
        agent_id: The agent ID
        list_key: The model key for session state
        module_root: The module root path
    """
    with st.form(key=f"edit_form_{doc_id}"):
        # Initialize editable metadata if not exists
        if doc_id not in st.session_state[list_key]["editable"]:
            st.session_state[list_key]["editable"][doc_id] = doc.copy()

        editable_doc = st.session_state[list_key]["editable"][doc_id]

        # Editable content
        editable_doc["text"] = st.text_area(
            "Content", value=editable_doc["text"], height=200
        )

        # Editable metadata
        st.subheader("Edit Metadata")
        for k, v in editable_doc["metadata"].items():
            if k == "page":
                try:
                    editable_doc["metadata"][k] = st.number_input(
                        k, value=int(v), min_value=0, key=f"meta_{k}_{doc_id}"
                    )
                except (ValueError, TypeError):
                    editable_doc["metadata"][k] = st.text_input(
                        k, value=str(v), key=f"meta_{k}_{doc_id}"
                    )
            else:
                editable_doc["metadata"][k] = st.text_input(
                    k, value=str(v), key=f"meta_{k}_{doc_id}"
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save") and call_update_document(
                agent_id, module_root, doc_id, editable_doc
            ):
                st.session_state[list_key]["edit_doc_id"] = None
                st.rerun()
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state[list_key]["edit_doc_id"] = None
                st.session_state[list_key]["editable"].pop(doc_id, None)
                st.rerun()


def _render_view_mode(doc: Dict[str, Any], doc_id: str, list_key: str) -> None:
    """Render the document view UI.

    Args:
        doc: The document to display
        doc_id: The document ID
        list_key: The model key for session state
    """
    st.markdown(f"**Document ID:** `{doc_id}`")
    st.text(doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"])

    with st.expander("Metadata"):
        st.json(doc["metadata"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Edit", key=f"edit_{doc_id}"):
            st.session_state[list_key]["edit_doc_id"] = doc_id
            st.rerun()
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{doc_id}"):
            st.session_state[list_key]["delete_doc_id"] = doc_id
            st.rerun()


def _render_pagination_controls(
    list_key: str,
    current_page: int,
    total_pages: int,
    start_idx: int,
    end_idx: int,
    total_docs: int,
) -> None:
    """Render the pagination controls.

    Args:
        list_key: The model key for session state
        current_page: Current page number
        total_pages: Total number of pages
        start_idx: Starting index of displayed docs
        end_idx: Ending index of displayed docs
        total_docs: Total number of documents
    """
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        disabled_prev = current_page <= 1
        if st.button("⬅️ Previous", disabled=disabled_prev, key="prev_page"):
            st.session_state[list_key]["page"] = max(1, current_page - 1)
            st.rerun()
    with col2:
        st.markdown(f"**Page {current_page} of {total_pages}**", unsafe_allow_html=True)
        st.caption(f"Showing documents {start_idx}-{end_idx} of {total_docs}")
    with col3:
        disabled_next = current_page >= total_pages
        if st.button("Next ➡️", disabled=disabled_next, key="next_page"):
            st.session_state[list_key]["page"] = min(total_pages, current_page + 1)
            st.rerun()


def _render_import_knodes(model_key: str, agent_id: str, module_root: str) -> None:
    """Render the knode import UI.

    Args:
        model_key: The model key for session state
        agent_id: The agent ID
        module_root: The module root path
    """
    knode_source = st.radio(
        "Choose data source:",
        ("Text input", "Upload file"),
        key=f"{model_key}_knode_source",
    )

    data_to_import = ""
    if knode_source == "Text input":
        data_to_import = st.text_area(
            "Agent Knodes in YAML or JSON",
            value="",
            height=170,
            key=f"{model_key}_knode_data",
        )

    uploaded_file = None
    if knode_source == "Upload file":
        uploaded_file = st.file_uploader(
            "Upload file (YAML or JSON)",
            type=["yaml", "json"],
            key=f"{model_key}_agent_knode_upload",
        )

    with_embeddings = st.toggle(
        "Import with Embeddings",
        value=True,
        key=f"{model_key}_import_embeddings",
    )

    if st.button("Import", key=f"{model_key}_btn_import_knodes"):
        if uploaded_file:
            try:
                file_content = uploaded_file.read().decode("utf-8")
                if uploaded_file.type == "application/json":
                    data_to_import = json.loads(file_content)
                else:
                    data_to_import = yaml.safe_load(file_content)
            except Exception as e:
                st.error(f"Error loading file: {e}")

        if data_to_import:
            if call_api(
                endpoint="action/walker/typesense_vector_store_action/import_knodes",
                json_data={"agent_id": agent_id, "data": data_to_import, "with_embeddings": with_embeddings},
            ):
                st.success("Agent knode imported successfully")
            else:
                st.error("Failed to import knodes. Ensure valid YAML/JSON format.")
        else:
            st.error("No data to import. Please provide valid text or upload a file.")


def _render_export_knodes(model_key: str, agent_id: str, module_root: str) -> None:
    """Render the knode export UI.

    Args:
        model_key: The model key for session state
        agent_id: The agent ID
        module_root: The module root path
    """
    as_json = st.toggle("Export as JSON", value=True, key=f"{model_key}_as_json")
    with_embeddings = st.toggle(
        "Export with Embeddings",
        value=True,
        key=f"{model_key}_with_embeddings",
    )
    with_ids = st.toggle(
        "Export with IDs",
        value=False,
        key=f"{model_key}_with_ids",
    )

    toggle_label = "Export as JSON" if as_json else "Export as YAML"
    st.caption(f"**{toggle_label} enabled**")

    if st.button("Export", key=f"{model_key}_btn_export_knodes"):
        params = {
            "as_json": as_json,
            "with_embeddings": with_embeddings,
            "with_ids": with_ids,
            "agent_id": agent_id,
        }

        result = call_api(endpoint="action/walker/typesense_vector_store_action/export_knodes", json_data=params)

        if result:
            st.success("Agent memory exported successfully!")
            if as_json:
                json_data = json.dumps(result, indent=4)
                json_file = BytesIO(json_data.encode("utf-8"))
                st.download_button(
                    label="Download JSON File",
                    data=json_file,
                    file_name="exported_knodes.json",
                    mime="application/json",
                    key="download_json",
                )
                st.json(result)
            else:
                knode_entries = jac_yaml_dumper(data=result, indent=2, sort_keys=False)
                yaml_file = BytesIO(knode_entries.encode("utf-8"))
                st.download_button(
                    label="Download YAML File",
                    data=yaml_file,
                    file_name="exported_knodes.yaml",
                    mime="application/x-yaml",
                    key="download_yaml",
                )
                st.code(knode_entries, language="yaml")
        else:
            st.error("Failed to export knodes. Please check your inputs.")


def _render_purge_collection(model_key: str, agent_id: str, module_root: str) -> None:
    """Render the collection purge UI.

    Args:
        model_key: The model key for session state
        agent_id: The agent ID
        module_root: The module root path
    """
    purge_key = f"{model_key}_purge_confirmation"
    if purge_key not in st.session_state:
        st.session_state[purge_key] = False

    if not st.session_state[purge_key]:
        if st.button("Delete all documents", key=f"{model_key}_btn_delete_collection"):
            st.session_state[purge_key] = True
            st.rerun()
    else:
        st.warning(
            "⚠️ Are you ABSOLUTELY sure you want to delete ALL documents? This action cannot be undone!"
        )
        st.markdown(
            """
            **This will permanently:**
            - Delete all documents in this collection
            - Remove all associated embeddings
            - Clear all vector search indexes
        """
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button(
                "✅ Confirm Permanent Deletion",
                type="primary",
                key=f"{model_key}_btn_confirm_purge",
            ):
                if call_api(endpoint="action/walker/typesense_vector_store_action/delete_collection", json_data={"agent_id": agent_id}):
                    st.success("Collection purged successfully")
                    st.session_state[model_key]["page"] = 1
                else:
                    st.error("Failed to complete purge.")
                st.session_state[purge_key] = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key=f"{model_key}_btn_cancel_purge"):
                st.session_state[purge_key] = False
                st.rerun()


def call_add_texts(
    agent_id: str, module_root: str, texts: List[str], metadatas: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Call the add_texts walker in the Typesense Vector Store Action.

    Args:
        agent_id: The agent ID
        module_root: The module root path
        texts: List of texts to add
        metadatas: List of metadata dictionaries

    Returns:
        Response dictionary from the walker
    """
    args = {"texts": texts, "metadatas": metadatas, "agent_id": agent_id}
    return call_api(endpoint="action/walker/typesense_vector_store_action/add_texts", json_data=args)


def call_delete_document(
    agent_id: str, module_root: str, doc_id: str
) -> Dict[str, Any]:
    """Call the delete_document walker in the Typesense Vector Store Action.

    Args:
        agent_id: The agent ID
        module_root: The module root path
        doc_id: The document ID to delete

    Returns:
        Response dictionary from the walker
    """
    args = {"id": doc_id, "agent_id": agent_id}
    return call_api(endpoint="action/walker/typesense_vector_store_action/delete_document", json_data=args)


def call_update_document(
    agent_id: str, module_root: str, doc_id: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    """Call the update_document walker in the Typesense Vector Store Action.

    Args:
        agent_id: The agent ID
        module_root: The module root path
        doc_id: The document ID to update
        data: The updated document data

    Returns:
        Response dictionary from the walker
    """
    args = {"id": doc_id, "data": data}
    return call_api(endpoint="action/walker/typesense_vector_store_action/update_document", json_data=args)
