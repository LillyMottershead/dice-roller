import tkinter as tk
from tkinter import font
from dice_parser import parse_command_tuple_wrapper

BG = '#0a0a0a'
alias_to_button = {}
command_stack_older = []
command_stack_newer = []
command_on = ''

window = tk.Tk()
window.columnconfigure(0, weight=1, minsize=200)
window.columnconfigure(1, weight=0, minsize=100)
window.rowconfigure(0, weight=1, minsize=300)
window.configure(bg=BG)
default_font = font.nametofont('TkDefaultFont')
default_font.configure(size=14)

log_frame = tk.Frame(
    bg=BG)
log_frame.grid(
    column=0,
    row=0,
    sticky='sw',)
log_frame_inner = tk.Frame(
    master=log_frame)
log_frame_inner.pack(
    fill=tk.X,
    anchor='sw')
log_textbox = tk.Text(
    master=log_frame_inner,
    state='disabled',
    fg='lightgrey',
    bg=BG,
    font=default_font)
log_textbox.pack()

alias_frame = tk.Frame(
    bg=BG)
alias_label = tk.Label(
    master=alias_frame,
    text='Aliases:',
    bg=BG,
    fg='lightgrey',
    justify='left')
alias_frame.grid(
    column=1,
    row=0,
    sticky='nw')
alias_label.pack()

entry_frame = tk.Frame(
    bg=BG)
entry = tk.Entry(
    master=entry_frame,
    fg='white',
    bg=BG,
    width=50,
    font=default_font)
entry_frame.grid(
    column=0,
    row=1,
    columnspan=2,
    sticky='nesw')
entry.pack(
    fill=tk.X)
entry.focus()


def enter_entry(event):
    global command_on
    command = entry.get()
    if command is not None or command != '':
        command_on = ''
        for historic_command in reversed(command_stack_newer[1:]):
            command_stack_older.append(historic_command)
        command_stack_older.append(command)
        command_stack_newer.clear()

    output, *options = output_roll_result(command)
    alias = options[0] if len(options) > 0 else None
    to_delete = options[1] if len(options) > 1 else False
    entry.delete(0, tk.END)

    if to_delete:
        alias_to_button[alias].destroy()
    elif alias is not None:
        if alias in alias_to_button and alias_to_button[alias] is not None:
            alias_to_button[alias].destroy()
        alias_to_button[alias] = tk.Button(
            master=alias_frame,
            text=alias,
            fg='lightgrey',
            bg='#383838',
            command=lambda: output_roll_result(alias))
        alias_to_button[alias].pack()


def output_roll_result(command):
    log_textbox.configure(state='normal')
    output, *options = parse_command_tuple_wrapper(command)
    log_textbox.insert(tk.END, str(output))
    log_textbox.insert(tk.END, '\n')
    log_textbox.configure(state='disabled')
    return output, *options


def clear_log(event):
    log_textbox.configure(state='normal')
    log_textbox.delete('1.0', tk.END)
    log_textbox.configure(state='disabled')


def close_window(event):
    window.destroy()


def command_history_up(event):
    global command_on
    if len(command_stack_older) > 0:
        entry.delete(0, tk.END)
        command_stack_newer.append(command_on)
        command_on = command_stack_older.pop()
        entry.insert(0, command_on)


def command_history_down(event):
    global command_on
    entry.delete(0, tk.END)
    if len(command_stack_newer) > 0 and command_on != '':
        command_stack_older.append(command_on)
        command_on = command_stack_newer.pop()
        entry.insert(0, command_on)


window.bind("<Return>", enter_entry)
window.bind('<Delete>', clear_log)
window.bind('<Escape>', close_window)
window.bind('<Up>', command_history_up)
window.bind('<Down>', command_history_down)
window.mainloop()
