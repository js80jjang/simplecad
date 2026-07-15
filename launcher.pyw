import sys, traceback, os, runpy

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    runpy.run_path("ceramic_cost.py", run_name="__main__")
except SystemExit:
    pass
except Exception:
    err = traceback.format_exc()
    with open("error_log.txt", "w", encoding="utf-8") as f:
        f.write(err)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("실행 오류", err[:1000])
        root.destroy()
    except Exception as e2:
        pass
