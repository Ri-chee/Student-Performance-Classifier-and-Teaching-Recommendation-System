import tkinter as tk
from tkinter import ttk

def get_pass_fail(student):
    avg = (float(student["quizzes"]) + float(student["exam"]) + float(student["activities"])) / 3
    return "PASS" if avg >= 75 else "FAIL"

class ClusterWindow:
    def __init__(self, root, student_list):
        self.win = tk.Toplevel(root)
        self.win.title("Clustered Student Results")
        self.win.geometry("1350x730")
        self.win.configure(bg="white")
        self.student_list = student_list
        self.build_ui()

    # ── TEACHING RECOMMENDATIONS DATA ────────────────────────────────────────
    RECOMMENDATIONS = {
        "A": {
            "title":    "High Performing Students",
            "icon":     "⭐",
            "bg":       "#EAF3DE",
            "fg":       "#3B6D11",
            "border":   "#8fcc55",
            "strategies": [
                "Provide enrichment tasks and advanced problem-solving activities",
                "Encourage independent and self-directed learning projects",
                "Use creative, engaging, and challenging materials",
                "Promote peer tutoring — let them help other students",
            ],
            "tools": ["Canva", "Google Slides", "Khan Academy (advanced)"],
        },
        "B": {
            "title":    "Average but Improving Students",
            "icon":     "📈",
            "bg":       "#E1F5EE",
            "fg":       "#0F6E56",
            "border":   "#55ccaa",
            "strategies": [
                "Use guided practice and collaborative learning activities",
                "Reinforce lessons through group discussions and exercises",
                "Provide regular, constructive feedback on progress",
                "Set incremental goals to build confidence and momentum",
            ],
            "tools": ["Google Classroom", "Quizlet", "Kahoot"],
        },
        "C": {
            "title":    "Struggling / At-Risk Students",
            "icon":     "🆘",
            "bg":       "#FCEBEB",
            "fg":       "#A32D2D",
            "border":   "#f08080",
            "strategies": [
                "Use differentiated instruction and scaffolding techniques",
                "Provide one-on-one or small group focused teaching sessions",
                "Focus on foundational and prerequisite skills first",
                "Break down complex tasks into smaller, manageable steps",
            ],
            "tools": ["Khan Academy", "Quizlet", "IXL Learning"],
        },
        "D": {
            "title":    "Inconsistent Performers",
            "icon":     "🔄",
            "bg":       "#FAEEDA",
            "fg":       "#854F0B",
            "border":   "#f0c060",
            "strategies": [
                "Identify patterns in performance — attendance, topic areas, etc.",
                "Provide structure and consistent routines to build stability",
                "Use motivational strategies and goal-setting frameworks",
                "Offer flexible assessments to capture varying performance",
            ],
            "tools": ["Google Classroom", "Quizlet", "Canva"],
        },
    }

    GENERAL_TIPS = [
        "Adjust teaching strategies based on each student's individual needs",
        "Use interactive and visual materials to increase engagement",
        "Monitor student progress continuously with formative assessments",
        "Provide timely, specific feedback and consistent encouragement",
    ]

    def build_ui(self):
        # header
        header = tk.Frame(self.win, bg="#E8A820", pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Clustered Student Results",
                 font=("Helvetica", 18, "bold"),
                 bg="#E8A820", fg="#1a1a1a").pack()
        tk.Label(header, text="K-Means Clustering — Teaching Recommendation System",
                 font=("Helvetica", 10),
                 bg="#E8A820", fg="#3a3a3a").pack()

        # scrollable body
        canvas_frame = tk.Frame(self.win, bg="white")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        sb = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg="white")
        cw = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(cw, width=e.width))

        # mouse scroll
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        self.render_groups()
        self.render_general_tips()

        # footer
        footer = tk.Frame(self.win, bg="#1a1a1a", pady=8)
        footer.pack(fill="x")
        tk.Label(footer, text=f"Total students: {len(self.student_list)}",
                 font=("Helvetica", 10, "bold"),
                 bg="#1a1a1a", fg="#E8A820").pack(side="left", padx=14)
        tk.Button(footer, text="Close", command=self.win.destroy,
                  bg="#E8A820", fg="#1a1a1a", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=14, pady=4).pack(side="right", padx=14)

    def render_groups(self):
        group_info = {
            "A": {"name": "High Performers",         "bg": "#EAF3DE", "fg": "#3B6D11", "header": "#c5e8a0"},
            "B": {"name": "Average but Improving",   "bg": "#E1F5EE", "fg": "#0F6E56", "header": "#a0dfc7"},
            "C": {"name": "Struggling Students",     "bg": "#FCEBEB", "fg": "#A32D2D", "header": "#f5b8b8"},
            "D": {"name": "Inconsistent Performers", "bg": "#FAEEDA", "fg": "#854F0B", "header": "#f5d9a0"},
        }

        col_labels = ["#", "First Name", "Last Name", "Number of Absences", "Quizzes", "Exam", "Activities", "Status"]
        col_widths  = [40,  140,          140,          140,                  90,        90,     90,            80]

        groups = {"A": [], "B": [], "C": [], "D": []}
        for s in self.student_list:
            g = s.get("group", "—")
            if g in groups:
                groups[g].append(s)

        for letter, students in groups.items():
            info = group_info[letter]
            count = len(students)

            # group header bar
            grp_hdr = tk.Frame(self.body, bg=info["header"], pady=8)
            grp_hdr.pack(fill="x", pady=(12, 0))
            tk.Label(grp_hdr,
                     text=f"  Group {letter}  —  {info['name']}  |  {count} student{'s' if count != 1 else ''}",
                     font=("Helvetica", 12, "bold"),
                     bg=info["header"], fg=info["fg"]).pack(side="left", padx=12)

            if not students:
                tk.Label(self.body,
                         text="  No students in this group.",
                         font=("Helvetica", 9, "italic"),
                         bg="white", fg="#aaa", pady=4).pack(fill="x")
            else:
                # column sub-header
                sub_hdr = tk.Frame(self.body, bg=info["bg"])
                sub_hdr.pack(fill="x")
                for lbl, w in zip(col_labels, col_widths):
                    tk.Label(sub_hdr, text=lbl,
                             font=("Helvetica", 9, "bold"),
                             bg=info["bg"], fg=info["fg"],
                             width=w//8, pady=5).pack(side="left", padx=1)

                # student rows
                for i, s in enumerate(students, start=1):
                    row_bg = info["bg"] if i % 2 == 0 else "white"
                    row = tk.Frame(self.body, bg=row_bg, pady=3)
                    row.pack(fill="x")

                    status = get_pass_fail(s)
                    status_fg = "#2e7d32" if status == "PASS" else "#c62828"

                    values = [
                        str(i),
                        s["first_name"],
                        s["last_name"],
                        str(s["absences"]),
                        str(s["quizzes"]),
                        str(s["exam"]),
                        str(s["activities"]),
                    ]
                    for val, w in zip(values, col_widths[:-1]):
                        tk.Label(row, text=val,
                                 font=("Helvetica", 10),
                                 bg=row_bg, fg="#1a1a1a",
                                 width=w//8, anchor="center").pack(side="left", padx=2)

                    # Pass/Fail badge — bold green or red
                    tk.Label(row, text=status,
                             font=("Helvetica", 10, "bold"),
                             bg=row_bg, fg=status_fg,
                             width=col_widths[-1]//8,
                             anchor="center").pack(side="left", padx=2)

            # Teaching Recommendation toggle button + hidden card
            self.render_recommendation_toggle(letter, info)

    def render_recommendation_toggle(self, letter, group_info):
        rec = self.RECOMMENDATIONS[letter]

        # Button row beneath each group
        btn_row = tk.Frame(self.body, bg="white", pady=6)
        btn_row.pack(fill="x", padx=16)

        def open_popup(letter=letter, rec=rec):
            popup = tk.Toplevel(self.win)
            popup.title(f"Group {letter} — Teaching Recommendations")
            
            # centered window
            popup.configure(bg=rec["bg"])
            popup.resizable(False, False)
            popup.grab_set()
            popup.update_idletasks()
            w, h = 620, 460
            parent_x = self.win.winfo_rootx()
            parent_y = self.win.winfo_rooty()
            parent_w = self.win.winfo_width()
            parent_h = self.win.winfo_height()
            x = parent_x + (parent_w // 2) - (w // 2)
            y = parent_y + (parent_h // 2) - (h // 2)
            popup.geometry(f"{w}x{h}+{x}+{y}")
# ── Popup header ──

            # ── Popup header ──────────────────────────────────────────────────
            hdr = tk.Frame(popup, bg=rec["border"], pady=14)
            hdr.pack(fill="x")
            tk.Label(hdr,
                     text=f"{rec['icon']}  Group {letter} — {rec['title']}",
                     font=("Helvetica", 14, "bold"),
                     bg=rec["border"], fg=rec["fg"]).pack()
            tk.Label(hdr,
                     text="Teaching Recommendations",
                     font=("Helvetica", 10),
                     bg=rec["border"], fg=rec["fg"]).pack()

            # ── Body ──────────────────────────────────────────────────────────
            body = tk.Frame(popup, bg=rec["bg"], padx=24, pady=16)
            body.pack(fill="both", expand=True)

            # Strategies section
            tk.Label(body, text="📋  Strategies",
                     font=("Helvetica", 11, "bold"),
                     bg=rec["bg"], fg=rec["fg"]).pack(anchor="w", pady=(0, 6))

            for strategy in rec["strategies"]:
                row = tk.Frame(body, bg=rec["bg"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text="•", font=("Helvetica", 10),
                         bg=rec["bg"], fg=rec["fg"]).pack(side="left", padx=(4, 8))
                tk.Label(row, text=strategy,
                         font=("Helvetica", 10),
                         bg=rec["bg"], fg="#1a1a1a",
                         anchor="w", justify="left",
                         wraplength=520).pack(side="left", fill="x")

            # Divider
            tk.Frame(body, bg=rec["border"], height=2).pack(fill="x", pady=12)

            # Recommended tools section
            tk.Label(body, text="🛠  Recommended Tools",
                     font=("Helvetica", 11, "bold"),
                     bg=rec["bg"], fg=rec["fg"]).pack(anchor="w", pady=(0, 6))

            tools_row = tk.Frame(body, bg=rec["bg"])
            tools_row.pack(anchor="w")
            for tool in rec["tools"]:
                tk.Label(tools_row,
                         text=f"  {tool}  ",
                         font=("Helvetica", 10, "bold"),
                         bg=rec["border"], fg=rec["fg"],
                         padx=8, pady=4,
                         relief="flat").pack(side="left", padx=4)

            # ── Close button ──────────────────────────────────────────────────
            footer = tk.Frame(popup, bg=rec["bg"], pady=10)
            footer.pack(fill="x")
            tk.Button(footer, text="Close",
                      font=("Helvetica", 10, "bold"),
                      bg=rec["border"], fg=rec["fg"],
                      relief="flat", padx=20, pady=5,
                      cursor="hand2",
                      command=popup.destroy).pack()

        tk.Button(btn_row,
                  text=f"📋  View Recommendations for Group {letter}",
                  font=("Helvetica", 10, "bold"),
                  bg=rec["bg"], fg=rec["fg"],
                  relief="flat", padx=12, pady=5,
                  cursor="hand2", command=open_popup).pack(side="left")

    def render_general_tips(self):
        tk.Frame(self.body, bg="#cccccc", height=2).pack(fill="x", padx=10, pady=(14, 0))

        tip_hdr = tk.Frame(self.body, bg="#1a1a1a", pady=8)
        tip_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(tip_hdr,
                 text="  💡  General Teaching Tips — Applies to All Groups",
                 font=("Helvetica", 12, "bold"),
                 bg="#1a1a1a", fg="#E8A820").pack(side="left", padx=12)

        tips_card = tk.Frame(self.body, bg="#F5F5F5", padx=16, pady=12)
        tips_card.pack(fill="x", padx=16, pady=(0, 16))

        for tip in self.GENERAL_TIPS:
            row = tk.Frame(tips_card, bg="#F5F5F5")
            row.pack(fill="x", pady=2)
            tk.Label(row, text="✔", font=("Helvetica", 10, "bold"),
                     bg="#F5F5F5", fg="#E8A820").pack(side="left", padx=(4, 8))
            tk.Label(row, text=tip,
                     font=("Helvetica", 10),
                     bg="#F5F5F5", fg="#1a1a1a",
                     anchor="w").pack(side="left")