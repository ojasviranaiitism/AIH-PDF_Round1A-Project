Round 1A: PDF Outline Extractor
This project provides a solution for Round 1A of the Adobe India Hackathon, which focuses on extracting a structured outline (Title, H1, H2, H3 headings with page numbers) from PDF documents.

Problem Statement Overview
The core task is to build a solution that:

Accepts a PDF file (up to 50 pages).

Extracts the document's Title.

Extracts Headings (H1, H2, H3) including their level and page number.

Outputs a valid JSON file in a specified hierarchical format.

Constraints:

Execution Time: 
le 10 seconds for a 50-page PDF.

Model Size: 
le 200MB (if used).

Network: No internet access allowed during execution.

Runtime: Must run on CPU (amd64) with 8 CPUs and 16 GB RAM.

Approach
This solution employs a heuristic-based approach for PDF outline extraction. Instead of training a complex machine learning model (which would be challenging given the dataset size and constraints), it leverages the robust parsing capabilities of PyMuPDF to extract detailed text information and then applies a set of intelligent rules to identify structural elements.

PDF Parsing with PyMuPDF:

The PyMuPDF library (also known as fitz) is used to open and read PDF documents.

It extracts text content along with crucial metadata for each text "span" (a continuous piece of text with consistent formatting). This metadata includes:

Text string

Font size

Font flags (e.g., indicating if the text is bold or italic)

Bounding box coordinates (position on the page)

Heuristic-Based Title Detection:

The title is typically identified by looking for the largest, boldest, and often centrally located text on the first page of the document. The script prioritizes text that matches these criteria.

Heuristic-Based Heading Detection (H1, H2, H3):

The script iterates through all text spans in the PDF, processing them in reading order (top-to-bottom, left-to-right).

For each line of text, it analyzes properties such as:

Font Size: Headings are generally larger than body text.

Boldness: Headings are frequently bolded.

Relative Positioning: While not explicitly coded in this basic example, in a more advanced heuristic system, one would analyze the x-coordinate (indentation) and y-coordinate (vertical spacing) relative to surrounding text. Headings often have more vertical space before them.

Based on a combination of these properties (primarily font size and boldness in this example), the script assigns a hierarchical level (H1, H2, or H3).

Important Note: The heuristics (e.g., font size thresholds) provided in src/main.py are illustrative and will need to be calibrated and refined using the sample PDFs provided by the hackathon organizers and other diverse documents to achieve high accuracy. The problem statement's "Pro Tip" specifically advises against relying solely on font sizes, encouraging a more comprehensive approach.

Libraries Used
PyMuPDF (fitz): A high-performance Python library for PDF processing, essential for extracting text and layout information.

json: Python's built-in library for working with JSON data, used to format the output.

os: Python's built-in module for interacting with the operating system, used for directory and file path management.

datetime: Python's built-in module for handling dates and times, used for the processing timestamp.

How to Build and Run the Solution (Docker)
Follow these steps to build and run your Docker container as specified by the hackathon problem statement:

Install Prerequisites:

VS Code: Download and install from code.visualstudio.com.

Docker Desktop: Download and install from docker.com/products/docker-desktop. Ensure it's running before proceeding.

Create Your Main Project Folder:

On your computer, create a new empty folder. Let's call it adobe_hackathon_r1a.

Example Path: C:\Users\YourUser\Documents\adobe_hackathon_r1a (Windows) or /Users/YourUser/Documents/adobe_hackathon_r1a (macOS/Linux).

Open the Project Folder in VS Code:

Launch VS Code.

Go to File > Open Folder... (or Open... on macOS).

Navigate to and select the adobe_hackathon_r1a folder you just created. Click "Select Folder".

Create Subdirectories:

In the VS Code Explorer (left sidebar), right-click inside your adobe_hackathon_r1a folder.

Select "New Folder".

Create a folder named src.

Repeat this to create two more folders: input and output.

Your VS Code Explorer should now show:

adobe_hackathon_r1a/
├── input/
├── output/
└── src/

Create requirements.txt:

In the VS Code Explorer, right-click directly on the adobe_hackathon_r1a folder (the root folder).

Select "New File".

Name the file requirements.txt.

Open requirements.txt and add the following line:

PyMuPDF

Save the file (Ctrl+S or Cmd+S).

Create Dockerfile:

In the VS Code Explorer, right-click directly on the adobe_hackathon_r1a folder.

Select "New File".

Name the file Dockerfile (no file extension).

Open Dockerfile and copy-paste the content provided below.

Save the file.

Create main.py:

In the VS Code Explorer, click on the src folder to open it.

Right-click inside the src folder.

Select "New File".

Name the file main.py.

Open main.py and copy-paste the Python code provided below.

Crucial Reminder: The heuristics in main.py are a starting point. You will need to refine them based on testing.

Save the file.

Add Sample PDF(s):

Find a sample PDF file on your computer (e.g., file02.pdf which you provided earlier, or any other PDF).

Copy this PDF file into the adobe_hackathon_r1a/input/ folder. You can do this directly using your operating system's file explorer (e.g., Windows Explorer, macOS Finder).

Your final project structure should now look exactly like this:

adobe_hackathon_r1a/
├── Dockerfile
├── README.md
├── requirements.txt
├── input/
│   └── your_sample.pdf  (or multiple PDFs, like file02.pdf)
├── output/
└── src/
    └── main.py

Build the Docker Image:

In VS Code, open the integrated terminal (Terminal > New Terminal or Ctrl+     ).

Ensure the terminal's current directory is adobe_hackathon_r1a (your project's root folder).

In the terminal, type the following command and press Enter:

docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

Important: Replace mysolutionname and somerandomidentifier with names you choose (e.g., adobe-outline-extractor:v1).

The . at the end is crucial – it tells Docker to look for the Dockerfile in the current directory.

This command will download the base Python image, install PyMuPDF and other dependencies inside the image, and copy your code. This process might take a few minutes the first time.

You should see output indicating layers being built successfully.

Run the Docker Container:

Once the image build is complete, use the following command in the same terminal and press Enter:

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:somerandomidentifier

Important: Use the exact same mysolutionname:somerandomidentifier tag you used in the docker build command.

--rm: Automatically removes the container after it finishes running.

-v "$(pwd)/input:/app/input": This mounts your local input folder (where your PDFs are) to the /app/input folder inside the Docker container.

-v "$(pwd)/output:/app/output": This mounts your local output folder to the /app/output folder inside the Docker container. Your script will write JSON files here.

--network none: This is critical for the hackathon constraint – it ensures your container has no internet access during execution.

Monitor Execution and Verify Output:

You will see output in the terminal from your main.py script, indicating which PDFs are being processed and where the output is being saved.

After the command finishes (the terminal prompt returns), go to your adobe_hackathon_r1a/output/ folder on your computer.

You should find JSON files there (e.g., your_sample.json or file02.json), corresponding to the PDFs you placed in the input folder. Open these JSON files with VS Code or a text editor to inspect the extracted title and outline.

File Contents (Detailed)
Dockerfile Content
# Use a lightweight Python base image compatible with AMD64 architecture
# This ensures a small image size and CPU-only execution.
FROM python:3.9-slim-buster AS builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by PyMuPDF
# libglib2.0-0 is a common dependency for many Python libraries, including some used by PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# PyMuPDF is the primary library for PDF parsing
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ ./src/

# Command to run the application
# This command will be executed when the container starts.
# It calls the main.py script which handles all PDF processing.
CMD ["python", "src/main.py"]
