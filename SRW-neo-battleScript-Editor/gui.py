import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import csv
import sys

class SRWNeoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SRW NEO Localization Tool")
        self.root.geometry("1450x850")
        
        # Script Names
        self.file_script1 = '1event_extract_encode.py'
        self.file_script2_master = '2mapping_encode.py'
        self.file_script2_diet = '2mapping_encode2.py' # Diet 전용 매핑 스크립트
        self.file_script3 = '3inject.py'
        self.file_script4 = '4move.py'
        
        self.master_csv = 'msbtl_extracted_v2.csv'
        self.diet_csv = 'diet_applied_results.csv'

        self.current_editor_file = None
        self.data = []             # CSV Data
        self.display_indices = []  # Indices for search/filtering
        self.current_page = 0
        self.items_per_page = 10
        self.is_modified = False
        self.text_widgets = []     # Store current page widgets

        self.setup_ui()
        self.check_file_status()

    def setup_ui(self):
        # Layout (Left: Menu, Right: Editor)
        self.left_frame = tk.Frame(self.root, width=200, bg='#2C3E50')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # --- Left Menu ---
        btn_style = {'font': ('Arial', 11, 'bold'), 'width': 18, 'pady': 10}
        tk.Label(self.left_frame, text="[ MENU ]", fg='white', bg='#2C3E50', font=('Arial', 14, 'bold')).pack(pady=20)

        self.btn_extract = tk.Button(self.left_frame, text="1. Extract", command=lambda: self.run_script(self.file_script1), **btn_style)
        self.btn_extract.pack(pady=5)

        self.btn_master_edit = tk.Button(self.left_frame, text="2. Master Edit", command=lambda: self.open_editor(self.master_csv), **btn_style)
        self.btn_master_edit.pack(pady=5)

        self.btn_inject = tk.Button(self.left_frame, text="3. Inject", command=lambda: self.run_script(self.file_script3), **btn_style)
        self.btn_inject.pack(pady=5)

        self.btn_diet_edit = tk.Button(self.left_frame, text="4. Diet Edit", command=lambda: self.open_editor(self.diet_csv), **btn_style)
        self.btn_diet_edit.pack(pady=5)

        self.btn_sum = tk.Button(self.left_frame, text="5. Sum (Merge)", command=lambda: self.run_script(self.file_script4), **btn_style)
        self.btn_sum.pack(pady=5)

        tk.Button(self.left_frame, text="6. Exit", command=self.exit_app, fg='#E74C3C', **btn_style).pack(side=tk.BOTTOM, pady=20)

        # --- Right Editor Layout ---
        self.editor_top = tk.Frame(self.right_frame, bg='#ECF0F1')
        self.editor_content = tk.Frame(self.right_frame)
        self.editor_bottom = tk.Frame(self.right_frame, bg='#ECF0F1')
        
        self.lbl_editor_title = tk.Label(self.editor_top, text="", font=('Arial', 12, 'bold'), bg='#ECF0F1')
        self.lbl_editor_title.pack(side=tk.LEFT, padx=20, pady=10)

        search_frame = tk.Frame(self.editor_top, bg='#ECF0F1')
        search_frame.pack(side=tk.RIGHT, padx=20)
        tk.Label(search_frame, text="Search:", bg='#ECF0F1').pack(side=tk.LEFT)
        self.ent_search = tk.Entry(search_frame, width=30)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind('<Return>', lambda e: self.apply_search())
        tk.Button(search_frame, text="Search", command=self.apply_search).pack(side=tk.LEFT, padx=2)
        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)

        # Bottom Controls
        self.btn_prev = tk.Button(self.editor_bottom, text="◀ Prev", command=self.prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_page = tk.Label(self.editor_bottom, text="Page: 0 / 0", font=('Arial', 10, 'bold'), bg='#ECF0F1')
        self.lbl_page.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(self.editor_bottom, text="Next ▶", command=self.next_page)
        self.btn_next.pack(side=tk.LEFT, padx=10)

        tk.Label(self.editor_bottom, text="Go to Page:", bg='#ECF0F1').pack(side=tk.LEFT, padx=(20, 5))
        self.ent_page_jump = tk.Entry(self.editor_bottom, width=5)
        self.ent_page_jump.pack(side=tk.LEFT)
        tk.Button(self.editor_bottom, text="Go", command=self.jump_to_page).pack(side=tk.LEFT, padx=5)

        # Mapping 버튼 (Master/Diet 공용)
        self.btn_mapping_run = tk.Button(self.editor_bottom, text="Run Mapping", command=self.run_mapping_and_refresh, bg='#3498DB', fg='white', font=('Arial', 9, 'bold'))
        
        tk.Button(self.editor_bottom, text="Save", command=self.save_csv, font=('Arial', 10, 'bold'), fg='blue').pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(self.editor_bottom, text="Close Editor", command=self.close_editor, font=('Arial', 10, 'bold'), fg='red').pack(side=tk.RIGHT, padx=10, pady=10)

    def check_file_status(self):
        self.btn_master_edit['state'] = tk.NORMAL if os.path.exists(self.master_csv) else tk.DISABLED
        self.btn_diet_edit['state'] = tk.NORMAL if os.path.exists(self.diet_csv) else tk.DISABLED
        self.root.after(2000, self.check_file_status)

    def run_script(self, script_name):
        if not os.path.exists(script_name):
            messagebox.showerror("Error", f"'{script_name}' not found!")
            return
        try:
            result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, encoding='utf-8')
            output = result.stdout + "\n" + result.stderr
            self.show_popup(f"Results: {script_name}", output)
        except Exception as e:
            messagebox.showerror("Runtime Error", str(e))

    def show_popup(self, title, message):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("700x450")
        txt = tk.Text(top, wrap='word', font=('Consolas', 10))
        txt.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        txt.insert('1.0', message)
        txt.config(state=tk.DISABLED)
        tk.Button(top, text="Close", command=top.destroy, width=15).pack(pady=10)

    def open_editor(self, filename):
        if self.current_editor_file:
            self.save_page_edits()
        
        if self.is_modified:
            if not messagebox.askyesno("Warning", "Unsaved changes exist. Continue without saving?"):
                return
        
        self.text_widgets = []
        self.data = []
        self.is_modified = False
        self.current_editor_file = filename
        
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.fieldnames = reader.fieldnames
                self.data = [row for row in reader]
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
            return
        
        self.lbl_editor_title.config(text=f"Editing: {filename}")
        
        self.ent_search.delete(0, tk.END)
        self.display_indices = list(range(len(self.data)))
        self.current_page = 0
        
        self.editor_top.pack(fill=tk.X)
        self.editor_content.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.editor_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        # Diet에서도 Mapping 버튼을 항상 노출
        self.btn_mapping_run.pack(side=tk.LEFT, padx=30, after=self.btn_next)
            
        self.render_page()

    def apply_search(self):
        query = self.ent_search.get().strip().lower()
        if not query:
            self.clear_search()
            return
        
        self.save_page_edits()
        self.display_indices = [
            i for i, row in enumerate(self.data) 
            if query in row['Japanese'].lower() or query in row['Korean'].lower()
        ]
        self.current_page = 0
        if not self.display_indices:
            messagebox.showinfo("Search", "No results found.")
            self.clear_search()
        else:
            self.render_page()

    def clear_search(self):
        if self.current_editor_file:
            self.save_page_edits()
            self.ent_search.delete(0, tk.END)
            self.display_indices = list(range(len(self.data)))
            self.current_page = 0
            self.render_page()

    def jump_to_page(self):
        try:
            target = int(self.ent_page_jump.get()) - 1
            total_pages = (len(self.display_indices) - 1) // self.items_per_page + 1
            if 0 <= target < total_pages:
                self.save_page_edits()
                self.current_page = target
                self.render_page()
            else:
                messagebox.showwarning("Jump", "Invalid page number.")
        except ValueError:
            pass

    def render_page(self):
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        self.text_widgets = []
        total_items = len(self.display_indices)
        total_pages = (total_items - 1) // self.items_per_page + 1 if total_items > 0 else 1
        self.lbl_page.config(text=f"Page: {self.current_page + 1} / {total_pages}")
        
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, total_items)

        headers = ["No.", "Japanese (Read-only)", "Korean (Edit)", "Mapping (Read-only)", "Byte Info (JP vs Map)"]
        widths = [5, 30, 30, 30, 20]
        for c, h in enumerate(headers):
            tk.Label(self.editor_content, text=h, font=('Arial', 9, 'bold'), bg='#BDC3C7', relief=tk.RIDGE).grid(row=0, column=c, sticky="nsew", padx=1, pady=1)
            self.editor_content.grid_columnconfigure(c, weight=widths[c])

        for r, display_idx in enumerate(range(start, end), start=1):
            data_idx = self.display_indices[display_idx]
            row_data = self.data[data_idx]
            
            tk.Label(self.editor_content, text=str(data_idx + 1)).grid(row=r, column=0, sticky="nsew")
            
            # Japanese
            jp_txt = tk.Text(self.editor_content, height=3, width=30, bg='#F2F3F4')
            jp_txt.insert('1.0', row_data.get('Japanese', ''))
            jp_txt.config(state=tk.DISABLED)
            jp_txt.grid(row=r, column=1, sticky="nsew", padx=2, pady=2)
            
            # Byte Info (Japanese vs Mapping 비교)
            jp_b = len(row_data.get('Japanese', '').encode('shift_jis', errors='ignore'))
            map_b = len(row_data.get('Mapping', '').encode('shift_jis', errors='ignore'))
            diff = map_b - jp_b
            
            info_text = f"JP: {jp_b}B / Map: {map_b}B\n" + (f"Over: +{diff}B" if diff > 0 else f"Free: {abs(diff)}B")
            lbl_info = tk.Label(self.editor_content, text=info_text, fg=('red' if diff > 0 else 'blue'), font=('Arial', 8, 'bold'))
            lbl_info.grid(row=r, column=4, sticky="nsew")

            # Korean Edit
            kor_txt = tk.Text(self.editor_content, height=3, width=30, undo=True)
            kor_txt.insert('1.0', row_data.get('Korean', ''))
            kor_txt.grid(row=r, column=2, sticky="nsew", padx=2, pady=2)
            self.text_widgets.append((data_idx, kor_txt))
            
            # Mapping (Read-only)
            map_txt = tk.Text(self.editor_content, height=3, width=30, bg='#F2F3F4')
            map_txt.insert('1.0', row_data.get('Mapping', ''))
            map_txt.config(state=tk.DISABLED)
            map_txt.grid(row=r, column=3, sticky="nsew", padx=2, pady=2)

    def save_page_edits(self):
        if not self.text_widgets or not self.data:
            return
            
        for data_idx, text_widget in self.text_widgets:
            try:
                if data_idx < len(self.data):
                    new_val = text_widget.get("1.0", "end-1c")
                    if self.data[data_idx]['Korean'] != new_val:
                        self.data[data_idx]['Korean'] = new_val
                        self.is_modified = True
            except (IndexError, KeyError):
                continue

    def prev_page(self):
        if self.current_page > 0:
            self.save_page_edits()
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        if (self.current_page + 1) * self.items_per_page < len(self.display_indices):
            self.save_page_edits()
            self.current_page += 1
            self.render_page()

    def run_mapping_and_refresh(self):
        # 현재 페이지 수정사항 저장
        self.save_page_edits()
        self.save_csv(silent=True)
        
        # 파일 타입에 따른 스크립트 선택
        if self.current_editor_file == self.master_csv:
            script_to_run = self.file_script2_master
        else:
            script_to_run = self.file_script2_diet
            
        self.run_script(script_to_run)
        
        # Mapping 결과를 UI에 반영하기 위해 파일 다시 로드 및 렌더링
        # open_editor의 초기화 과정을 거치지 않고 데이터만 새로 읽음
        try:
            with open(self.current_editor_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.data = [row for row in reader]
            self.render_page()
            messagebox.showinfo("Success", f"Mapping completed using {script_to_run} and Byte Info updated.")
        except Exception as e:
            messagebox.showerror("Refresh Error", str(e))

    def save_csv(self, silent=False):
        self.save_page_edits()
        if not self.current_editor_file: return
        
        try:
            with open(self.current_editor_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(self.data)
            self.is_modified = False
            if not silent: messagebox.showinfo("Saved", f"Changes saved to {self.current_editor_file}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def close_editor(self):
        self.save_page_edits()
        if self.is_modified:
            if messagebox.askyesno("Save Changes?", "You have unsaved changes. Save before closing?"):
                self.save_csv()
        
        self.editor_top.pack_forget()
        self.editor_content.pack_forget()
        self.editor_bottom.pack_forget()
        self.text_widgets = []
        self.current_editor_file = None
        self.is_modified = False

    def exit_app(self):
        if self.current_editor_file and self.is_modified:
            if not messagebox.askyesno("Exit", "Unsaved changes exist. Exit anyway?"):
                return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SRWNeoEditorGUI(root)
    root.mainloop()