import webview as wv
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from multiprocessing import Process, Queue
from queue import Empty, Full

try:
    import ctypes
    from hidpi_tk import DPIAwareTk
    tk.Tk = DPIAwareTk
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass
    
from complx.pickled import search, is_reachable, SHOWN, LOADED # separate module for pickle reasons
from complx.focus import steal_focus

class App(tk.Tk):
    """Entry point"""
    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.title('ComplX')
        self.wm_iconbitmap(str(Path(__file__).resolve().parent / 'icon.ico'))
        
        self.address = tk.StringVar(value='')
        
        self.draw()
        self.position()
    
    def draw(self):
        self.titlebar = ttk.Frame(self)
        self.titlebar.pack(fill='x', expand=True, padx=5, pady=5)
        
        self.title = ttk.Label(self.titlebar, text='ComplX Browser', anchor='center', justify='center', font=("Segoe UI", 12, "bold"))
        self.title.pack(fill='x', expand=True, pady=2)
        
        self.desc = ttk.Label(self.titlebar, text='The only browser you\'ll ever need', anchor='center', justify='center')
        self.desc.pack(fill='x', expand=True, pady=2)
        
        self.searchbar = ttk.Frame(self)
        self.searchbar.pack(padx=5, pady=5)
        
        self.searchbox = ttk.Entry(self.searchbar, textvariable=self.address)
        self.searchbox.pack(side=tk.LEFT, padx=(7, 2), pady=2)
        self.searchbox.bind('<Return>', lambda e: self.searchbtn.invoke())
        steal_focus(self, self.searchbox)
        
        self.searchbtn = ttk.Button(self.searchbar, text='Search', command=self.run)
        self.searchbtn.pack(side=tk.LEFT, padx=(2, 7), pady=2)
        
        self.errorbar = ttk.Frame(self)
        self.error_label = tk.Label(self.errorbar, text='')
        
        self.bind('<Button-1>', lambda e: self.focus_force() if e.widget != self.searchbox else None)
        
    def position(self):
        self.update_idletasks()
        
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        
        self.wm_geometry(f"{width}x{height}+{x}+{y}") # use `wm_geometry` instead of `geometry` due to DPI awareness
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())
        self.deiconify()
    
    def show_msg(self, msg, col='black'):
        if not self.errorbar.winfo_ismapped():
            self.errorbar.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        if not self.error_label.winfo_ismapped():
            self.error_label.pack(pady=2)
        self.error_label.configure(text=msg, fg=col)
        self.position()
        self.update_idletasks()
        
    def hide_msg(self):
        self.errorbar.pack_forget()
        self.error_label.pack_forget()
        self.position()
        self.update_idletasks()
    
    def _search(self, url):
        self.search_q = Queue()
        self.search_proc = Process(target=search, args=(url,self.search_q), daemon=True)
        self.search_proc.start()
        
    def _reach(self, url):
        self.reach_q = Queue()
        self.reach_proc = Process(target=is_reachable, args=(url,self.reach_q), daemon=True)
        self.reach_proc.start()
    
    def _run(self):
        url = self.address.get().strip()
        if not url:
            self.show_msg('Please enter a URL', col='red')
            return
        
        self._reach(url)
        self.show_msg('Trying to reach the URL', col='blue')
        reachable = self.reach_q.get()
        
        if reachable:
            self.show_msg('URL reached', col='green')
            self._search(url)
            self.show_msg('Creating window...', col='blue')
            for _ in range(2):
                try:
                    item = self.search_q.get()
                    if item == SHOWN:
                        self.show_msg('Window created; loading...', col='blue')
                    elif item == LOADED:
                        self.show_msg('Webpage loaded', col='green')
                    else:
                        print('Unknown item')
                        return
                except Empty:
                    print('Expected more items')
                    return
        else:
            self.show_msg('URL not reachable or does not exist', col='red')
            return
    
    def run(self):
        self._run()
        steal_focus(self, self.searchbox)
        
        
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support() # essential
    
    a = App()
    a.mainloop()
    # Test url: https://google.com