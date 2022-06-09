"""-"""
import re

# from tkinter import Tk
import tkinter as tk

import wss_command_list as wsscl
import wss_global_hotkey as wssgh

com_list = wsscl.commands_dict.keys()


class MyApp(object):
    """-"""

    def __init__(self, parent):
        self.root = parent

        self.entry = AutocompleteEntry(com_list, root, width=300)
        self.entry.pack(side=tk.TOP)
        self.entry.focus()

        # HotKeys
        hkl = wssgh.HotKeylistener()
        listener = hkl.get_keyboard()
        hkl.generate_add_hotkeys("<cmd>+0+s", self.show_frame)
        hkl.generate_add_hotkeys("<cmd>+0+h", self.hide_frame)
        listener.start()

    def show_frame(self):
        """-"""
        self.root.update()
        self.root.deiconify()
        self.root.focus_force()
        self.entry.delete(0, "end")
        self.entry.focus()

    def hide_frame(self):
        """-"""
        self.root.update()
        self.root.withdraw()
        self.root.focus_force()


class AutocompleteEntry(tk.Entry):
    """Main window"""

    def __init__(self, com_list_in, *args, **kwargs):

        tk.Entry.__init__(self, *args, **kwargs)
        self.com_list = com_list_in
        self.var = self["textvariable"]
        if self.var == "":
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace("w", self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        # self.bind("<Escape>", self.root.destroy)

        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == "":
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = tk.Listbox(width=300)
                    # self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.bind("<Return>", self.selection)
                    self.lb.place(
                        x=self.winfo_x(), y=self.winfo_y() + self.winfo_height()
                    )
                    self.lb_up = True

                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):
        """-"""
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

            wsscl.main_handler_commands(self.var.get())
            self.var.set("")

    def up(self, event):
        """-"""
        if self.lb_up:
            if self.lb.curselection() == ():
                index = "0"
            else:
                index = self.lb.curselection()[0]
            if index != "0":
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):
        """-"""
        if self.lb_up:
            if self.lb.curselection() == ():
                index = "0"
            else:
                index = self.lb.curselection()[0]
            if index != tk.END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        in_str = self.var.get().lower()
        arr_str = list(in_str)
        pattern_str = ".*".join(arr_str)
        pattern = re.compile(".*" + pattern_str + ".*")
        return [w for w in self.com_list if re.match(pattern, w.lower())]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("WSS")
    root.geometry("400x200")
    app = MyApp(root)
    root.mainloop()
