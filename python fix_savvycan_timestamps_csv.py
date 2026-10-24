import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# --- Defaults (editable in the GUI) ---
DEFAULT_FRAME_ID = "000002C3"
DEFAULT_PERIOD_MS = 100
# --------------------------------------


def fix_csv(input_path, output_path, frame_id, period_us):
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    ts_idx = None
    for i, col in enumerate(header):
        if col.strip().lower() == "time stamp":
            ts_idx = i
            break
    if ts_idx is None:
        raise ValueError("Column 'Time Stamp' not found in CSV header.")

    id_idx = None
    for i, col in enumerate(header):
        if col.strip().lower() == "id":
            id_idx = i
            break
    if id_idx is None:
        raise ValueError("Column 'ID' not found in CSV header.")

    current_time = 0
    anchor_count = 0
    for row in rows:
        if len(row) <= max(ts_idx, id_idx):
            continue

        row_id = row[id_idx].strip().upper()
        if row_id == frame_id.upper():
            row[ts_idx] = str(current_time)
            current_time += period_us
            anchor_count += 1
        else:
            row[ts_idx] = str(current_time - period_us if anchor_count > 0 else 0)

    if anchor_count == 0:
        raise ValueError(
            f"No frame with ID {frame_id} found in the file. "
            "Check that the ID is correct."
        )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    return anchor_count


def run_gui():
    root = tk.Tk()
    root.title("Fix SavvyCAN Timestamps")
    root.geometry("560x380")
    root.resizable(False, False)

    input_var = tk.StringVar()
    output_var = tk.StringVar()
    frame_id_var = tk.StringVar(value=DEFAULT_FRAME_ID)
    period_ms_var = tk.StringVar(value=str(DEFAULT_PERIOD_MS))

    def choose_input():
        path = filedialog.askopenfilename(
            title="Select SavvyCAN CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            input_var.set(path)
            base, ext = os.path.splitext(path)
            output_var.set(base + "_fixed" + ext)

    def choose_output():
        path = filedialog.asksaveasfilename(
            title="Save fixed CSV as",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            output_var.set(path)

    def do_fix():
        inp = input_var.get().strip()
        out = output_var.get().strip()
        frame_id = frame_id_var.get().strip()
        period_str = period_ms_var.get().strip()

        if not inp or not os.path.isfile(inp):
            messagebox.showerror("Error", "Please select an existing input CSV file.")
            return
        if not out:
            messagebox.showerror("Error", "Please choose an output file path.")
            return
        if os.path.abspath(inp) == os.path.abspath(out):
            messagebox.showerror("Error", "Output file cannot be the same as the input file.")
            return
        if not frame_id:
            messagebox.showerror("Error", "Reference frame ID cannot be empty.")
            return
        try:
            period_ms = float(period_str)
            if period_ms <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Period must be a positive number (ms).")
            return

        period_us = int(round(period_ms * 1000))
        try:
            anchors = fix_csv(inp, out, frame_id, period_us)
            messagebox.showinfo(
                "Success",
                f"Timestamps fixed.\n\n"
                f"Reference frame: {frame_id} every {period_ms:g} ms\n"
                f"Found {anchors} reference frames.\n"
                f"Saved to:\n{out}"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Layout ---
    tk.Label(
        root,
        text=(
            "Select a SavvyCAN CSV log and click Fix Timestamps. "
            "Frames matching the reference ID are used as time anchors "
            "spaced by the given period, and all other frames get the "
            "time of the preceding anchor."
        ),
        wraplength=530, justify="left", fg="#333"
    ).pack(anchor="w", padx=10, pady=(12, 8))

    tk.Label(root, text="Input CSV file:").pack(anchor="w", padx=10)
    frame_in = tk.Frame(root)
    frame_in.pack(fill="x", padx=10)
    tk.Entry(frame_in, textvariable=input_var).pack(side="left", fill="x", expand=True)
    tk.Button(frame_in, text="Browse...", command=choose_input).pack(side="left", padx=(6, 0))

    tk.Label(root, text="Output CSV file:").pack(anchor="w", padx=10, pady=(10, 0))
    frame_out = tk.Frame(root)
    frame_out.pack(fill="x", padx=10)
    tk.Entry(frame_out, textvariable=output_var).pack(side="left", fill="x", expand=True)
    tk.Button(frame_out, text="Save as...", command=choose_output).pack(side="left", padx=(6, 0))

    # --- Reference frame + period ---
    frame_params = tk.Frame(root)
    frame_params.pack(fill="x", padx=10, pady=(12, 0))

    tk.Label(frame_params, text="Reference frame ID:").grid(row=0, column=0, sticky="w")
    tk.Entry(frame_params, textvariable=frame_id_var, width=14).grid(row=0, column=1, sticky="w", padx=(6, 20))

    tk.Label(frame_params, text="Period (ms):").grid(row=0, column=2, sticky="w")
    tk.Entry(frame_params, textvariable=period_ms_var, width=8).grid(row=0, column=3, sticky="w", padx=(6, 0))

    tk.Button(root, text="Fix Timestamps", command=do_fix, height=2).pack(
        fill="x", padx=10, pady=14
    )

    root.mainloop()


if __name__ == "__main__":
    run_gui()
