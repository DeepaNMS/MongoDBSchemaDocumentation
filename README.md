# MongoDBSchemaDocumentation

> A Python-based tool that automates the generation of MongoDB schema documentation from Java source files and publishes it to Confluence.

---

## Table of Contents

- [2.1 Overview](#21-overview)
- [2.2 Features](#22-features)
- [2.3 Project Structure](#23-project-structure)
- [2.4 Installation](#24-installation)
- [2.5 Usage](#25-usage)
- [2.6 Output](#26-output)
- [2.7 Contact](#27-contact)

---

## 2.1 Overview

**MongoDBSchemaDocumentation** is designed to simplify the process of documenting MongoDB schemas by automating the following steps:

1. **Fetches Java source files** — Reads one or more GitHub repository URLs (configured in `configurations.py`) and retrieves all Java entity class files from the specified paths.
2. **Parses Java classes into JSON Schema** — Converts Java class definitions into structured JSON schema representations, resolving data types without relying on an LLM.
3. **Identifies MongoDB collections** — Inspects parsed classes to determine which ones map to MongoDB collections (i.e., annotated entity classes).
4. **Generates HTML documentation** — Creates an HTML representation of the schema for each identified MongoDB collection class.
5. **Publishes to Confluence** — Uploads or updates the generated HTML documentation to a specified Confluence page based on configurations in `configurations.py`.

---

## 2.2 Features

| Feature | Description |
|---|---|
| **Automated Java Source Retrieval** | Fetches Java entity classes from GitHub repositories. |
| **Schema Parsing** | Converts Java classes into JSON schema representations. |
| **MongoDB Collection Identification** | Detects annotated classes that map to MongoDB collections. |
| **HTML Documentation Generation** | Creates visually appealing schema documentation in HTML format. |
| **Confluence Integration** | Publishes schema documentation directly to Confluence pages. |

---

## 2.3 Project Structure

```
MongoDBSchemaDocumentation/
├── src/
│   ├── ConfluenceOperations.py   # Handles Confluence operations
│   ├── GithubOperations.py       # Handles GitHub operations
│   ├── HTMLOperations.py         # Generates HTML to update in Confluence
│   ├── JsonOperations.py         # Handles JSON operations
│   └── configurations.py         # Configuration settings (GitHub URLs, Confluence, etc.)
├── tests/
├── main.py                       # Main entry point for the application
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## 2.4 Installation

### Prerequisites

- **Python** — Version 3.8 or higher
- **Git** — For cloning repositories
- **Confluence Account** — With API access enabled

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/MongoDBSchemaDocumentation.git
   cd MongoDBSchemaDocumentation
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

   _On Windows:_
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## 2.5 Usage

### Configure the application

Update `src/configurations.py` with:

- GitHub repository URLs
- File paths to scan for Java classes
- Confluence API credentials and page details

#### Example `configurations.py`

```python
# GitHub Repository URLs
GIT_HTML_URLS = [
    "https://github.com/your-org/your-repo",
    "https://github.com/another-org/another-repo"
]

# Confluence Page ID
CONFLUENCE_PAGE_ID = "<id of the page you are trying to access>"
```

### Run the application

```bash
python main.py
```

---

## 2.6 Output

| File | Description |
|---|---|
| `output/result.txt` | Contains the generated JSON schema |
| `output/Logs.txt` | Contains the application logs |

---

## 2.7 Contact

For questions, suggestions, or feedback, feel free to reach out:

- **Author:** Deepa Nair M S
- **Email:** [deepanairms@gmail.com](mailto:deepanairms@gmail.com)
