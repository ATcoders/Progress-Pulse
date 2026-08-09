import tkinter as tk
from tkinter import messagebox
import database
import App

# ---------------------------------------------------------------------------
# Colors — modern dark theme matching the Task Planner's accent color
# ---------------------------------------------------------------------------
BG_COLOR = "#12121f"
CARD_COLOR = "#1c1c2e"
ACCENT_COLOR = "#4D3EEF"
ACCENT_HOVER = "#6a5cf5"
TEXT_COLOR = "#ffffff"
MUTED_COLOR = "#8a8aa3"
ENTRY_BG = "#0f0f1c"
ERROR_COLOR = "#ff6b6b"

database.create_users_table()

root = tk.Tk()
root.title("Task Planner — Login")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

# Center the window at 38% width x 60% height of the screen (well under half)
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
win_w = int(screen_w * 0.38)
win_h = int(screen_h * 0.65)
pos_x = (screen_w - win_w) // 2
pos_y = (screen_h - win_h) // 2
root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

mode = "login"  # switches to "signup" when the user clicks the toggle link

# ---------------------------------------------------------------------------
# Card (the centered panel that holds the form)
# ---------------------------------------------------------------------------
card = tk.Frame(root, bg=CARD_COLOR)
card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.9)

title_label = tk.Label(card, text="Welcome Back", font=("Segoe UI", 22, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
title_label.pack(pady=(35, 4))

subtitle_label = tk.Label(card, text="Login to continue to Task Planner",
                           font=("Segoe UI", 11), bg=CARD_COLOR, fg=MUTED_COLOR)
subtitle_label.pack(pady=(0, 25))


def make_field(label_text):
    """Creates a labeled entry field and returns the Entry widget."""
    tk.Label(card, text=label_text, font=("Segoe UI", 10), bg=CARD_COLOR, fg=MUTED_COLOR, anchor="w") \
        .pack(fill="x", padx=45)
    entry = tk.Entry(card, font=("Segoe UI", 12), bg=ENTRY_BG, fg=TEXT_COLOR,
                      insertbackground=TEXT_COLOR, relief="flat")
    entry.pack(fill="x", padx=45, pady=(3, 14), ipady=9)
    return entry


username_entry = make_field("Username")
password_entry = make_field("Password")
password_entry.config(show="•")

# Confirm-password field exists but is only shown in signup mode
confirm_label = tk.Label(card, text="Confirm Password", font=("Segoe UI", 10),
                          bg=CARD_COLOR, fg=MUTED_COLOR, anchor="w")
confirm_entry = tk.Entry(card, font=("Segoe UI", 12), bg=ENTRY_BG, fg=TEXT_COLOR,
                          insertbackground=TEXT_COLOR, relief="flat", show="•")

error_label = tk.Label(card, text="", font=("Segoe UI", 9), bg=CARD_COLOR, fg=ERROR_COLOR)
error_label.pack(pady=(2, 0))


def show_error(message):
    error_label.config(text=message)


def clear_error():
    error_label.config(text="")


def handle_submit():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        show_error("Please fill in all fields")
        return

    if mode == "login":
        if database.verify_login(username, password):
            root.destroy()
            App.launch_task_planner()
        else:
            show_error("Invalid username or password")
    else:
        confirm = confirm_entry.get().strip()
        if password != confirm:
            show_error("Passwords do not match")
            return
        if database.username_exists(username):
            show_error("That username is already taken")
            return

        database.signup_user(username, password)
        messagebox.showinfo("Account Created", "Your account was created. Please log in.")
        switch_mode("login")


submit_btn = tk.Button(card, text="Login", font=("Segoe UI", 12, "bold"), bg=ACCENT_COLOR, fg="white",
                        bd=0, cursor="hand2", command=handle_submit)
submit_btn.pack(fill="x", padx=45, pady=(12, 12), ipady=9)

# Simple hover effect on the main button
submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg=ACCENT_HOVER))
submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg=ACCENT_COLOR))

switch_label = tk.Label(card, text="Don't have an account?  Sign Up",
                         font=("Segoe UI", 10, "underline"), bg=CARD_COLOR, fg=ACCENT_COLOR, cursor="hand2")
switch_label.pack(pady=(0, 20))


def switch_mode(new_mode):
    global mode
    mode = new_mode
    clear_error()
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    confirm_entry.delete(0, tk.END)

    if mode == "login":
        title_label.config(text="Welcome Back")
        subtitle_label.config(text="Login to continue to Task Planner")
        submit_btn.config(text="Login")
        switch_label.config(text="Don't have an account?  Sign Up")
        confirm_label.pack_forget()
        confirm_entry.pack_forget()
    else:
        title_label.config(text="Create Account")
        subtitle_label.config(text="Sign up to start planning your tasks")
        submit_btn.config(text="Sign Up")
        switch_label.config(text="Already have an account?  Login")
        confirm_label.pack(fill="x", padx=45, before=error_label)
        confirm_entry.pack(fill="x", padx=45, pady=(3, 14), ipady=9, before=error_label)


def toggle_mode(event=None):
    switch_mode("signup" if mode == "login" else "login")


switch_label.bind("<Button-1>", toggle_mode)

# Let the user press Enter to submit from either password field
password_entry.bind("<Return>", lambda e: handle_submit())
confirm_entry.bind("<Return>", lambda e: handle_submit())

root.mainloop()