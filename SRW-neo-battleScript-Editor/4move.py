import csv
import json
import os

def load_charmap(json_file):
    """Loads the {Japanese_Kanji: Korean_Char} mapping from JSON."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] JSON Load Error: {e}")
        return None

def convert_to_mapped_chars(text, charmap_reversed):
    """Converts Korean text back to mapped Japanese Kanji characters."""
    if not text:
        return ""
    converted = ""
    for char in text:
        # Get the mapped Kanji for the Korean character, or keep original if not found
        converted += charmap_reversed.get(char, char)
    return converted

def main():
    # File Paths
    diet_log_csv = 'diet_applied_results.csv'
    mapping_json = 'font1_charmap_table_kor.json'
    master_csv = 'msbtl_extracted_v2.csv'
    output_csv = 'msbtl_extracted_v2.csv'

    # 1. Check if files exist
    # FIXED: Use Python's built-in all() instead of os.path.all()
    required_files = [diet_log_csv, mapping_json, master_csv]
    if not all(os.path.exists(f) for f in required_files):
        for f in required_files:
            if not os.path.exists(f):
                print(f"[-] Required file missing: {f}")
        return

    # 2. Load and Reverse Charset Mapping (Korean -> Kanji)
    charmap = load_charmap(mapping_json)
    if not charmap:
        return
    # Create a reverse map for conversion: {Korean: Kanji}
    kor_to_jp_map = {v: k for k, v in charmap.items() if v}

    # 3. Read the Diet Log and prepare updates
    updates = {}
    with open(diet_log_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Use English column names as updated in previous step
            offset = row['Offset']
            korean_text = row['Korean']
            # Re-generate Mapping value from the Korean text
            new_mapping = convert_to_mapped_chars(korean_text, kor_to_jp_map)
            updates[offset] = {
                'Korean': korean_text,
                'Mapping': new_mapping
            }
    
    print(f"[*] Loaded {len(updates)} updates from diet log.")

    # 4. Merge updates into the Master CSV
    final_data = []
    fieldnames = ["Offset", "CharCount", "Japanese", "Korean", "Mapping"]
    match_count = 0

    with open(master_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            offset = row['Offset']
            
            # If this offset exists in the diet updates, overwrite the values
            if offset in updates:
                row['Korean'] = updates[offset]['Korean']
                row['Mapping'] = updates[offset]['Mapping']
                match_count += 1
            
            final_data.append(row)

    # 5. Save the final merged result
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        # QUOTE_ALL ensures all fields are enclosed in double quotes ""
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"[*] Update Complete: {match_count} dialogues have been synchronized.")
    print(f"[*] Final merged file created: {output_csv}")

if __name__ == "__main__":
    main()