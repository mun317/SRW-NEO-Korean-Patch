# User Manual: SRW NEO Localization Tool

This tool is a dedicated GUI designed to streamline the translation process for *Super Robot Wars NEO*. It manages the extraction, editing, mapping, and injection of text while ensuring byte compatibility with the original game files.

---

## 1. Workflow Overview
The localization process follows a numerical sequence. For a successful translation, follow the steps in the order listed on the menu.

1. **Extract** (Source Data)
2. **Master Edit** (Main Translation)
3. **Inject** (Initial Build)
4. **Diet Edit** (Optimization)
5. **Sum** (Final Synchronization)

---

## 2. Menu Functionality

### Step 1: Extract
- **Action:** Runs `1event_extract_encode.py`.
- **Purpose:** Extracts the original Japanese dialogue from the `event.pac` file and generates the `event_extracted_v2.csv` file.

### Step 2: Master Edit
- **Action:** Opens the Master Editor for `event_extracted_v2.csv`.
- **Purpose:** This is your primary translation workspace. You can enter Korean translations for each Japanese line.
- **Key Feature:** Use the **[Run Mapping]** button here to execute `2mapping_encode.py`. This converts your Korean text into font-mapped characters and calculates the final byte size.

### Step 3: Inject
- **Action:** Runs `3inject.py`.
- **Purpose:** Injects the current translations into a new PAC file. If a line exceeds the original byte limit, it will be logged for "Diet" (optimization).

### Step 4: Diet Edit
- **Action:** Opens the editor for `diet_applied_results.csv`.
- **Purpose:** Handles lines that failed the initial injection due to being **over-budget in bytes**.
- **Key Feature:** Use the **[Run Mapping]** button here to execute `2mapping_encode2.py`. It allows you to shorten the Korean text and verify immediately if it fits within the limit.

### Step 5: Sum (Merge)
- **Action:** Runs `4move.py`.
- **Purpose:** Merges the optimized "Diet" translations back into the master database to ensure all changes are synchronized for the final build.
Note:
Step 5: Sum (Merge) updates the CSV database. After running this step, you must run Step 3: Inject again. If the "Diet" file is not generated (or is empty) after this final injection, it means no sentences exceed the byte limit. The complete cycle should be: Edit (Step 4) → Sum (Step 5) → Verify in Master Edit (Step 2) → Finalize with Inject (Step 3).
---

## 3. Editor Features & Controls

| Feature | Description |
| :--- | :--- |
| **Search** | Filter rows by Japanese or Korean keywords. Press **Enter** or click **Search**. |
| **Byte Info** | Displays **JP (Original)** vs **Map (Current)** bytes. Red indicates the text is too long. |
| **Run Mapping** | Saves current progress and updates the "Mapping" column and "Byte Info" based on your latest edits. |
| **Go to Page** | Quickly navigate through large files by entering a page number. |
| **Undo (Ctrl+Z)** | Supported within the Korean text edit fields. |

---

## 4. Important Tips for Translators

- **Byte Constraints:** The "Map" bytes must be less than or equal to the "JP" bytes. The game cannot accept text longer than the original data.
- **Saving:** Always click **[Save]** before closing the editor or switching between Master and Diet modes. 
- **Script Dependency:** Ensure all `.py` scripts and the `font1_charmap_table_kor.json` file are in the same folder as the GUI.
- **Multi-line Support:** The editor supports multi-line dialogues. Ensure you maintain the correct structure for the game to display them properly.

---

## 5. Troubleshooting
- **IndexError:** If you encounter a range error, simply close and reopen the editor. The latest version includes safeguards to prevent this.
- **Button Disabled:** If "Master Edit" or "Diet Edit" buttons are greyed out, it means the corresponding `.csv` files have not been generated yet. Run the previous steps first.

---
*Happy Translating!*
