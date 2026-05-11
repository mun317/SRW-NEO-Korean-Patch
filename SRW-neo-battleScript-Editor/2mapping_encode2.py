import csv
import json
import os

def load_reverse_charmap(json_file):
    """
    Loads {Japanese: Korean} structure from JSON and reverses it to {Korean: Japanese}.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Return a dictionary with Korean as key and Japanese Kanji as value
            return {v: k for k, v in data.items()}
    except Exception as e:
        print(f"[-] JSON Load Error: {e}")
        return None

def convert_to_mapped_chars(text, charmap):
    """Converts each Korean character in the text to its mapped Japanese Kanji."""
    if not text:
        return ""
    
    converted = ""
    for char in text:
        # Replace if the Korean character exists in the mapping table, 
        # otherwise keep it (brackets, control codes, etc.)
        converted += charmap.get(char, char)
    return converted

def main():
    json_file = 'font1_charmap_table_kor.json'
    input_file = 'diet_applied_results.csv'
    output_file = 'diet_applied_results.csv'

    # 1. Load mapping data (Korean -> Japanese Kanji)
    kor_to_jp_map = load_reverse_charmap(json_file)
    if kor_to_jp_map is None:
        return

    # 2. Process CSV
    if not os.path.exists(input_file):
        print(f"[-] '{input_file}' not found.")
        return

    final_results = []
    
    with open(input_file, 'r', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)
        # Ensure the fieldnames match the new structure: Offset, CharCount, Japanese, Korean, Mapping
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Get original Korean dialogue from 'Korean' column
            original_kor = row['Korean']
            
            # Convert Korean -> Japanese Kanji for font mapping
            mapped_text = convert_to_mapped_chars(original_kor, kor_to_jp_map)
            
            # Update 'Mapping' column instead of overwriting 'Korean'
            row['Mapping'] = mapped_text
            final_results.append(row)

    # 3. Save results (preserving quotes)
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(final_results)

    print(f"[*] Conversion complete! '{output_file}' has been created.")
    print(f"[*] The 'Mapping' column now contains Japanese Kanji mapped from the 'Korean' column.")

if __name__ == "__main__":
    main()