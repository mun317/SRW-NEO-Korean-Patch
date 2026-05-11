import csv
import os

def get_sjis_bytes(text):
    """Returns byte data encoded in Shift-JIS."""
    return text.encode('shift_jis', errors='ignore')

def apply_diet(dst_text, max_bytes):
    """
    Performs 'diet' logic (length reduction) and returns 
    the adjusted text along with the count of exceeded bytes.
    """
    initial_bytes_len = len(get_sjis_bytes(dst_text))
    over_bytes = initial_bytes_len - max_bytes
    
    # If it doesn't exceed the limit
    if over_bytes <= 0:
        return dst_text, 0

    temp_text = dst_text

    # Step 1: Remove spaces
    while len(get_sjis_bytes(temp_text)) > max_bytes:
        space_idx = temp_text.find(' ')
        if space_idx != -1:
            temp_text = temp_text[:space_idx] + temp_text[space_idx+1:]
        else:
            break
    if len(get_sjis_bytes(temp_text)) <= max_bytes:
        return temp_text, over_bytes

    # Step 2: Remove symbols (preserve < > tags)
    cleaned = ""
    is_inside_tag = False
    targets = ['…', '.', '!', '！', '?', '？', ',', '，', '「', '」', '（', '）', '\"', '\'']
    
    for char in temp_text:
        if char == '<': is_inside_tag = True
        if char == '>': 
            cleaned += char
            is_inside_tag = False
            continue
        if is_inside_tag or char not in targets:
            cleaned += char
            
    temp_text = cleaned
    if len(get_sjis_bytes(temp_text)) <= max_bytes:
        return temp_text, over_bytes

    # Step 3: Force cut at the end
    while len(get_sjis_bytes(temp_text)) > max_bytes:
        temp_text = temp_text[:-1]

    return temp_text, over_bytes

def main():
    # Updated input filename as requested
    input_csv = 'event_extracted_v2.csv' 
    original_pac = 'event.pac'
    output_pac = 'event_mod.pac'
    log_csv = 'diet_applied_results.csv'
    
    if not os.path.exists(original_pac):
        print(f"[-] Original {original_pac} not found.")
        return

    with open(original_pac, 'rb') as f:
        pac_data = bytearray(f.read())

    injected_count = 0
    diet_log = []

    with open(input_csv, 'r', encoding='utf-8-sig') as f_csv:
        reader = csv.DictReader(f_csv)
        fieldnames = reader.fieldnames
        
        for row in reader:
            try:
                # Updated to use new column names: Offset, Japanese, Korean, Mapping
                offset = int(row['Offset'], 16)
                src_text = row['Japanese']
                # Using 'Mapping' for actual injection as requested
                dst_text = row['Mapping'] 
                
                max_bytes = len(get_sjis_bytes(src_text))
                
                # Perform diet logic
                final_text, initial_over_bytes = apply_diet(dst_text, max_bytes)
                
                # Log if data was truncated
                if initial_over_bytes > 0:
                    log_row = row.copy()
                    # Keep original Mapping text in log for reference
                    log_row['Mapping'] = dst_text 
                    log_row['ExceededBytes'] = f"{initial_over_bytes} bytes"
                    diet_log.append(log_row)
                
                # Inject mapped bytes into the bytearray
                final_bytes = get_sjis_bytes(final_text)
                padding_size = max_bytes - len(final_bytes)
                payload = final_bytes + b'\x00' * padding_size
                
                pac_data[offset:offset+max_bytes] = payload
                injected_count += 1
                
            except Exception as e:
                print(f"[Error] Offset {row.get('Offset')}: {e}")

    # Save the modified PAC file
    with open(output_pac, 'wb') as f_out:
        f_out.write(pac_data)

    # Save log for entries that required diet adjustment
    if diet_log:
        with open(log_csv, 'w', encoding='utf-8-sig', newline='') as f_log:
            # Add 'ExceededBytes' to the existing fieldnames
            output_fields = fieldnames + ['ExceededBytes']
            
            # quoting=csv.QUOTE_ALL ensures every field is enclosed in double quotes ""
            writer = csv.DictWriter(f_log, fieldnames=output_fields, quoting=csv.QUOTE_ALL)
            
            writer.writeheader()
            writer.writerows(diet_log)
        print(f"[*] Diet log saved with {len(diet_log)} entries.")

if __name__ == "__main__":
    main()