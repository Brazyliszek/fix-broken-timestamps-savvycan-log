# Fix SavvyCAN Timestamps

A small GUI tool that repairs corrupted `Time Stamp` values in CSV logs exported from **SavvyCAN**.

![Showoff screen](https://github.com/Brazyliszek/fix-broken-timestamps-savvycan-log/blob/main/example.jpg?raw=true)

## The problem

SavvyCAN has a known bug where received CAN frames (especially over serial/SLCAN interfaces) are written to CSV with **huge negative timestamps** (e.g. `-1788895826027060`). The original timing information is lost — the values are the result of a parsing error and cannot be reversed.

However, if you know that a particular frame arrives at a **fixed period** (for example, `0x2C3` every 100 ms), those frames can be used as **timing anchors** to rebuild a usable, evenly-spaced timeline.

## How it works

1. The CSV is loaded and its **row order is preserved** — this is assumed to be the real chronological order of reception (always true for SavvyCAN logs). The corrupted timestamps themselves are never used.
2. Every row whose `ID` matches the **reference frame ID** becomes a timing **anchor**.
3. New timestamps are assigned in **microseconds** (the unit SavvyCAN expects):
   - 1st anchor → `0`
   - 2nd anchor → `period` (e.g. `100000` µs for 100 ms)
   - 3rd anchor → `2 × period`, and so on.
4. **All other frames get the timestamp of the preceding anchor** — frames are "snapped" to the nearest earlier reference tick. Frames before the first anchor get `0`.
5. The result is written to a **new file**. Only the `Time Stamp` column is modified — no columns are added or removed, so the file opens in SavvyCAN without any format changes. The original input file is never overwritten.

## Requirements

- Python 3.7+
- Tkinter (bundled with standard Python on Windows/macOS; on Linux install `python3-tk`)

No third-party packages are needed.

## Usage

1. Run the script:

   ```bash
   python fix_savvycan_timestamps_csv.py
