# Typesense Vector Store Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/typesense_vector_store_action)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/typesense_vector_store_action/test-action.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/typesense_vector_store_action)
![GitHub pull requests](https://img.shields.io/github/issues-pr/TrueSelph/typesense_vector_store_action)
![GitHub](https://img.shields.io/github/license/TrueSelph/typesense_vector_store_action)

JIVAS action wrapper around the Typesense vector database for retrieval-augmented generation tasks.

## Package Information

- **Name:** `jivas/typesense_vector_store_action`
- **Author:** [V75 Inc.](https://v75inc.com/)
- **Architype:** `TypesenseVectorStoreAction`

## Meta Information

- **Title:** Typesense Vector Store Action
- **Group:** core
- **Type:** vector_store_action

## Configuration

- **Singleton:** true

## Dependencies

- **Jivas:** `^2.0.0`
- **Pip:**
  - `typesense`: `0.21.0`

This package, developed by V75 Inc., provides integration with the Typesense vector database, supporting retrieval-augmented generation tasks. As a core vector store action, it enables efficient storage, retrieval, and manipulation of vector data within the Typesense ecosystem. Configured as a singleton, it requires the Jivas library version 2.0.0 and the `typesense` Python package version 0.21.0 to function effectively.

---

## How to Use

Below is detailed guidance on how to configure and use the Typesense Vector Store Action.

### Overview

The Typesense Vector Store Action provides an abstraction layer for interacting with the Typesense vector database. It supports multiple configurations for various use cases, including:

- **Document storage and retrieval** for vector-based search.
- **Integration** with Typesense for efficient vector operations.
- **Pipeline management** for chaining multiple vector operations.

---

### Configuration Structure

The configuration consists of the following components:

### `typesense_settings`

Defines the settings for the Typesense database, such as host, API keys, and parameters.

```python
typesense_settings = {
    "host": "your_typesense_host",       # Example: "localhost" or "xxx.a1.typesense.net"
    "port": "8108",                      # Example: "8108" or "443" for Typesense Cloud
    "protocol": "http",                  # Example: "http" or "https" for Typesense Cloud
    "api_key": "your_api_key",           # API key for Typesense
    "connection_timeout": 2,             # Timeout in seconds
    "collection_name": "your_collection" # Name of the Typesense collection
}
```

---

### Example Configurations

### Basic Configuration for Typesense

```python
typesense_settings = {
    "host": "localhost",
    "port": "8108",
    "protocol": "http",
    "api_key": "your_typesense_api_key",
    "connection_timeout": 2,
    "collection_name": "example_collection"
}
```

### Best Practices
- Validate your API keys and Typesense settings before deployment.
- Test pipelines in a staging environment before production use.

---

## 🔰 Contributing

- **🐛 [Report Issues](https://github.com/TrueSelph/typesense_vector_store_action/issues)**: Submit bugs found or log feature requests for the `typesense_vector_store_action` project.
- **💡 [Submit Pull Requests](https://github.com/TrueSelph/typesense_vector_store_action/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/TrueSelph/typesense_vector_store_action
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details open>
<summary>Contributor Graph</summary>
<br>
<p align="left">
    <a href="https://github.com/TrueSelph/typesense_vector_store_action/graphs/contributors">
        <img src="https://contrib.rocks/image?repo=TrueSelph/typesense_vector_store_action" />
   </a>
</p>
</details>

## 🎗 License

This project is protected under the Apache License 2.0. See [LICENSE](./LICENSE) for more information.