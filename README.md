# 📘 PDF Outline Extractor  
### 🏁 Round 1A: Adobe India Hackathon Solution

This project provides a solution for **Round 1A of the Adobe India Hackathon**, which focuses on extracting a structured outline (Title, H1, H2, H3 headings with page numbers) from PDF documents.

---

## 📋 Problem Statement Overview

The core task is to build a solution that:

- Accepts a PDF file (up to 50 pages)
- Extracts the document's **Title**
- Extracts **Headings (H1, H2, H3)** including their level and page number
- Outputs a valid **JSON** file in a specified hierarchical format

---

## 🔧 Constraints

- **Execution Time**: ≤ 10 seconds for a 50-page PDF  
- **Model Size**: ≤ 200MB (if used)  
- **Network**: No internet access allowed during execution  
- **Runtime**: Must run on CPU (amd64) with 8 CPUs and 16 GB RAM  

---

## 🎯 Approach

This solution uses a **heuristic-based** approach for PDF outline extraction. Instead of training a machine learning model, it leverages the powerful parsing capabilities of **PyMuPDF** and applies intelligent rules to identify structural elements.

### 📄 PDF Parsing with PyMuPDF

PyMuPDF (`fitz`) is used to extract:

- Text content
- Font size and flags (bold/italic)
- Bounding box (location on page)

### 🏷️ Heuristic-Based Title Detection

The **title** is identified by searching for the **largest, boldest, centrally located** text on the **first page**.

### 🪜 Heuristic-Based Heading Detection (H1, H2, H3)

The script:

- Iterates through all text spans
- Analyzes:
  - **Font size** (larger = likely heading)
  - **Boldness**
  - **Relative position** (indentation and spacing)
- Assigns levels based on these properties

> ⚠️ **Note**: Heuristics in `src/main.py` are **illustrative** and should be fine-tuned for better accuracy, as per the hackathon’s "Pro Tip".

---

## 📚 Libraries Used

- **PyMuPDF (fitz)** – For PDF parsing  
- **json** – To generate the output  
- **os** – For path handling  
- **datetime** – For processing timestamps  

---

## 🚀 How to Build and Run the Solution (Docker)

### 🧰 Prerequisites

- **VS Code**: [code.visualstudio.com](https://code.visualstudio.com)  
- **Docker Desktop**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

---

## 🛠️ Setup Instructions

### 1. Create Your Project Folder

Name it something like: `adobe_hackathon_r1a`

Example paths:

- **Windows**: `C:\Users\YourUser\Documents\adobe_hackathon_r1a`
- **macOS/Linux**: `/Users/YourUser/Documents/adobe_hackathon_r1a`

---

### 2. Open in VS Code

- Launch VS Code  
- Go to **File > Open Folder...**  
- Select your `adobe_hackathon_r1a` folder

---

### 3. Create Project Structure

```text
adobe_hackathon_r1a/
├── input/
├── output/
└── src/
```

> Create folders by right-clicking the root folder in VS Code Explorer.

---

### 4. Create `requirements.txt`

Add:

```txt
PyMuPDF
```

---

### 5. Create `Dockerfile`

Create a file named `Dockerfile` in the root and paste:

```dockerfile
# Use a lightweight Python base image compatible with AMD64 architecture
FROM python:3.9-slim-buster AS builder

# Set the working directory
WORKDIR /app

# Install system dependencies required by PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set default execution command
CMD ["python", "src/main.py"]
```

---

### 6. Create `main.py`

Create a `main.py` inside `src/` folder.

Paste your logic there.

> ⚠️ Remember: Tune the heuristics inside this script to improve accuracy.

---

### 7. Add Sample PDFs

Copy sample PDFs into the `input/` folder.

---

## 📁 Final Project Structure

```text
adobe_hackathon_r1a/
├── Dockerfile
├── README.md
├── requirements.txt
├── input/
│   └── your_sample.pdf
├── output/
└── src/
    └── main.py
```

---

## 🧪 Build and Run Commands

### 🏗️ Build the Docker Image

Open terminal in VS Code:

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

> Replace `mysolutionname` and `somerandomidentifier` with your custom tag.

---

### ▶️ Run the Docker Container

```bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:somerandomidentifier
```

#### What These Flags Mean:

- `--rm`: Delete container after run  
- `-v`: Mount folders for input/output  
- `--network none`: No internet access (per constraints)

---

## ✅ Verify Output

- Check the terminal logs  
- After completion, inspect the `output/` folder  
- Open the `.json` file to review extracted title and outline  

---

## 📝 Customization Notes

To improve detection:

- Test with **varied PDFs**
- Adjust **font thresholds**
- Improve **bold/italic** detection
- Add **positional/spacing** analysis
- Create fallback rules for inconsistent layouts

---
