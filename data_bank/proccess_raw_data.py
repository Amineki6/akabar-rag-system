import os
import re
import shutil

# --- Configuration ---
# Set the directory where your raw .md files are located.
# The script assumes a 'raw_data_lake' folder in the same directory.
INPUT_DIR = 'raw_data_lake'

# Set the directory where the structured output will be saved.
# This folder will be deleted and recreated on each run.
OUTPUT_DIR = 'output'
# ---------------------

def parse_and_structure_files():
    """
    Parses concatenated markdown files from an input directory and
    recreates them in a structured output directory based on metadata
    found in the content.
    """
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found.")
        print("Please make sure your markdown files are in a folder named 'raw_data_lake'.")
        return

    # Clean up and recreate the output directory for a fresh start
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"Cleaned and created output directory: '{OUTPUT_DIR}'")

    # Regex to find the header line like '--- Content from: path/to/file.txt ---'
    header_pattern = re.compile(r"--- Content from: (.*?) ---")
    
    # Process each file in the input directory
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.md'):
            input_filepath = os.path.join(INPUT_DIR, filename)
            print(f"\nProcessing file: {filename}")

            # The city/toplevel name is derived from the filename (e.g., 'agadir.md' -> 'agadir')
            base_name = os.path.splitext(filename)[0]

            with open(input_filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split the file into sections based on the '=====' separator
            sections = content.split('================================================================================')

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                # Find the header line in the section
                header_match = header_pattern.search(section)
                if not header_match:
                    print(f"  [Warning] Could not find a valid header in a section of {filename}. Skipping section.")
                    continue
                
                # Extract the original file path from the header
                original_path = header_match.group(1).strip()
                path_parts = original_path.split('/')
                
                # Extract the content, which is everything after the header line
                content_body = section[header_match.end():].strip()

                # Determine the correct output path
                # For 'morocco', the structure is flat. For cities, it's nested.
                if base_name == 'morocco':
                    # Path is like 'morocco/architecture.txt' -> 'morocco/architecture.md'
                    if len(path_parts) > 1:
                        output_filename = os.path.splitext(path_parts[-1])[0] + '.md'
                        output_subfolder = os.path.join(OUTPUT_DIR, base_name)
                    else:
                        print(f"  [Warning] Unexpected path format for morocco: {original_path}")
                        continue
                else:
                    # Path is like 'city/category/file.txt' -> 'city/category/file.md'
                    # We ignore the first part of the path (the inconsistent city name)
                    # and rely on the filename for the base folder.
                    sub_dirs = path_parts[1:-1]
                    output_filename = os.path.splitext(path_parts[-1])[0] + '.md'
                    output_subfolder = os.path.join(OUTPUT_DIR, base_name, *sub_dirs)

                # Create the necessary directories
                os.makedirs(output_subfolder, exist_ok=True)
                
                output_filepath = os.path.join(output_subfolder, output_filename)
                
                # Write the cleaned content to the new file
                with open(output_filepath, 'w', encoding='utf-8') as out_f:
                    out_f.write(content_body)
                
                print(f"  -> Created: {output_filepath}")

    print("\nParsing complete!")

if __name__ == '__main__':
    # To run this script, you need to create a 'raw_data_lake' folder
    # in the same directory and place your .md files inside it.
    # The script will then generate the 'output' folder with the results.
    parse_and_structure_files()