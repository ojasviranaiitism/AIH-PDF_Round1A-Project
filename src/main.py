import fitz  # PyMuPDF library for PDF processing
import json    # For working with JSON data
import os      # For interacting with the operating system (file paths, directories)
import datetime # For generating timestamps
import re      # For regular expressions

def avg(nums):
    """Calculates the average of a list of numbers."""
    if not nums:
        return 0
    return sum(nums) / len(nums)

def extract_outline(pdf_path):
    """
    Extracts the document title and a hierarchical outline (H1, H2, H3)
    from a given PDF file using heuristics directly translated from the
    provided JavaScript approach.

    Args:
        pdf_path (str): The full path to the PDF file.

    Returns:
        dict: A dictionary containing the 'title' and 'outline' list.
    """
    title = ""
    outline = []
    
    # List to store all text items (spans) with their relevant properties.
    # Corresponds to `pageItems` in JS `extractAllPageItems` map.
    all_page_items = [] 

    try:
        doc = fitz.open(pdf_path)

        # --- Step 1: Extract all page items (spans) ---
        # Corresponds to `extractAllPageItems` in JS
        for p_num in range(doc.page_count):
            page = doc[p_num]
            text_content = page.get_text("dict") # Get text content as a dictionary
            
            # Iterate through blocks, lines, and spans to get text and properties
            for block in text_content["blocks"]:
                if block["type"] == 0: # Only process text blocks
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text: # Only include non-empty text
                                all_page_items.append({
                                    "text": text,
                                    "y": span["bbox"][1],  # Top-left Y-coordinate
                                    "fontSize": span["size"], # Font size
                                    "fontName": span["font"], # Font name
                                    "page": p_num + 1 # 1-based page number
                                })
        
        # --- Step 2: Group text items into lines for each page ---
        # Corresponds to `groupItemsIntoLines` in JS
        # We need to process page by page, then group into lines, then flatten.
        
        # First, group all_page_items by page
        items_by_page = {}
        for item in all_page_items:
            if item["page"] not in items_by_page:
                items_by_page[item["page"]] = []
            items_by_page[item["page"]].append(item)

        all_pages_lines = []
        y_tolerance = 2 # As per JS code

        for page_num in sorted(items_by_page.keys()):
            page_items = items_by_page[page_num]
            
            # Sort items by Y-coordinate descending (as in JS `groupItemsIntoLines`)
            # Note: PyMuPDF's Y increases downwards, so `b.y - a.y` means items higher on the page come later.
            # We'll sort by Y ascending to process top-down, then reverse the line order later if needed.
            # Or, more simply, sort by Y ascending and build lines top-down.
            sorted_items = sorted(page_items, key=lambda it: it["y"])
            
            lines_on_page = []
            current_line = None

            for item in sorted_items:
                if not current_line:
                    current_line = { "y": item["y"], "texts": [item["text"]], "font_sizes": [item["fontSize"]] }
                elif abs(item["y"] - current_line["y"]) <= y_tolerance:
                    current_line["texts"].append(item["text"])
                    current_line["font_sizes"].append(item["fontSize"])
                else:
                    # Finish the current line and start a new one
                    lines_on_page.append({
                        "y": current_line["y"],
                        "text": " ".join(current_line["texts"]).replace("  ", " ").strip(),
                        "fontSizeAvg": avg(current_line["font_sizes"]),
                        "page": page_num # Add page number to line object
                    })
                    current_line = { "y": item["y"], "texts": [item["text"]], "font_sizes": [item["fontSize"]] }
            
            if current_line: # Add the last line
                lines_on_page.append({
                    "y": current_line["y"],
                    "text": " ".join(current_line["texts"]).replace("  ", " ").strip(),
                    "fontSizeAvg": avg(current_line["font_sizes"]),
                    "page": page_num
                })
            
            # Sort lines on page by Y ascending (top to bottom)
            lines_on_page.sort(key=lambda l: l["y"])
            all_pages_lines.append(lines_on_page)

        # --- Step 3: Detect Title ---
        # Corresponds to `detectTitle` in JS, but adapted for multi-line title and exclusion.
        
        title_lines = []
        if all_pages_lines and all_pages_lines[0]: # Check if first page has lines
            first_page_lines = all_pages_lines[0]
            
            # Find the maximum font size on the first page
            max_title_font_size = 0
            if first_page_lines:
                max_title_font_size = max(line["fontSizeAvg"] for line in first_page_lines)

            # Filter lines that have the max font size and sort by Y descending (as in JS)
            # JS: `sort((a, b) => b.y - a.y)` means higher Y (lower on page) comes first.
            # Our `all_pages_lines` are already sorted by Y ascending (top to bottom).
            # So, to get the "top" lines with max font size, we can filter and then sort by Y ascending.
            
            # The JS code's `detectTitle` sorts by `fontSizeAvg` descending, then iterates.
            # It then filters out lines starting with numbers.
            
            # Let's collect all lines with max font size from the first page, sorted by Y ascending.
            potential_title_lines = [
                line for line in first_page_lines 
                if line["fontSizeAvg"] == max_title_font_size
            ]
            potential_title_lines.sort(key=lambda l: l["y"]) # Sort top-down

            # JS `detectTitle` loop: `for (const ln of sorted)`
            # `if (!/^\s*\d+(\.|$)/.test(ln.text) && ln.text.length > 2)`
            
            # Re-implementing the JS title detection logic:
            # Get all lines from page 1, sorted by font size (desc), then Y (asc)
            sorted_page1_lines_for_title = sorted(first_page_lines, key=lambda l: (-l["fontSizeAvg"], l["y"]))
            
            found_title_line_data = None
            for ln in sorted_page1_lines_for_title:
                # Exclude lines that start with numbers (e.g., "1. Introduction")
                # and ensure text is not too short.
                if not re.match(r'^\s*\d+(\.|$)', ln["text"]) and len(ln["text"]) > 2:
                    found_title_line_data = ln
                    break # Found the most prominent non-numbered line

            if found_title_line_data:
                # Now, collect all lines that are part of this "title block"
                # This means lines with the same font size as the main title line, and vertically close.
                title_lines_to_combine = []
                current_y_bottom = -1 # Track bottom of last added title line
                
                # Iterate through all original first_page_lines (sorted top-down)
                for line_data in first_page_lines:
                    # If this line has the same font size as the main title line
                    # and is vertically close to the previously added line (if any)
                    # and is not a numbered heading itself
                    if line_data["fontSizeAvg"] == found_title_line_data["fontSizeAvg"] and \
                       not re.match(r'^\s*\d+(\.|$)', line_data["text"]):
                        
                        if not title_lines_to_combine: # First line of the title block
                            title_lines_to_combine.append(line_data)
                            current_y_bottom = line_data["y"] + line_data["fontSizeAvg"] # Approximate bottom
                        elif (line_data["y"] - current_y_bottom) < (line_data["fontSizeAvg"] * 1.5): # Vertically close
                            title_lines_to_combine.append(line_data)
                            current_y_bottom = line_data["y"] + line_data["fontSizeAvg"]
                        else:
                            # Line is too far vertically, stop combining
                            break
                    elif title_lines_to_combine: # If we started combining but found a line that doesn't fit
                        break # Stop combining
            
                # Join the combined parts to form the final title
                title = " ".join([l["text"] for l in title_lines_to_combine]).replace("  ", " ").strip()
            
            if not title: # Fallback if no specific title detected
                title = first_page_lines[0]["text"] if first_page_lines else 'Untitled Document'
        else:
            title = 'Untitled Document'


        # --- Step 4: Detect Headings ---
        # Corresponds to `detectHeadings` in JS, including title line exclusion.
        
        flat_heading_candidates = []
        
        # Create a set of title line texts for efficient exclusion
        title_text_set = set(l["text"] for l in title_lines_to_combine)

        for page_lines in all_pages_lines:
            for ln in page_lines:
                # Skip lines that are part of the title
                if ln["text"] in title_text_set:
                    continue

                words = ln["text"].split()
                if not ln["text"]: continue
                if len(words) > 12: continue # Max 12 words for a heading
                if re.search(r'[.!?]\s*$', ln["text"]): continue # Ends with punctuation

                flat_heading_candidates.append({
                    "text": ln["text"],
                    "page": ln["page"],
                    "fontSize": ln["fontSizeAvg"],
                    "y": ln["y"] # Keep y for final sorting
                })

        if not flat_heading_candidates:
            return {"title": title, "outline": []}

        # Group by rounded font size (as in JS `sizeMap`)
        size_map = {}
        for f in flat_heading_candidates:
            key = round(f["fontSize"])
            if key not in size_map:
                size_map[key] = []
            size_map[key].append(f)
        
        # Sort font size bins from largest to smallest (as in JS `sizeBins`)
        sorted_size_bins = sorted(size_map.items(), key=lambda item: item[0], reverse=True)

        level_labels = ['H1', 'H2', 'H3']
        
        # Assign levels based on sorted font size bins (as in JS)
        temp_outline = []
        level_idx = 0
        for font_size_key, items_in_bin in sorted_size_bins:
            if level_idx >= len(level_labels):
                break # All levels assigned

            lvl = level_labels[level_idx]
            for item in items_in_bin:
                temp_outline.append({ "level": lvl, "text": item["text"], "page": item["page"], "y": item["y"] })
            level_idx += 1

        # Final sort by page, then by Y-position (as in JS)
        outline = sorted(temp_outline, key=lambda x: (x["page"], x["y"]))

        doc.close()

    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")

    return {"title": title, "outline": outline}

