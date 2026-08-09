import database
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar
from datetime import date

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas

# ---------------------------------------------------------------------------
# Theme — bold modern dark palette (teal/emerald accent instead of the old
# navy/purple, on a near-black background) so the change is unmistakable.
# ---------------------------------------------------------------------------
APP_BG = "#080B10"
PANEL_BG = "#0F1720"
CARD_BG = "#152029"
BORDER_COLOR = "#22EFC0"

ACCENT = "#22EFC0"          # bright teal/emerald — new primary accent
ACCENT_HOVER = "#5FFFDA"
ACCENT_SOFT = "#1B3A38"

DANGER = "#FF3B5C"
DANGER_HOVER = "#FF6B85"

GOLD = "#FFC531"
GOLD_HOVER = "#FFD966"

MONTH_ACTIVE = "#FF8A3D"    # orange, distinct from teal weekly bars
MONTH_INACTIVE = "#3A2A1E"

TEXT_PRIMARY = "#EAFBF7"
TEXT_MUTED = "#6F8B87"
GRID_LINE = "#1C2B2A"

FONT = "Segoe UI"

BG_COLOR = PANEL_BG
TEXT_COLOR = TEXT_PRIMARY
ACCENT_COLOR = ACCENT
CERTIFICATE_THRESHOLD = 90


def add_hover(widget, normal_color, hover_color):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))


