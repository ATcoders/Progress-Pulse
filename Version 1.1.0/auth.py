import tkinter as tk
from tkinter import messagebox
import database

# ---------------------------------------------------------------------------
# Theme — matches the Task Planner's teal/near-black theme, so login and
# the app feel like one product.
# ---------------------------------------------------------------------------
APP_BG = "#080B10"
CARD_BG = "#101820"
FIELD_BG = "#0B1116"
BORDER_COLOR = "#1E2C2A"

ACCENT = "#22EFC0"
ACCENT_HOVER = "#5FFFDA"
ACCENT_DARK_TEXT = "#08120F"

TEXT_PRIMARY = "#EAFBF7"
TEXT_MUTED = "#6F8B87"
ERROR_COLOR = "#FF6B85"

FONT = "Segoe UI"


def show_login_window():
    """
    Builds and runs the Login / Signup window. Wrapped in a function (instead
    of running at import time) so it can be called again after a Logout,
    without needing to restart the whole program.
    """
    import main  # local import: avoids a circular import with main.py

    database.create_users_table()

    root = tk.Tk()
    root.title("Task Planner \u2014 Login")
    root.configure(bg=APP_BG)
    root.resizable(False, False)

    # FIX: the window used to be a fixed, generously-tall size so the
    # signup form would always fit — but that left login mode (which
    # needs far less space) sitting in a mostly-empty window. Instead,
    # the window now sizes itself to whatever content is actually
    # visible, via resize_to_fit() below, and re-sizes itself again each
    # time the mode is toggled between login and signup.
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    win_w = int(screen_w * 0.38)
    placeholder_h = 480
    pos_x = (screen_w - win_w) // 2
    pos_y = (screen_h - placeholder_h) // 2
    root.geometry(f"{win_w}x{placeholder_h}+{pos_x}+{pos_y}")

    def resize_to_fit():
        """Shrinks/grows the window to fit exactly what's currently
        visible (login fields only, or login + signup fields), instead
        of always reserving space for the taller signup form."""
        root.update_idletasks()
        req_h = root.winfo_reqheight()
        new_h = min(req_h, screen_h - 80)
        new_pos_x = (screen_w - win_w) // 2
        new_pos_y = max((screen_h - new_h) // 2, 20)
        root.geometry(f"{win_w}x{new_h}+{new_pos_x}+{new_pos_y}")

    mode = "login"  # switches to "signup" when the user clicks the toggle link

    # -----------------------------------------------------------------
    # Header — small brand mark above the card
    # -----------------------------------------------------------------
    header = tk.Frame(root, bg=APP_BG)
    header.pack(pady=(26, 6))

    tk.Label(header, text="\U0001F4CB", font=(FONT, 30), bg=APP_BG, fg=ACCENT).pack()
    tk.Label(header, text="TASK PLANNER", font=(FONT, 15, "bold"), bg=APP_BG, fg=TEXT_PRIMARY) \
        .pack(pady=(2, 0))
    tk.Label(header, text="Plan your days. Track your progress.", font=(FONT, 9), bg=APP_BG, fg=TEXT_MUTED) \
        .pack(pady=(1, 0))

    # -----------------------------------------------------------------
    # Card — glowing accent border wrapper + inner dark card
    # -----------------------------------------------------------------
    glow = tk.Frame(root, bg=ACCENT)
    glow.pack(pady=(14, 10), padx=int(win_w * 0.06), fill="both", expand=True)

    card = tk.Frame(glow, bg=CARD_BG)
    card.pack(fill="both", expand=True, padx=1, pady=1)

    body = tk.Frame(card, bg=CARD_BG)
    body.pack(fill="both", expand=True, padx=6, pady=6)

    title_label = tk.Label(body, text="Welcome Back", font=(FONT, 20, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY)
    title_label.pack(pady=(22, 2))

    subtitle_label = tk.Label(body, text="Login to continue to Task Planner",
                               font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED)
    subtitle_label.pack(pady=(0, 18))

    def make_field(parent, icon_and_label):
        label = tk.Label(parent, text=icon_and_label, font=(FONT, 9, "bold"), bg=CARD_BG, fg=TEXT_MUTED, anchor="w")
        label.pack(fill="x", padx=40)

        wrapper = tk.Frame(parent, bg=BORDER_COLOR)
        wrapper.pack(fill="x", padx=40, pady=(4, 12))
        entry = tk.Entry(wrapper, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                          insertbackground=ACCENT, relief="flat", bd=0)
        entry.pack(fill="x", padx=1, pady=1, ipady=9)

        # Highlight the field's border in accent color while it's focused
        entry.bind("<FocusIn>", lambda e: wrapper.config(bg=ACCENT))
        entry.bind("<FocusOut>", lambda e: wrapper.config(bg=BORDER_COLOR))
        return label, wrapper, entry

    # Full Name field only appears in signup mode
    fullname_label = tk.Label(body, text="\U0001F4DB  FULL NAME", font=(FONT, 9, "bold"),
                               bg=CARD_BG, fg=TEXT_MUTED, anchor="w")
    fullname_wrapper = tk.Frame(body, bg=BORDER_COLOR)
    fullname_entry = tk.Entry(fullname_wrapper, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                               insertbackground=ACCENT, relief="flat", bd=0)
    # FIX: this entry was created but never packed into its wrapper frame,
    # so it never appeared on screen and couldn't be typed into. That was
    # the "can't enter name" bug.
    fullname_entry.pack(fill="x", padx=1, pady=1, ipady=9)
    fullname_entry.bind("<FocusIn>", lambda e: fullname_wrapper.config(bg=ACCENT))
    fullname_entry.bind("<FocusOut>", lambda e: fullname_wrapper.config(bg=BORDER_COLOR))

    username_label, username_wrapper, username_entry = make_field(body, "\U0001F464  USERNAME")
    password_label, password_wrapper, password_entry = make_field(body, "\U0001F512  PASSWORD")
    password_entry.config(show="\u2022")

    # Confirm-password field only appears in signup mode
    confirm_label = tk.Label(body, text="\U0001F512  CONFIRM PASSWORD", font=(FONT, 9, "bold"),
                              bg=CARD_BG, fg=TEXT_MUTED, anchor="w")
    confirm_wrapper = tk.Frame(body, bg=BORDER_COLOR)
    confirm_entry = tk.Entry(confirm_wrapper, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                              insertbackground=ACCENT, relief="flat", bd=0, show="\u2022")
    confirm_entry.bind("<FocusIn>", lambda e: confirm_wrapper.config(bg=ACCENT))
    confirm_entry.bind("<FocusOut>", lambda e: confirm_wrapper.config(bg=BORDER_COLOR))

    error_label = tk.Label(body, text="", font=(FONT, 9), bg=CARD_BG, fg=ERROR_COLOR)
    error_label.pack(pady=(0, 2))

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
                main.launch_task_planner(username)
            else:
                show_error("Invalid username or password")
        else:
            full_name = fullname_entry.get().strip()
            confirm = confirm_entry.get().strip()

            if not full_name:
                show_error("Please enter your full name")
                return
            if password != confirm:
                show_error("Passwords do not match")
                return
            if database.username_exists(username):
                show_error("That username is already taken")
                return

            database.signup_user(username, full_name, password)
            messagebox.showinfo("Account Created", "Your account was created. Please log in.")
            switch_mode("login")

    submit_btn = tk.Button(body, text="Login", font=(FONT, 12, "bold"), bg=ACCENT, fg=ACCENT_DARK_TEXT,
                            bd=0, cursor="hand2", activebackground=ACCENT_HOVER, activeforeground=ACCENT_DARK_TEXT,
                            command=handle_submit)
    submit_btn.pack(fill="x", padx=40, pady=(6, 10), ipady=10)
    submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg=ACCENT_HOVER))
    submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg=ACCENT))

    # FIX: this was a plain Label before — it worked as a click target but
    # didn't read as a button and could get clipped off a too-short window.
    # Now it's a real Button, and the taller window above guarantees it's
    # always visible. In signup mode its label doubles as the explicit
    # "back to login" control that was requested.
    switch_btn = tk.Button(body, text="Don't have an account?  Sign Up",
                            font=(FONT, 10, "bold"), bg=CARD_BG, fg=ACCENT, bd=0,
                            cursor="hand2", activebackground=CARD_BG, activeforeground=ACCENT_HOVER)
    switch_btn.pack(pady=(0, 4))
    switch_btn.bind("<Enter>", lambda e: switch_btn.config(fg=ACCENT_HOVER))
    switch_btn.bind("<Leave>", lambda e: switch_btn.config(fg=ACCENT))

    forgot_label = tk.Label(body, text="Forgot Password?",
                             font=(FONT, 9, "underline"), bg=CARD_BG, fg=TEXT_MUTED, cursor="hand2")
    forgot_label.pack(pady=(0, 18))

    def switch_mode(new_mode):
        nonlocal mode
        mode = new_mode
        clear_error()
        fullname_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)

        if mode == "login":
            title_label.config(text="Welcome Back")
            subtitle_label.config(text="Login to continue to Task Planner")
            submit_btn.config(text="Login")
            switch_btn.config(text="Don't have an account?  Sign Up")
            forgot_label.pack(pady=(0, 18))
            fullname_label.pack_forget()
            fullname_wrapper.pack_forget()
            confirm_label.pack_forget()
            confirm_wrapper.pack_forget()
        else:
            title_label.config(text="Create Account")
            subtitle_label.config(text="Sign up to start planning your tasks")
            submit_btn.config(text="Sign Up")
            switch_btn.config(text="\u2190  Back to Login")
            forgot_label.pack_forget()

            fullname_label.pack(fill="x", padx=40, before=username_label)
            fullname_wrapper.pack(fill="x", padx=40, pady=(4, 12), before=username_label)

            confirm_label.pack(fill="x", padx=40, before=error_label)
            confirm_wrapper.pack(fill="x", padx=40, pady=(4, 12), before=error_label)

        resize_to_fit()

    def toggle_mode(event=None):
        switch_mode("signup" if mode == "login" else "login")

    switch_btn.config(command=toggle_mode)

    password_entry.bind("<Return>", lambda e: handle_submit())
    confirm_entry.bind("<Return>", lambda e: handle_submit())

    # -----------------------------------------------------------------
    # Forgot Password flow: username -> verify it exists -> set new password
    # -----------------------------------------------------------------

    def center_dialog(win, width, height):
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def open_forgot_password_dialog():
        dialog = tk.Toplevel(root)
        dialog.title("Reset Password")
        dialog.configure(bg=CARD_BG)
        center_dialog(dialog, 340, 300)
        dialog.transient(root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="Reset Password", font=(FONT, 16, "bold"),
                 bg=CARD_BG, fg=TEXT_PRIMARY).pack(pady=(25, 4))
        tk.Label(dialog, text="Enter your username to continue", font=(FONT, 10),
                 bg=CARD_BG, fg=TEXT_MUTED).pack(pady=(0, 15))

        tk.Label(dialog, text="Username", font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
            .pack(fill="x", padx=35)
        user_entry = tk.Entry(dialog, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                               insertbackground=ACCENT, relief="flat")
        user_entry.pack(fill="x", padx=35, pady=(3, 10), ipady=8)

        dlg_error = tk.Label(dialog, text="", font=(FONT, 9), bg=CARD_BG, fg=ERROR_COLOR)
        dlg_error.pack()

        def proceed():
            username = user_entry.get().strip()
            if not username:
                dlg_error.config(text="Please enter your username")
                return
            if not database.username_exists(username):
                dlg_error.config(text="No account found with that username")
                return
            dialog.destroy()
            open_new_password_dialog(username)

        next_btn = tk.Button(dialog, text="Continue", font=(FONT, 12, "bold"),
                              bg=ACCENT, fg=ACCENT_DARK_TEXT, bd=0, cursor="hand2", command=proceed)
        next_btn.pack(fill="x", padx=35, pady=(12, 20), ipady=8)
        next_btn.bind("<Enter>", lambda e: next_btn.config(bg=ACCENT_HOVER))
        next_btn.bind("<Leave>", lambda e: next_btn.config(bg=ACCENT))
        user_entry.bind("<Return>", lambda e: proceed())

    def open_new_password_dialog(username):
        dialog = tk.Toplevel(root)
        dialog.title("Set New Password")
        dialog.configure(bg=CARD_BG)
        center_dialog(dialog, 340, 380)
        dialog.transient(root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="Set New Password", font=(FONT, 16, "bold"),
                 bg=CARD_BG, fg=TEXT_PRIMARY).pack(pady=(25, 4))
        tk.Label(dialog, text=f"for {username}", font=(FONT, 10),
                 bg=CARD_BG, fg=TEXT_MUTED).pack(pady=(0, 15))

        tk.Label(dialog, text="New Password", font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
            .pack(fill="x", padx=35)
        pw_entry = tk.Entry(dialog, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                             insertbackground=ACCENT, relief="flat", show="\u2022")
        pw_entry.pack(fill="x", padx=35, pady=(3, 10), ipady=8)

        tk.Label(dialog, text="Confirm Password", font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
            .pack(fill="x", padx=35)
        confirm_pw_entry = tk.Entry(dialog, font=(FONT, 12), bg=FIELD_BG, fg=TEXT_PRIMARY,
                                     insertbackground=ACCENT, relief="flat", show="\u2022")
        confirm_pw_entry.pack(fill="x", padx=35, pady=(3, 10), ipady=8)

        dlg_error = tk.Label(dialog, text="", font=(FONT, 9), bg=CARD_BG, fg=ERROR_COLOR)
        dlg_error.pack()

        def save_new_password():
            pw = pw_entry.get().strip()
            confirm = confirm_pw_entry.get().strip()
            if not pw or not confirm:
                dlg_error.config(text="Please fill in both fields")
                return
            if pw != confirm:
                dlg_error.config(text="Passwords do not match")
                return

            database.reset_password(username, pw)
            dialog.destroy()
            messagebox.showinfo("Password Reset", "Your password has been updated. Please log in.")

        save_btn = tk.Button(dialog, text="Update Password", font=(FONT, 12, "bold"),
                              bg=ACCENT, fg=ACCENT_DARK_TEXT, bd=0, cursor="hand2", command=save_new_password)
        save_btn.pack(fill="x", padx=35, pady=(12, 20), ipady=8)
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=ACCENT_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=ACCENT))
        confirm_pw_entry.bind("<Return>", lambda e: save_new_password())

    forgot_label.bind("<Button-1>", lambda e: open_forgot_password_dialog())

    resize_to_fit()
    root.mainloop()


if __name__ == "__main__":
    show_login_window()