def process_pdfs_in_directory(input_dir, output_dir):
    """
    Processes all PDF files found in the specified input directory.
    For each PDF, it extracts the outline and saves it as a JSON file
    in the specified output directory.
    """
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found: '{input_dir}'")
        return
    
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'. Please ensure PDFs are placed in this directory.")
        return

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        output_filename_base = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{output_filename_base}.json")

        print(f"--- Processing '{filename}' ---")
        
        processing_timestamp = datetime.datetime.now().isoformat()

        extracted_data = extract_outline(pdf_path)
        
        final_output = {
            "metadata": {
                "input_document": filename,
                "processing_timestamp": processing_timestamp,
                "persona": "N/A (Challenge 1A)",
                "job_to_be_done": "Extract structured outline (title, H1, H2, H3)"
            },
            "extracted_section": {
                "title": extracted_data.get("title", ""),
                "outline": extracted_data.get("outline", [])
            }
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved outline for '{filename}' to '{output_filename_base}.json'")
        except IOError as e:
            print(f"Error: Could not save output for '{filename}' to '{output_path}'. Reason: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving output for '{filename}': {e}")
        print(f"--- Finished processing '{filename}' ---\n")


if __name__ == "__main__":
    INPUT_DIR = "/app/input"
    OUTPUT_DIR = "/app/output"

    print(f"Starting PDF outline extraction process from '{INPUT_DIR}' to '{OUTPUT_DIR}'...")
    process_pdfs_in_directory(INPUT_DIR, OUTPUT_DIR)
    print("PDF outline extraction process completed.")