def center_toplevel(win, width, height):
    """Centers a Toplevel dialog on the screen instead of leaving it at
    whatever default position Tk picks (which could clip off-screen)."""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def style_axes(ax, title, ylabel):
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, color=TEXT_PRIMARY, fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, color=TEXT_MUTED, fontsize=9)
    ax.tick_params(colors=TEXT_MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID_LINE, linestyle="-", linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    for spine_name in ["top", "right", "left", "bottom"]:
        ax.spines[spine_name].set_color("#223230")


def launch_task_planner(username):
    checkbox_vars = {}
    pending_changes = {}

    # The account this session belongs to. It's a plain variable (not a
    # dict) so the Profile dialog can update it in place with `nonlocal`
    # if the person changes their username there.
    current_username = username

    today = date.today()
    current_month = today.month
    current_year = today.year

    root = tk.Tk()
    database.create_database()
    root.title("Task Planner")
    root.configure(bg=APP_BG)
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width}x{height}")

    top_frame = tk.Frame(root, height=int(height * 0.38), bg=PANEL_BG)
    top_frame.pack(side="top", fill="x")
    top_frame.pack_propagate(False)

    canvas = tk.Canvas(root, bg=APP_BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(
        root, orient="vertical", command=canvas.yview,
        bg=CARD_BG, troughcolor=APP_BG, activebackground=ACCENT,
        highlightbackground=APP_BG, bd=0
    )
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tk.Frame(canvas, bg=APP_BG)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=width)

    weekly_graph_frame = tk.Frame(top_frame, bg=CARD_BG, highlightbackground="#22322f", highlightthickness=1)
    weekly_graph_frame.place(relx=0, rely=0.1, relwidth=0.35, relheight=0.65)

    monthly_graph_frame = tk.Frame(top_frame, bg=CARD_BG, highlightbackground="#22322f", highlightthickness=1)
    monthly_graph_frame.place(relx=0.355, rely=0.1, relwidth=0.4, relheight=0.65)

    def get_current_week_range():
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        if current_year == today.year and current_month == today.month:
            current_day = today.day
        else:
            current_day = 1
        week_index = (current_day - 1) // 7
        week_start = week_index * 7 + 1
        week_end = min(week_start + 6, days_in_month)
        return week_start, week_end, week_index + 1

    def show_bar_graph():
        week_data = database.get_week_comparison(current_month, current_year)
        _, _, current_week_num = get_current_week_range()

        week_labels_list = [f"Week {w}" for w, pct, s, e in week_data]
        weekly_progress = [pct for w, pct, s, e in week_data]
        week_colors = [ACCENT if w == current_week_num else ACCENT_SOFT for w, pct, s, e in week_data]

        month_data = database.get_month_comparison(current_year)
        month_labels_list = [calendar.month_abbr[m] for m, pct in month_data]
        monthly_progress = [pct for m, pct in month_data]
        month_colors = [MONTH_ACTIVE if m == current_month else MONTH_INACTIVE for m, pct in month_data]

        for widget in weekly_graph_frame.winfo_children():
            widget.destroy()
        for widget in monthly_graph_frame.winfo_children():
            widget.destroy()

        fig1 = Figure(figsize=(4, 3), dpi=80)
        fig1.patch.set_facecolor(CARD_BG)
        ax1 = fig1.add_subplot(111)
        ax1.bar(week_labels_list, weekly_progress, color=week_colors, width=0.6)
        ax1.set_ylim(0, 100)
        style_axes(ax1, f"Weekly Comparison - {calendar.month_name[current_month]} {current_year}", "Completion %")
        fig1.tight_layout()

        chart1 = FigureCanvasTkAgg(fig1, master=weekly_graph_frame)
        chart1.draw()
        chart1.get_tk_widget().configure(bg=CARD_BG)
        chart1.get_tk_widget().pack(fill="both", expand=True)

        fig2 = Figure(figsize=(5, 3), dpi=80)
        fig2.patch.set_facecolor(CARD_BG)
        ax2 = fig2.add_subplot(111)
        ax2.bar(month_labels_list, monthly_progress, color=month_colors, width=0.6)
        ax2.set_ylim(0, 100)
        style_axes(ax2, f"Monthly Comparison - {current_year}", "Completion %")
        fig2.tight_layout()

        chart2 = FigureCanvasTkAgg(fig2, master=monthly_graph_frame)
        chart2.draw()
        chart2.get_tk_widget().configure(bg=CARD_BG)
        chart2.get_tk_widget().pack(fill="both", expand=True)

    def save_progress():
        nonlocal pending_changes
        for (task_id, day), status in pending_changes.items():
            database.update_progress(task_id, day, status)
        pending_changes = {}
        show_bar_graph()

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", on_frame_configure)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    task_y = 0
    ROW_HEIGHT = 55
    START_X = 0.210
    DATE_WIDTH = 0.024
    BOX_SIZE = 0.014
    TOTAL_CALENDAR_WIDTH = DATE_WIDTH * 31

    month_labels = []
    week_labels = []
    date_labels = []

    def clear_month_widgets():
        nonlocal month_labels, week_labels, date_labels
        for lbl in month_labels:
            lbl.destroy()
        for lbl in week_labels:
            lbl.destroy()
        for lbl in date_labels:
            lbl.destroy()
        month_labels = []
        week_labels = []
        date_labels = []

    def clear_task_widgets():
        nonlocal task_y
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        task_y = 0
        checkbox_vars.clear()

    def select_month(month):
        nonlocal current_month, pending_changes
        pending_changes = {}
        current_month = month

        clear_task_widgets()
        draw_calendar_strip()
        load_tasks()
        show_bar_graph()

    def draw_calendar_strip():
        clear_month_widgets()

        days_in_month = calendar.monthrange(current_year, current_month)[1]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        month_width = TOTAL_CALENDAR_WIDTH / 12
        x = START_X
        for i, month in enumerate(months):
            is_current = (i + 1) == current_month
            bg = ACCENT if is_current else CARD_BG
            fg = "#08120F" if is_current else TEXT_PRIMARY
            btn = tk.Button(
                top_frame, text=month, font=(FONT, 13, "bold" if is_current else "normal"),
                bg=bg, fg=fg, bd=0, cursor="hand2",
                activebackground=ACCENT_HOVER, activeforeground="#08120F",
                command=lambda m=i + 1: select_month(m)
            )
            btn.place(relx=x, rely=0.75, relwidth=month_width - 0.003, relheight=0.08)
            add_hover(btn, bg, ACCENT_HOVER)
            month_labels.append(btn)
            x += month_width

        num_weeks = -(-days_in_month // 7)
        week_width = TOTAL_CALENDAR_WIDTH / num_weeks
        x = START_X
        for w in range(1, num_weeks + 1):
            label = tk.Label(top_frame, text=f"Week {w}", font=(FONT, 12), bg=PANEL_BG, fg=TEXT_MUTED)
            label.place(relx=x, rely=0.84, relwidth=week_width - 0.005, relheight=0.08)
            week_labels.append(label)
            x += week_width

        start_x = START_X
        day_width = TOTAL_CALENDAR_WIDTH / 31
        for day in range(1, days_in_month + 1):
            is_today = (current_year == today.year and current_month == today.month and day == today.day)
            bg = ACCENT if is_today else CARD_BG
            fg = "#08120F" if is_today else TEXT_MUTED
            label = tk.Label(top_frame, text=str(day), font=(FONT, 9), bg=bg, fg=fg)
            label.place(relx=start_x, rely=0.92, relwidth=day_width, relheight=0.08)
            date_labels.append(label)
            start_x += day_width

    # ------------------------------------------------------------------
    # Add Task dialog
    # ------------------------------------------------------------------
    # FIX: this used to be tkinter's built-in simpledialog.askstring(),
    # which renders as a plain white system popup that clashes with the
    # rest of the app. It's now a themed Toplevel matching every other
    # dialog in the app (same card style, accent button, hover states).

    def add_task():
        dialog = tk.Toplevel(root)
        dialog.title("Add Task")
        dialog.configure(bg=BORDER_COLOR)
        dialog.resizable(False, False)
        center_toplevel(dialog, 380, 250)
        dialog.transient(root)
        dialog.grab_set()

        inner = tk.Frame(dialog, bg=CARD_BG)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(inner, text="\u2795 Add New Task", font=(FONT, 15, "bold"),
                 bg=CARD_BG, fg=TEXT_PRIMARY).pack(pady=(22, 4))
        tk.Label(inner, text=f"for {calendar.month_name[current_month]} {current_year}", font=(FONT, 10),
                 bg=CARD_BG, fg=TEXT_MUTED).pack(pady=(0, 14))

        tk.Label(inner, text="Task Name", font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
            .pack(fill="x", padx=30)

        entry_wrapper = tk.Frame(inner, bg="#22322f")
        entry_wrapper.pack(fill="x", padx=30, pady=(4, 6))
        name_entry = tk.Entry(entry_wrapper, font=(FONT, 12), bg="#0B1116", fg=TEXT_PRIMARY,
                               insertbackground=ACCENT, relief="flat", bd=0)
        name_entry.pack(fill="x", padx=1, pady=1, ipady=9)
        name_entry.bind("<FocusIn>", lambda e: entry_wrapper.config(bg=ACCENT))
        name_entry.bind("<FocusOut>", lambda e: entry_wrapper.config(bg="#22322f"))
        name_entry.focus_set()

        dlg_error = tk.Label(inner, text="", font=(FONT, 9), bg=CARD_BG, fg=DANGER)
        dlg_error.pack(pady=(0, 2))

        def confirm():
            task_name = name_entry.get().strip()
            if not task_name:
                dlg_error.config(text="Please enter a task name")
                return
            dialog.destroy()
            task_id = database.add_task(task_name, current_month, current_year)
            render_task_row(task_id, task_name)
            show_bar_graph()

        btn_row = tk.Frame(inner, bg=CARD_BG)
        btn_row.pack(fill="x", padx=30, pady=(10, 20))

        cancel_btn = tk.Button(btn_row, text="Cancel", font=(FONT, 11), bg="#2a2a3a", fg=TEXT_PRIMARY,
                                bd=0, cursor="hand2", activebackground="#3a3a4d", activeforeground=TEXT_PRIMARY,
                                command=dialog.destroy)
        cancel_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 6))
        add_hover(cancel_btn, "#2a2a3a", "#3a3a4d")

        confirm_btn = tk.Button(btn_row, text="Add Task", font=(FONT, 11, "bold"), bg=ACCENT, fg="#08120F",
                                 bd=0, cursor="hand2", activebackground=ACCENT_HOVER, activeforeground="#08120F",
                                 command=confirm)
        confirm_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(6, 0))
        add_hover(confirm_btn, ACCENT, ACCENT_HOVER)

        name_entry.bind("<Return>", lambda e: confirm())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def render_task_row(task_id, task_name):
        nonlocal task_y

        label = tk.Label(scroll_frame, text=task_name, font=(FONT, 13), bg=PANEL_BG, fg=TEXT_PRIMARY, anchor="w", padx=15)
        label.place(relx=0, y=task_y, relwidth=0.2, height=50)

        row_vars = []
        x = START_X
        progress = database.get_progress(task_id)

        for day in range(1, 32):
            var = tk.IntVar()
            for d, status in progress:
                if d == day:
                    var.set(status)

            checkbox = tk.Checkbutton(
                scroll_frame, variable=var, indicatoron=False, onvalue=1, offvalue=0,
                bg=CARD_BG, fg="#08120F", selectcolor=ACCENT, activebackground=ACCENT_HOVER,
                relief="flat", bd=0, highlightbackground="#22322f", highlightthickness=1,
                padx=0, pady=0, font=(FONT, 10, "bold")
            )
            checkbox.config(text="\u2713" if var.get() else "")

            def on_toggle(*args, cb=checkbox, v=var, d=day, t_id=task_id):
                cb.config(text="\u2713" if v.get() else "")
                pending_changes[(t_id, d)] = v.get()

            var.trace_add("write", on_toggle)

            box_x = x + (DATE_WIDTH - BOX_SIZE) / 2
            checkbox.place(relx=box_x, y=task_y + 8, relwidth=BOX_SIZE, height=30)
            row_vars.append(var)
            x += DATE_WIDTH

        checkbox_vars[task_id] = row_vars
        task_y += ROW_HEIGHT
        scroll_frame.config(height=task_y)

    def load_tasks():
        tasks = database.get_tasks(current_month, current_year)
        for task_id, task_name in tasks:
            render_task_row(task_id, task_name)

    # ------------------------------------------------------------------
    # Certificate feature
    # ------------------------------------------------------------------
    # FIX: this dialog now ALWAYS opens first, no matter how many months
    # qualify (1, several, or 0). It never skips straight to the name
    # prompt. If nothing qualifies, the list area shows a clear message
    # instead of any month buttons, and there's no way to proceed past it.

    def open_certificate_dialog():
        eligible = database.get_eligible_months(CERTIFICATE_THRESHOLD)

        dialog = tk.Toplevel(root)
        dialog.title("Download Certificate")
        dialog.configure(bg=CARD_BG)
        center_toplevel(dialog, 380, 420)
        dialog.transient(root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(
            dialog, text="Eligible Months", font=(FONT, 15, "bold"),
            bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(pady=(20, 4))

        tk.Label(
            dialog, text=f"Months with \u2265 {CERTIFICATE_THRESHOLD}% completion",
            font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED
        ).pack(pady=(0, 15))

        list_area = tk.Frame(dialog, bg=CARD_BG)
        list_area.pack(fill="both", expand=True, padx=20)

        if not eligible:
            tk.Label(
                list_area,
                text=f"No month has reached {CERTIFICATE_THRESHOLD}% completion yet.\n\nKeep completing your daily tasks —\nonce a month hits {CERTIFICATE_THRESHOLD}%, it will show up here.",
                font=(FONT, 11), bg=CARD_BG, fg=TEXT_MUTED, justify="center", wraplength=320
            ).pack(pady=30)

            close_btn = tk.Button(
                dialog, text="Close", font=(FONT, 11, "bold"), bg="#2a2a3a", fg=TEXT_PRIMARY,
                bd=0, cursor="hand2", command=dialog.destroy
            )
            close_btn.pack(pady=20, padx=20, fill="x", ipady=8)
            add_hover(close_btn, "#2a2a3a", "#3a3a4d")
            return

        def choose(m, y, p):
            dialog.destroy()
            save_certificate(m, y, p)

        canvas_list = tk.Canvas(list_area, bg=CARD_BG, highlightthickness=0)
        canvas_list.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas_list, bg=CARD_BG)
        canvas_list.create_window((0, 0), window=inner, anchor="nw", width=320)
        inner.bind("<Configure>", lambda e: canvas_list.configure(scrollregion=canvas_list.bbox("all")))

        for m, y, p in eligible:
            row = tk.Button(
                inner,
                text=f"{calendar.month_name[m]} {y}          {p:.1f}%",
                font=(FONT, 12), bg=ACCENT, fg="#08120F", bd=0, cursor="hand2",
                anchor="w", padx=15,
                activebackground=ACCENT_HOVER, activeforeground="#08120F",
                command=lambda m=m, y=y, p=p: choose(m, y, p)
            )
            row.pack(fill="x", pady=5, ipady=10)
            add_hover(row, ACCENT, ACCENT_HOVER)

        dialog.wait_window()

    def save_certificate(month, year, percentage):
        # No name prompt here anymore — the name comes from the account's
        # saved profile (set at signup, editable via the Profile dialog).
        profile = database.get_user_profile(current_username)
        name = profile[0] if profile and profile[0] else current_username

        default_filename = f"Certificate_{calendar.month_name[month]}_{year}.pdf"
        save_path = filedialog.asksaveasfilename(
            title="Save Certificate As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_filename
        )
        if not save_path:
            return

        try:
            generate_certificate_pdf(save_path, name, month, year, percentage)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create certificate:\n{e}")
            return

        messagebox.showinfo("Certificate Saved", f"Certificate saved to:\n{save_path}")

    def generate_certificate_pdf(path, name, month, year, percentage):
        page_size = landscape(letter)
        c = pdf_canvas.Canvas(path, pagesize=page_size)
        page_width, page_height = page_size

        navy = HexColor("#000080")
        accent = HexColor(ACCENT_COLOR)
        gray = HexColor("#333333")

        c.setStrokeColor(accent)
        c.setLineWidth(6)
        c.rect(0.4 * inch, 0.4 * inch, page_width - 0.8 * inch, page_height - 0.8 * inch)

        c.setStrokeColor(navy)
        c.setLineWidth(1.2)
        c.rect(0.55 * inch, 0.55 * inch, page_width - 1.1 * inch, page_height - 1.1 * inch)

        c.setFont("Helvetica-Bold", 34)
        c.setFillColor(navy)
        c.drawCentredString(page_width / 2, page_height - 1.7 * inch, "CERTIFICATE OF ACHIEVEMENT")

        c.setFont("Helvetica", 15)
        c.setFillColor(gray)
        c.drawCentredString(page_width / 2, page_height - 2.25 * inch, "This certificate is proudly presented to")

        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(accent)
        c.drawCentredString(page_width / 2, page_height - 3.05 * inch, name)

        name_width = c.stringWidth(name, "Helvetica-Bold", 30)
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.line(
            page_width / 2 - name_width / 2 - 0.3 * inch, page_height - 3.2 * inch,
            page_width / 2 + name_width / 2 + 0.3 * inch, page_height - 3.2 * inch
        )

        c.setFont("Helvetica", 15)
        c.setFillColor(gray)
        body_text = f"for achieving {percentage:.1f}% task completion in {calendar.month_name[month]} {year}"
        c.drawCentredString(page_width / 2, page_height - 3.75 * inch, body_text)

        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width / 2, page_height - 4.3 * inch, "Issued by Task Planner")

        issue_date = date.today().strftime("%B %d, %Y")
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(gray)
        c.drawString(1 * inch, 1 * inch, f"Date: {issue_date}")
        c.drawRightString(page_width - 1 * inch, 1 * inch, "Task Planner")

        c.save()

    # ------------------------------------------------------------------
    # Account menu (top-right icon -> dropdown)
    #
    # This replaces a standalone "Logout" button so the action-button
    # column (Save Progress / Add Task / Download Certificate) has room
    # to grow with future features without getting crowded. Anything
    # account-related — Logout now, and things like "Change Password" or
    # "Settings" later — goes inside this dropdown instead of taking a
    # new full-width button slot.
    #
    # To add a new item later: copy the "Logout" add_menu_item(...) call
    # below and give it a new label + command. That's the only change
    # needed; the button and dropdown positioning stay the same.
    # ------------------------------------------------------------------

    def logout():
        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return
        root.destroy()
        import auth  # local import: avoids a circular import with auth.py
        auth.show_login_window()

    def open_profile_dialog():
        nonlocal current_username

        profile = database.get_user_profile(current_username)
        existing_full_name = profile[0] if profile and profile[0] else ""
        existing_username = profile[1] if profile else current_username

        dialog = tk.Toplevel(root)
        dialog.title("Profile")
        dialog.configure(bg=CARD_BG)
        # FIX: this was 380x500, which was just short of fitting the Save
        # Changes / Cancel buttons below the four fields — they existed,
        # they just rendered off the bottom edge of the dialog. Taller
        # dialog + centering on screen fixes both the clipping and the
        # dialog spawning partially off-screen on smaller monitors.
        center_toplevel(dialog, 380, 580)
        dialog.transient(root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="\U0001F464 Your Profile", font=(FONT, 16, "bold"),
                 bg=CARD_BG, fg=TEXT_PRIMARY).pack(pady=(22, 4))
        tk.Label(dialog, text="View and edit your account details", font=(FONT, 10),
                 bg=CARD_BG, fg=TEXT_MUTED).pack(pady=(0, 16))

        def make_field(label_text, initial_value="", show=None):
            tk.Label(dialog, text=label_text, font=(FONT, 10), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
                .pack(fill="x", padx=30)
            entry = tk.Entry(dialog, font=(FONT, 12), bg="#0B1116", fg=TEXT_PRIMARY,
                              insertbackground=ACCENT, relief="flat", show=show or "")
            entry.insert(0, initial_value)
            entry.pack(fill="x", padx=30, pady=(3, 12), ipady=8)
            return entry

        name_entry = make_field("Full Name", existing_full_name)
        username_field = make_field("Username", existing_username)
        new_password_entry = make_field("New Password (leave blank to keep current)")
        new_password_entry.config(show="\u2022")
        current_password_entry = make_field("Current Password (only needed if changing username/password)")
        current_password_entry.config(show="\u2022")

        dlg_error = tk.Label(dialog, text="", font=(FONT, 9), bg=CARD_BG, fg=DANGER)
        dlg_error.pack(pady=(0, 4))

        def save_changes():
            nonlocal current_username

            new_full_name = name_entry.get().strip()
            new_username = username_field.get().strip()
            new_password = new_password_entry.get().strip()
            current_password = current_password_entry.get().strip()

            if not new_full_name or not new_username:
                dlg_error.config(text="Full name and username can't be empty")
                return

            # FIX: previously the current password was required for ANY
            # save, even just fixing a typo in the full name. Now it's
            # only required when actually changing something sensitive —
            # the username or the password itself.
            changing_username = new_username != current_username
            changing_password = bool(new_password)

            if changing_username or changing_password:
                if not current_password:
                    dlg_error.config(text="Enter your current password to change username/password")
                    return
                if not database.verify_login(current_username, current_password):
                    dlg_error.config(text="Current password is incorrect")
                    return

            if changing_username and database.username_taken_by_other(new_username, current_username):
                dlg_error.config(text="That username is already taken")
                return

            database.update_profile(
                current_username, new_full_name, new_username,
                new_password if new_password else None
            )
            current_username = new_username

            dialog.destroy()
            messagebox.showinfo("Profile Updated", "Your profile has been saved.")

        save_btn = tk.Button(dialog, text="Save Changes", font=(FONT, 12, "bold"), bg=ACCENT, fg="#08120F",
                              bd=0, cursor="hand2", activebackground=ACCENT_HOVER, activeforeground="#08120F",
                              command=save_changes)
        save_btn.pack(fill="x", padx=30, pady=(8, 8), ipady=9)
        add_hover(save_btn, ACCENT, ACCENT_HOVER)

        cancel_btn = tk.Button(dialog, text="Cancel", font=(FONT, 11), bg="#2a2a3a", fg=TEXT_PRIMARY,
                                bd=0, cursor="hand2", activebackground="#3a3a4d", activeforeground=TEXT_PRIMARY,
                                command=dialog.destroy)
        cancel_btn.pack(fill="x", padx=30, pady=(0, 20), ipady=8)
        add_hover(cancel_btn, "#2a2a3a", "#3a3a4d")

    menu_state = {"window": None}

    def close_account_menu(event=None):
        if menu_state["window"] is not None:
            menu_state["window"].destroy()
            menu_state["window"] = None

    def add_menu_item(parent, text, command):
        item = tk.Button(
            parent, text=text, font=(FONT, 11), bg=CARD_BG, fg=TEXT_PRIMARY,
            bd=0, cursor="hand2", anchor="w", padx=16,
            activebackground=ACCENT_SOFT, activeforeground=TEXT_PRIMARY,
            command=lambda: (close_account_menu(), command())
        )
        item.pack(fill="x", ipady=9)
        add_hover(item, CARD_BG, ACCENT_SOFT)
        return item

    def toggle_account_menu():
        if menu_state["window"] is not None:
            close_account_menu()
            return

        dropdown = tk.Toplevel(root)
        dropdown.overrideredirect(True)
        dropdown.attributes("-topmost", True)

        outer = tk.Frame(dropdown, bg=BORDER_COLOR)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = tk.Frame(outer, bg=CARD_BG)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="ACCOUNT", font=(FONT, 8, "bold"), bg=CARD_BG, fg=TEXT_MUTED, anchor="w") \
            .pack(fill="x", padx=16, pady=(10, 4))

        # Add future account-related items the same way as these:
        add_menu_item(inner, "\U0001F464  Profile", open_profile_dialog)
        add_menu_item(inner, "\U0001F6AA  Logout", logout)

        inner.update_idletasks()
        menu_width = 190
        menu_height = inner.winfo_reqheight() + 4
        btn_right = account_btn.winfo_rootx() + account_btn.winfo_width()
        y = account_btn.winfo_rooty() + account_btn.winfo_height() + 6
        dropdown.geometry(f"{menu_width}x{menu_height}+{btn_right - menu_width}+{y}")

        dropdown.bind("<FocusOut>", close_account_menu)
        dropdown.bind("<Escape>", close_account_menu)
        dropdown.focus_set()

        menu_state["window"] = dropdown

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    label = tk.Label(top_frame, text="\U0001F4CA Weekly Progress", font=(FONT, 14, "bold"), bg=PANEL_BG, fg=TEXT_PRIMARY)
    label.place(relx=0, rely=0, relwidth=0.35, relheight=0.1)

    label = tk.Label(top_frame, text="\U0001F4C8 Monthly Progress", font=(FONT, 14, "bold"), bg=PANEL_BG, fg=TEXT_PRIMARY)
    label.place(relx=0.355, rely=0, relwidth=0.40, relheight=0.1)

    account_btn = tk.Button(
        top_frame, text="\U0001F464 \u25BE", font=(FONT, 13, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY,
        bd=0, cursor="hand2", activebackground=ACCENT_SOFT, activeforeground=TEXT_PRIMARY,
        command=toggle_account_menu
    )
    account_btn.place(relx=0.965, rely=0.015, relwidth=0.03, relheight=0.07)
    add_hover(account_btn, CARD_BG, ACCENT_SOFT)

    btn = tk.Button(top_frame, text="Save Progress", font=(FONT, 12, "bold"), bg=DANGER, fg="white",
                     bd=0, cursor="hand2", activebackground=DANGER_HOVER, activeforeground="white",
                     command=save_progress)
    btn.place(relx=0.775, rely=0.02, relwidth=0.11, relheight=0.14)
    add_hover(btn, DANGER, DANGER_HOVER)

    btn = tk.Button(top_frame, text="\u2795 Add Task", font=(FONT, 12, "bold"), bg=ACCENT, fg="#08120F",
                     bd=0, cursor="hand2", activebackground=ACCENT_HOVER, activeforeground="#08120F",
                     command=add_task)
    btn.place(relx=0.775, rely=0.19, relwidth=0.11, relheight=0.14)
    add_hover(btn, ACCENT, ACCENT_HOVER)

    btn = tk.Button(top_frame, text="\U0001F3C6 Download Certificate", font=(FONT, 11, "bold"),
                     bg=GOLD, fg="#1a1206", bd=0, cursor="hand2",
                     activebackground=GOLD_HOVER, activeforeground="#1a1206",
                     command=open_certificate_dialog)
    btn.place(relx=0.775, rely=0.36, relwidth=0.11, relheight=0.14)
    add_hover(btn, GOLD, GOLD_HOVER)

    label = tk.Label(top_frame, text="\U0001F4C5 Day Tasks", font=(FONT, 14, "bold"), bg=PANEL_BG, fg=TEXT_PRIMARY)
    label.place(relx=0, rely=0.75, relwidth=0.2, relheight=0.16)

    draw_calendar_strip()
    load_tasks()
    show_bar_graph()

    root.mainloop()


if __name__ == "__main__":
    # Running main.py directly (skipping the login screen) has no logged-in
    # username to attach to, so certificates/profile fall back to this.
    # Normal usage goes through `python auth.py`, which passes the real
    # logged-in username.
    launch_task_planner("guest")