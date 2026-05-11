import csv
import re
import os

def extract_event_dialogue():
    input_pac = 'event.pac'
    output_csv = 'event_extracted_v2.csv'
    
    if not os.path.exists(input_pac):
        print(f"[-] '{input_pac}' not found.")
        return

    # 1. Read file
    with open(input_pac, 'rb') as f:
        content = f.read()

    # 2. Compile Regex Pattern
    # Applying [\s\S] to match all bytes including newlines between brackets
    # Shift-JIS Full-width symbols: 「 (81 75), 」 (81 76), （ (81 69), ） (81 6A)
    # Pattern: Collect all bytes starting from an opening bracket until the first closing bracket
    pattern = re.compile(rb'(\x81\x75[\s\S]*?\x81\x76|\x81\x69[\s\S]*?\x81\x6A)')

    results = []
    seen_offsets = set()

    print("[*] Starting extraction (including multi-line dialogue)...")

    # 3. Search for matching dialogues
    for match in pattern.finditer(content):
        offset = match.start()
        raw_bytes = match.group()
        
        if offset in seen_offsets:
            continue
        seen_offsets.add(offset)

        try:
            # Decode Shift-JIS (handles mixed newlines/control characters)
            jp_text = raw_bytes.decode('shift_jis', errors='ignore')
            
            # Calculate actual character length
            char_count = len(jp_text)
            
            results.append({
                "Offset": hex(offset).upper(),
                "CharCount": char_count,
                "Japanese": jp_text,
                "Korean": "",
                "Mapping": ""  # Added Mapping column data
            })
        except:
            continue

    # 4. Save to CSV (QUOTE_ALL is essential for multi-line dialogues)
    # Added "Mapping" to the fieldnames list
    fieldnames = ["Offset", "CharCount", "Japanese", "Korean", "Mapping"]
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f_csv:
        # QUOTE_ALL ensures that multi-line data is not corrupted in CSV format
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(results)

    print(f"[*] Extraction complete! {len(results)} dialogues saved to '{output_csv}'.")

if __name__ == "__main__":
    extract_event_dialogue()