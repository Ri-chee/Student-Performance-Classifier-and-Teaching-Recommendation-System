import tkinter as tk
from tkinter import ttk, messagebox
from db_operations import save_students, get_all_students, update_student
import threading
import json
import os
from PIL import Image, ImageTk
import pandas as pd 
from tkinter import filedialog
import webbrowser

# ── THREE ML ALGORITHMS ───────────────────────────────────────────────────────
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np
# ─────────────────────────────────────────────────────────────────────────────

SUBJECT_OPTIONS = ["ITEC 106", "CMSC 204", "CSEL 302"]
SECTION_OPTIONS = ["BSCS 2A", "BSCS 2B"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset(relative_path):
    return os.path.join(BASE_DIR, relative_path)


# ── PASS / FAIL LOGIC (simple if-else, unchanged) ────────────────────────────
def compute_pass_fail(absences, quizzes, exam, activities):
    avg = (quizzes + exam + activities) / 3
    if absences >= 15:
        return "FAIL"
    elif avg >= 75:
        return "PASS"
    else:
        return "FAIL"

# ── FACTOR-SPECIFIC STRATEGIES & TOOLS ───────────────────────────────────────
# When the Decision Tree identifies a top factor for a group, these strategies
# and tools replace the generic group ones in the recommendation popup.
FACTOR_STRATEGIES = {
    "Absences": {
        "strategies": [
            "Implement an attendance monitoring and early-warning alert system",
            "Conduct weekly check-ins with students who miss two or more consecutive classes",
            "Provide catch-up materials and recorded lessons for absent students",
            "Engage parents or guardians early when absences begin to accumulate",
        ],
        "tools": ["Google Classroom (announcements)", "ClassDojo", "Remind"],
    },
    "Quizzes": {
        "strategies": [
            "Use frequent low-stakes quizzes to reinforce daily learning objectives",
            "Review quiz mistakes as a class to identify and address common misconceptions",
            "Introduce spaced-repetition practice so quiz topics are revisited regularly",
            "Offer optional retake quizzes with targeted feedback to build mastery",
        ],
        "tools": ["Kahoot", "Quizlet", "Google Forms"],
    },
    "Exam": {
        "strategies": [
            "Provide structured exam reviews covering high-weight topics and past patterns",
            "Teach and practice test-taking strategies (time management, elimination, etc.)",
            "Use mock exams under timed conditions to reduce test anxiety",
            "Break exam preparation into weekly study milestones with checkpoints",
        ],
        "tools": ["Khan Academy", "Quizlet", "Google Classroom (assignments)"],
    },
    "Activities": {
        "strategies": [
            "Increase hands-on, project-based activities to build practical engagement",
            "Use collaborative group tasks that require every member to contribute",
            "Provide clear rubrics and sample outputs so expectations are transparent",
            "Give timely, specific feedback on activity submissions to guide improvement",
        ],
        "tools": ["Canva", "Google Slides", "Padlet"],
    },
}

# ── RECOMMENDATIONS DATA ──────────────────────────────────────────────────────
RECOMMENDATIONS = {
    "A": {
        "title":    "High Performing Students",
        "icon":     "⭐",
        "bg":       "#111827",
        "fg":       "#4ade80",
        "border":   "#1A3A5C",
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
        "bg":       "#111827",
        "fg":       "#38bdf8",
        "border":   "#1A3A5C",
        "strategies": [
            "Use guided practice and collaborative learning activities",
            "Reinforce lessons through group discussions and exercises",
            "Provide regular, constructive feedback on progress",
            "Set incremental goals to build confidence and momentum",
        ],
        "tools": ["Google Classroom", "Quizlet", "Kahoot"],
    },
    "C": {
        "title":      "Struggling / At-Risk Students",
        "icon":       "🆘",
        "bg":       "#111827",
        "fg":       "#f87171",
        "border":   "#1A3A5C",
        "strategies": [
            "Use differentiated instruction and scaffolding techniques",
            "Provide one-on-one or small group focused teaching sessions",
            "Focus on foundational and prerequisite skills first",
            "Break down complex tasks into smaller, manageable steps",
        ],
        "tools": ["Khan Academy", "Quizlet", "IXL Learning"],
    },
    "D": {
        "title":      "Inconsistent Performers",
        "icon":       "🔄",
        "bg":       "#111827",
        "fg":       "#fbbf24",
        "border":   "#1A3A5C",
        "strategies": [
            "Identify patterns in performance — attendance, topic areas, etc.",
            "Provide structure and consistent routines to build stability",
            "Use motivational strategies and goal-setting frameworks",
            "Offer flexible assessments to capture varying performance",
        ],
        "tools": ["Google Classroom", "Quizlet", "Canva"],
    },
}


# ── RECOMMENDATION POPUP  (now shows DT-based recommendation tip) ─────────────
def open_recommendation_popup(parent, letter, dt_insight=None):
    rec   = RECOMMENDATIONS[letter]
    popup = tk.Toplevel(parent)
    popup.title(f"Group {letter} — Teaching Recommendations")
    popup.configure(bg=rec["bg"])
    popup.resizable(False, False)
    popup.grab_set()
    popup.update_idletasks()
    w, h     = 640, 520
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    x  = (sw // 2) - (w // 2)
    y  = (sh // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    hdr = tk.Frame(popup, bg=rec["border"], pady=14)
    hdr.pack(fill="x")
    tk.Label(hdr, text=f"{rec['icon']}  Group {letter} — {rec['title']}",
             font=("Poppins", 14, "bold"),
             bg=rec["border"], fg=rec["fg"]).pack()
    tk.Label(hdr, text="Teaching Recommendations",
             font=("Poppins", 10),
             bg=rec["border"], fg="#9ca3af").pack()

    body = tk.Frame(popup, bg=rec["bg"], padx=24, pady=16)
    body.pack(fill="both", expand=True)

    top_factor = None
    if dt_insight:
        for factor in FACTOR_STRATEGIES:
            if f"'{factor}'" in dt_insight:
                top_factor = factor
                break

    if top_factor and top_factor in FACTOR_STRATEGIES:
        active_strategies = FACTOR_STRATEGIES[top_factor]["strategies"]
        active_tools      = FACTOR_STRATEGIES[top_factor]["tools"]
    else:
        active_strategies = rec["strategies"]   # fallback to original
        active_tools      = rec["tools"]

    # ── Decision-Tree insight (shown at top when available) ───────────────────
    if dt_insight:
        insight_frame = tk.Frame(body, bg="#1E2433", padx=12, pady=10)
        insight_frame.pack(fill="x", pady=(0, 14))
        tk.Label(insight_frame,
                 text="🤖  AI-Powered Focus Area (Decision Tree)",
                 font=("Poppins", 10, "bold"),
                 bg="#1E2433", fg=rec["fg"]).pack(anchor="w")
        tk.Label(insight_frame,
                 text=dt_insight,
                 font=("Poppins", 10),
                 bg="#1E2433", fg="#ffffff",
                 anchor="w", justify="left", wraplength=560).pack(anchor="w", pady=(4, 0))

    tk.Label(body, text="Strategies", font=("Poppins", 11, "bold"),
             bg=rec["bg"], fg=rec["fg"]).pack(anchor="w", pady=(0, 6))
    
    for strategy in active_strategies:
        row = tk.Frame(body, bg=rec["bg"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text="•", font=("Poppins", 10),
                 bg=rec["bg"], fg="#ffffff").pack(side="left", padx=(4, 8))
        tk.Label(row, text=strategy, font=("Poppins", 10),
                 bg=rec["bg"], fg="#ffffff",
                 anchor="w", justify="left", wraplength=540).pack(side="left", fill="x")

    tk.Frame(body, bg=rec["border"], height=2).pack(fill="x", pady=12)
    tk.Label(body, text="Recommended Tools", font=("Poppins", 11, "bold"),
             bg=rec["bg"], fg=rec["fg"]).pack(anchor="w", pady=(0, 6))
    # ── ADD import at top of file if not already present ──────────────────
    # import webbrowser  ← add this to the imports at the very top

    TOOL_URLS = {
        "Canva":                          "https://www.canva.com",
        "Google Slides":                  "https://slides.google.com",
        "Khan Academy (advanced)":        "https://www.khanacademy.org",
        "Khan Academy":                   "https://www.khanacademy.org",
        "Google Classroom":               "https://classroom.google.com",
        "Google Classroom (assignments)": "https://classroom.google.com",
        "Google Classroom (announcements)":"https://classroom.google.com",
        "Quizlet":                        "https://www.quizlet.com",
        "Kahoot":                         "https://kahoot.com",
        "IXL Learning":                   "https://www.ixl.com",
        "ClassDojo":                      "https://www.classdojo.com",
        "Remind":                         "https://www.remind.com",
        "Google Forms":                   "https://forms.google.com",
        "Padlet":                         "https://padlet.com",
    }

    tools_row = tk.Frame(body, bg=rec["bg"])
    tools_row.pack(anchor="w")

    for tool in active_tools:
        url = TOOL_URLS.get(tool, "")
        btn = tk.Label(tools_row, text=f"  {tool}  ", font=("Poppins", 10),
                       bg=rec["border"], fg="#ffffff",
                       padx=8, pady=4, relief="flat",
                       cursor="hand2" if url else "arrow")
        btn.pack(side="left", padx=4)
        if url:
            btn.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg="#E8A820", bg="#1A3A5C"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#ffffff", bg=rec["border"]))

    footer = tk.Frame(popup, bg=rec["bg"], pady=10)
    footer.pack(fill="x")
    tk.Button(footer, text="CLOSE", font=("Poppins", 10, "bold"),
              bg=rec["border"], fg=rec["fg"],
              relief="flat", padx=80, pady=5,
              cursor="hand2", command=popup.destroy).pack()


# ── ANALYSIS SUMMARY POPUP ────────────────────────────────────────────────────
def open_ml_info_popup(parent, stats):
    popup = tk.Toplevel(parent)
    popup.title("How Your Students Were Analyzed")
    popup.configure(bg="#111827")
    popup.resizable(True, True)
    popup.grab_set()
    popup.update_idletasks()
    pw, ph = 820, 640
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    px = (sw // 2) - (pw // 2)
    py = (sh // 2) - (ph // 2)
    popup.geometry(f"{pw}x{ph}+{px}+{py}")
    popup.minsize(700, 480)

    algo_configs = [
        {
            "step":  "Step 1",
            "name":  "Student Grouping",
            "color": "#38bdf8",
            "role":  (
                "The system looked at each student's scores and absences, then automatically "
                "sorted them into groups (A, B, C, D) based on how similar they performed. "
                "No manual sorting needed — it finds the natural performance tiers in your class."
            ),
            "key":   "kmeans",
        },
        {
            "step":  "Step 2",
            "name":  "Teaching Recommendation Engine",
            "color": "#4ade80",
            "role":  (
                "After grouping, the Decision Tree analyzed each group's score patterns to "
                "identify which academic factor (quizzes, exams, activities, or absences) has "
                "the greatest impact on each group's performance. This powers the AI-driven "
                "focus area shown in each group's Teaching Recommendations popup."
            ),
            "key":   "dtree",
        },
        {
            "step":  "Step 3",
            "name":  "Predicting New Students",
            "color": "#f59e0b",
            "role":  (
                "Now that your class has been analyzed, you can enter any new student's data "
                "and the system will instantly predict which group they belong to — by comparing "
                "them to your existing students and finding the closest match. "
                "Predicted students are also added to the Student Record for future reference."
            ),
            "key":   "knn",
        },
    ]

    MULTI_ROW_KEYS = {"Influence of each factor", "Students per group"}

    hdr = tk.Frame(popup, bg="#1A3A5C", pady=14)
    hdr.pack(fill="x", side="top")
    tk.Label(hdr, text="How Your Students Were Analyzed",
             font=("Poppins", 14, "bold"),
             bg="#1A3A5C", fg="#E8A820").pack()
    tk.Label(hdr, text="Three steps were used to group, assess, and predict student performance.",
             font=("Poppins", 9), bg="#1A3A5C", fg="#9ca3af").pack(pady=(2, 0))

    footer = tk.Frame(popup, bg="#111827", pady=8)
    footer.pack(fill="x", side="bottom")
    tk.Button(footer, text="   CLOSE   ", font=("Poppins", 10, "bold"),
              bg="#1A3A5C", fg="#E8A820",
              relief="flat", padx=80, pady=6,
              cursor="hand2", command=popup.destroy).pack()

    scroll_container = tk.Frame(popup, bg="#111827")
    scroll_container.pack(fill="both", expand=True, side="top")

    canvas = tk.Canvas(scroll_container, bg="#111827", highlightthickness=0)
    sb     = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, bg="#111827")
    cw   = canvas.create_window((0, 0), window=body, anchor="nw")

    def on_body_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(e):
        canvas.itemconfig(cw, width=e.width)
        new_wrap = max(200, e.width - 72)
        for lbl in body._wrap_labels:
            lbl.config(wraplength=new_wrap)

    body.bind("<Configure>", on_body_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    popup.protocol("WM_DELETE_WINDOW", lambda: (canvas.unbind_all("<MouseWheel>"), popup.destroy()))

    body._wrap_labels = []

    for cfg in algo_configs:
        card  = tk.Frame(body, bg="#1E2433")
        card.pack(fill="x", padx=20, pady=8)
        inner = tk.Frame(card, bg="#1E2433", padx=16, pady=14)
        inner.pack(fill="x")

        badge_row = tk.Frame(inner, bg="#1E2433")
        badge_row.pack(fill="x", anchor="w")
        tk.Label(badge_row, text=cfg["step"], font=("Poppins", 9, "bold"),
                 bg="#1E2433", fg="#6b7280").pack(side="left")
        tk.Label(badge_row, text=f"  —  {cfg['name']}", font=("Poppins", 13, "bold"),
                 bg="#1E2433", fg=cfg["color"]).pack(side="left")

        role_lbl = tk.Label(inner, text=cfg["role"], font=("Poppins", 10),
                            bg="#1E2433", fg="#d1d5db",
                            justify="left", anchor="w", wraplength=700)
        role_lbl.pack(fill="x", anchor="w", pady=(8, 12))
        body._wrap_labels.append(role_lbl)

        tk.Frame(inner, bg="#374151", height=1).pack(fill="x", pady=(0, 10))

        info = stats.get(cfg["key"], {})
        for k, v in info.items():
            v_str = str(v)
            if k in MULTI_ROW_KEYS and "|" in v_str:
                tk.Label(inner, text=f"{k}:", font=("Poppins", 10, "bold"),
                         bg="#1E2433", fg="#e2e8f0", anchor="w").pack(fill="x", pady=(4, 0))
                for part in [p.strip() for p in v_str.split("|") if p.strip()]:
                    tk.Label(inner, text=f"    •  {part}", font=("Poppins", 10),
                             bg="#1E2433", fg=cfg["color"], anchor="w").pack(fill="x")
            else:
                stat_row = tk.Frame(inner, bg="#1E2433")
                stat_row.pack(fill="x", pady=3)
                tk.Label(stat_row, text=f"{k}:", font=("Poppins", 10, "bold"),
                         bg="#1E2433", fg="#e2e8f0", anchor="w", width=30).pack(side="left")
                tk.Label(stat_row, text=v_str, font=("Poppins", 10),
                         bg="#1E2433", fg=cfg["color"],
                         anchor="w", justify="left", wraplength=380).pack(side="left", fill="x", expand=True)


# ── PREDICT NEW STUDENT POPUP ─────────────────────────────────────────────────
def open_predict_popup(parent, knn_model, scaler, student_list, on_student_added, switch_to_record_cb):
    popup = tk.Toplevel(parent)
    popup.title("Predict New Student")
    popup.configure(bg="#111827")
    popup.resizable(False, False)
    popup.grab_set()
    popup.update_idletasks()
    w, h = 520, 560
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    popup.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    hdr = tk.Frame(popup, bg="#1A3A5C", pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text="Predict New Student Performance",
             font=("Poppins", 13, "bold"), bg="#1A3A5C", fg="#E8A820").pack()
    tk.Label(hdr, text="Enter a student's details to predict their group. They will be added to the Student Record.",
             font=("Poppins", 9), bg="#1A3A5C", fg="#9ca3af", wraplength=480).pack()

    body = tk.Frame(popup, bg="#111827", padx=30, pady=20)
    body.pack(fill="both", expand=True)

    fields = [
        ("First Name",     "text"),
        ("Last Name",      "text"),
        ("Subject",        "text"),
        ("Section",        "text"),
        ("Absences",       "number"),
        ("Quizzes (%)",    "number"),
        ("Exam (%)",       "number"),
        ("Activities (%)", "number"),
    ]
    entries = []
    for label, ftype in fields:
        row = tk.Frame(body, bg="#111827")
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, font=("Poppins", 10, "bold"),
                 bg="#111827", fg="#e2e8f0", width=16, anchor="w").pack(side="left")

        if label == "Subject":
            var = tk.StringVar(value=SUBJECT_OPTIONS[0])
            e = ttk.Combobox(row, textvariable=var,
                             values=SUBJECT_OPTIONS,
                             font=("Poppins", 10),
                             state="readonly",
                             style="Dark.TCombobox",
                             width=24)
            e.pack(side="left", padx=8, ipady=4)
            entries.append((e, ftype))

        elif label == "Section":
            var = tk.StringVar(value=SECTION_OPTIONS[0])
            e = ttk.Combobox(row, textvariable=var,
                             values=SECTION_OPTIONS,
                             font=("Poppins", 10),
                             state="readonly",
                             style="Dark.TCombobox",
                             width=24)
            e.pack(side="left", padx=8, ipady=4)
            entries.append((e, ftype))

        else:
            e = tk.Entry(row, font=("Poppins", 10),
                         bg="#1E2433", fg="white", relief="flat",
                         highlightthickness=2, highlightbackground="#374151",
                         highlightcolor="#E8A820", insertbackground="white", width=26)
            e.pack(side="left", padx=8, ipady=4)
            entries.append((e, ftype))

    result_frame  = tk.Frame(body, bg="#111827")
    result_frame.pack(fill="x", pady=(14, 0))
    result_group  = tk.Label(result_frame, text="", font=("Poppins", 12, "bold"),
                             bg="#111827", fg="#E8A820")
    result_group.pack()
    result_status = tk.Label(result_frame, text="", font=("Poppins", 11),
                             bg="#111827", fg="#9ca3af")
    result_status.pack()
    result_tip    = tk.Label(result_frame, text="", font=("Poppins", 9, "italic"),
                             bg="#111827", fg="#6b7280", wraplength=420)
    result_tip.pack()

    group_colors = {"A": "#4ade80", "B": "#38bdf8", "C": "#f87171", "D": "#fbbf24"}

    predicted_data = {}

    def predict():
        errors = []
        vals   = {}

        first = entries[0][0].get().strip()
        last  = entries[1][0].get().strip()
        subj  = entries[2][0].get().strip()
        sect  = entries[3][0].get().strip()

        if not first:   errors.append("First Name is required.")
        if not last:    errors.append("Last Name is required.")
        if not subj:    errors.append("Subject is required.")
        if not sect:    errors.append("Section is required.")

        for label, (e, ftype) in zip([f[0] for f in fields[4:]], entries[4:]):
            raw = e.get().strip().replace("%", "")
            if not raw:
                errors.append(f"{label} is required.")
                continue
            try:
                num = float(raw)
            except ValueError:
                errors.append(f"{label} must be a number.")
                continue
            name = label.replace(" (%)", "").lower()
            if name == "absences" and num < 0:
                errors.append("Absences cannot be negative.")
                continue
            if name in ("quizzes", "exam", "activities (%)"):
                name = label.replace(" (%)", "").lower()
            if name != "absences" and not (0 <= num <= 100):
                errors.append(f"{label} must be between 0 and 100.")
                continue
            vals[name] = num

        if errors:
            messagebox.showerror("Input Error", "\n".join(errors), parent=popup)
            return

        absences   = vals.get("absences", 0)
        quizzes    = vals.get("quizzes", 0)
        exam       = vals.get("exam", 0)
        activities = vals.get("activities (%)", vals.get("activities", 0))

        # Collect activities with fallback
        num_vals = []
        for label, (e, ftype) in zip([f[0] for f in fields[4:]], entries[4:]):
            raw = e.get().strip().replace("%", "")
            num_vals.append(float(raw))

        absences, quizzes, exam, activities = num_vals

        X_raw    = np.array([[absences, quizzes, exam, activities]])
        X_scaled = scaler.transform(X_raw)

        predicted_group  = knn_model.predict(X_scaled)[0]
        predicted_status = compute_pass_fail(absences, quizzes, exam, activities)

        group_name = RECOMMENDATIONS[predicted_group]["title"]
        color      = group_colors.get(predicted_group, "#E8A820")
        status_col = "#4ade80" if predicted_status == "PASS" else "#f87171"
        tip        = RECOMMENDATIONS[predicted_group]["strategies"][0]

        result_group.config(text=f"Predicted Group: {predicted_group}  ({group_name})", fg=color)
        result_status.config(text=f"Predicted Status: {predicted_status}", fg=status_col)
        result_tip.config(text=f"Tip: {tip}", fg="#9ca3af")

        predicted_data.update({
            "first_name": first,
            "last_name":  last,
            "subject":    subj,
            "section":    sect,
            "absences":   int(absences),
            "quizzes":    int(quizzes),
            "exam":       int(exam),
            "activities": int(activities),
            "group":      predicted_group,
            "status":     predicted_status,
        })

    def add_to_record():
        if not predicted_data:
            messagebox.showwarning("No Prediction", "Run a prediction first.", parent=popup)
            return
        on_student_added(dict(predicted_data))
        popup.destroy()
        switch_to_record_cb()

    btn_row = tk.Frame(body, bg="#111827")
    btn_row.pack(fill="x", pady=(12, 0))
    tk.Button(btn_row, text="   PREDICT   ", font=("Poppins", 10, "bold"),
              bg="#E8A820", fg="#1a1a1a", relief="flat", padx=60, pady=6,
              cursor="hand2", command=predict).pack(side="left")
    tk.Button(btn_row, text="  ADD TO RECORD  ", font=("Poppins", 10, "bold"),
              bg="#1A3A5C", fg="#38bdf8", relief="flat", padx=20, pady=6,
              cursor="hand2", command=add_to_record).pack(side="left", padx=6)
    tk.Button(btn_row, text="   CLOSE   ", font=("Poppins", 10),
              bg="#1E2433", fg="#9ca3af", relief="flat", padx=40, pady=6,
              cursor="hand2", command=popup.destroy).pack(side="left", padx=4)


# ── EDIT STUDENT POPUP ────────────────────────────────────────────────────────
def open_edit_popup(parent, student, on_save, uid):
    """Popup to edit a student's record and persist to DB."""
    popup = tk.Toplevel(parent)
    popup.title("Edit Student Record")
    popup.configure(bg="#111827")
    popup.resizable(False, False)
    popup.grab_set()
    popup.update_idletasks()
    w, h = 460, 460
    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    popup.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    hdr = tk.Frame(popup, bg="#1A3A5C", pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text="Edit Student Record", font=("Poppins", 13, "bold"),
             bg="#1A3A5C", fg="#E8A820").pack()
    tk.Label(hdr, text="Update details then click SAVE.",
             font=("Poppins", 9), bg="#1A3A5C", fg="#9ca3af").pack()

    body = tk.Frame(popup, bg="#111827", padx=30, pady=20)
    body.pack(fill="both", expand=True)

    fields = [
        ("First Name",     "first_name",  False),
        ("Last Name",      "last_name",   False),
        ("Subject",        "subject",     False),
        ("Section",        "section",     False),
        ("Absences",       "absences",    True),
        ("Quizzes (%)",    "quizzes",     True),
        ("Exam (%)",       "exam",        True),
        ("Activities (%)", "activities",  True),
    ]

    entries = {}
    for label, key, is_num in fields:
        row = tk.Frame(body, bg="#111827")
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, font=("Poppins", 10, "bold"),
                 bg="#111827", fg="#e2e8f0", width=16, anchor="w").pack(side="left")

        # ── Subject and Section use dropdowns ──────────────────────────────
        if key == "subject":
            var = tk.StringVar(value=student.get("subject", SUBJECT_OPTIONS[0]))
            e = ttk.Combobox(row, textvariable=var,
                             values=SUBJECT_OPTIONS,
                             font=("Poppins", 10),
                             state="readonly",
                             style="Dark.TCombobox",
                             width=20)
            e.pack(side="left", padx=8, ipady=4)
            entries[key] = (e, False)

        elif key == "section":
            var = tk.StringVar(value=student.get("section", SECTION_OPTIONS[0]))
            e = ttk.Combobox(row, textvariable=var,
                             values=SECTION_OPTIONS,
                             font=("Poppins", 10),
                             state="readonly",
                             style="Dark.TCombobox",
                             width=20)
            e.pack(side="left", padx=8, ipady=4)
            entries[key] = (e, False)

        else:
            def _no_digits_edit(new_val):
                return not any(c.isdigit() for c in new_val)
            name_vcmd_edit = (popup.register(_no_digits_edit), '%P')

            e = tk.Entry(row, font=("Poppins", 10),
                         bg="#1E2433", fg="white", relief="flat",
                         highlightthickness=2, highlightbackground="#374151",
                         highlightcolor="#E8A820", insertbackground="white", width=22)
            if key in ("first_name", "last_name"):
                e.config(validate="key", validatecommand=name_vcmd_edit)
            e.insert(0, str(student.get(key, "")))
            e.pack(side="left", padx=8, ipady=4)
            entries[key] = (e, is_num)

    def save():
        errors  = []
        updated = {}
        for key, (e, is_num) in entries.items():
            val = e.get().strip()
            # Paste-safety for name fields
            if key in ("first_name", "last_name") and not is_num:
                if any(c.isdigit() for c in val):
                    errors.append(f"{key.replace('_',' ').title()} must contain letters only.")
                    continue
            if not val:
                errors.append(f"{key.replace('_', ' ').title()} is required.")
                continue
            if is_num:
                try:
                    num = float(val.replace("%", ""))
                    if key == "absences" and num < 0:
                        errors.append("Absences cannot be negative.")
                        continue
                    if key in ("quizzes", "exam", "activities") and not (0 <= num <= 100):
                        errors.append(f"{key.title()} must be 0–100.")
                        continue
                    updated[key] = int(num)
                except ValueError:
                    errors.append(f"{key.title()} must be a number.")
                    continue
            else:
                updated[key] = val

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors), parent=popup)
            return

        updated["status"] = compute_pass_fail(
            updated["absences"], updated["quizzes"], updated["exam"], updated["activities"]
        )
        updated["group"] = student.get("group", "—")

        # Persist to DB
        def run_update():
            try:
                update_student(
                    uid=uid,
                    original_first=student.get("first_name", ""),
                    original_last=student.get("last_name", ""),
                    new_data=updated
                )
                popup.after(0, lambda: on_save(updated))
                popup.after(0, popup.destroy)
            except Exception as ex:
                popup.after(0, lambda msg=str(ex): messagebox.showerror("DB Error", msg, parent=popup))

        threading.Thread(target=run_update, daemon=True).start()

    btn_row = tk.Frame(body, bg="#111827")
    btn_row.pack(fill="x", pady=(14, 0))
    tk.Button(btn_row, text="   SAVE   ", font=("Poppins", 10, "bold"),
              bg="#E8A820", fg="#1a1a1a", relief="flat", padx=60, pady=6,
              cursor="hand2", command=save).pack(side="left")
    tk.Button(btn_row, text="   CANCEL   ", font=("Poppins", 10),
              bg="#1E2433", fg="#9ca3af", relief="flat", padx=60, pady=6,
              cursor="hand2", command=popup.destroy).pack(side="left", padx=8)


# ── MAIN APP CLASS ────────────────────────────────────────────────────────────
class StudentClassifier:

    def __init__(self, root):
        self.root         = root
        self.uid          = self.load_uid()
        self.root.title("Student Performance Classifier")
        self.root.configure(bg="#1a1a1a")

        self.entry_widgets  = []
        self.row_frames     = []
        self.student_list   = []
        self._filtered_list = []

        self.kmeans_model = None
        self.dt_model     = None
        self.knn_model    = None
        self.scaler       = None
        self.le           = LabelEncoder()
        self.ml_stats     = {}
        self.dt_insights  = {}   # group → AI insight string

        self._dashboard_visible = False

        self.build_ui()

    def load_uid(self):
        with open("session.json", "r") as f:
            session = json.load(f)
        return session["UID"]

    def logout(self):
        confirmed = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirmed:
            try:
                with open("session.json", "w") as f:
                    json.dump({}, f)
            except Exception:
                pass
            self.root.destroy()

    # ── UI CONSTRUCTION ───────────────────────────────────────────────────────
    def build_ui(self):
        bg_image = Image.open(asset("images/bglspu.png"))
        bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.root, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        logout_btn = tk.Button(self.root, text="LOGOUT",
                               font=("Poppins", 10, "bold"),
                               bg="#AA0404", fg="#ffffff",
                               activebackground="#2E1F0A", activeforeground="#f87171",
                               relief="flat", padx=14, pady=6,
                               cursor="hand2", command=self.logout)
        logout_btn.place(relx=1.0, x=-14, y=14, anchor="ne")

        # Header
        self.header = tk.Frame(self.root, bg="#111827")
        self.header.pack(fill="x", padx=150, pady=(10, 0))

        tk.Label(self.header, text="STUDENT PERFORMANCE CLASSIFIER",
                 font=("Poppins", 30, "bold"),
                 bg="#111827", fg="#E8A820",
                 anchor="center", justify="center").pack(fill="x", pady=(60, 0))
        tk.Label(self.header, text="Teaching Recommendation System",
                 font=("Poppins", 20),
                 bg="#111827", fg="#9ca3af",
                 anchor="center", justify="center").pack(fill="x", pady=(6, 0))
        tk.Frame(self.header, bg="#493405", height=1).pack(fill="x", pady=(18, 0))

        # ── Tab bar — full-width rectangle buttons, flush to header bottom ──
        self.tab_bar = tk.Frame(self.header, bg="#111827")
        self.tab_bar.pack(fill="x", side="bottom")
        # ── Bottom border under tabs ───────────────────────────────────────
        tk.Frame(self.header, bg="#E8A820", height=2).pack(fill="x", side="bottom")
        for i in range(2):
            self.tab_bar.columnconfigure(i, weight=1, uniform="tab")

        def make_tab(col, text, key):
            lbl = tk.Label(self.tab_bar, text=text,
                           font=("Poppins", 12, "bold"),
                           bg="#1E2433", fg="#6b7280",
                           cursor="hand2",
                           anchor="center",
                           pady=12,
                           relief="flat")
            lbl.grid(row=0, column=col, sticky="nsew")
            lbl.bind("<Button-1>", lambda e, k=key: self.switch_tab(k))
            lbl.bind("<Enter>", lambda e, l=lbl, k=key: (
                l.config(bg="#2D3748", fg="#E8A820")
                if self._active_tab != k else None
            ))
            lbl.bind("<Leave>", lambda e, l=lbl, k=key: l.config(
                bg="#1A3A5C" if self._active_tab == k else "#1E2433",
                fg="#E8A820" if self._active_tab == k else "#6b7280"
            ))
            return lbl, lbl

        self.tab_input_btn,  self.input_underline  = make_tab(0, "STUDENT INPUT",  "input")

        # ── ADD: vertical separator between the two tabs ───────────────────
        sep = tk.Frame(self.tab_bar, bg="#493405", width=2)
        sep.grid(row=0, column=0, sticky="nse", pady=4)

        self.tab_record_btn, self.record_underline = make_tab(1, "STUDENT RECORD", "record")

        # Body
        self.body = tk.Frame(self.root, bg="#0D1117")
        self.body.pack(fill="both", expand=True, padx=150, pady=(0, 10))

        self.frame_input  = tk.Frame(self.body, bg="#0D1117")
        self.frame_record = tk.Frame(self.body, bg="#0D1117")

        self.build_input_tab()
        self.build_record_tab()

        for f in (self.frame_input, self.frame_record):
            f.pack_forget()

        for lbl in (self.tab_input_btn, self.tab_record_btn):
            lbl.config(fg="#6b7280", font=("Poppins", 12, "bold"),
                       bg="#1E2433")
        # input_underline / record_underline now same as label — no separate reset

    def switch_tab(self, tab):
        frames    = {"input": self.frame_input, "record": self.frame_record}
        labels    = {"input": self.tab_input_btn, "record": self.tab_record_btn}
        underlines = {"input": self.input_underline, "record": self.record_underline}

        for f in frames.values():
            f.pack_forget()
        for lbl in labels.values():
            lbl.config(fg="#6b7280", font=("Poppins", 12, "bold"),
                       bg="#1E2433")

        frames[tab].pack(fill="both", expand=True)
        self._active_tab = tab
        labels[tab].config(fg="#E8A820", font=("Poppins", 12, "bold"),
                           bg="#1A3A5C")
        # underlines are now the same label object — no separate update needed

        if tab == "record":
            self.render_record_table()
            if self._dashboard_visible:
                self._collapse_dashboard()

    # ── DASHBOARD PANEL (inside Student Record tab) ───────────────────────────
    def build_dashboard_panel(self, parent):
        """Build a collapsible dashboard panel pinned above the record table."""
        self._dash_panel_outer = tk.Frame(parent, bg="#0D1117")
        self._dash_panel_outer.pack(fill="x", padx=30, pady=(10, 0))

    # Toggle header — label only, no buttons here
        toggle_bar = tk.Frame(self._dash_panel_outer, bg="#1A3A5C", pady=6)
        toggle_bar.pack(fill="x")

        self._dash_toggle_lbl = tk.Label(
            toggle_bar, text="▼  ANALYSIS DASHBOARD",
            font=("Poppins", 11, "bold"), bg="#1A3A5C", fg="#E8A820", cursor="hand2"
        )
        self._dash_toggle_lbl.pack(side="left", padx=12)
        self._dash_toggle_lbl.bind("<Button-1>", lambda e: self.toggle_dashboard())

    # Collapsible body
        self._dash_panel_body = tk.Frame(self._dash_panel_outer, bg="#111827")
        # self._dash_panel_body.pack(fill="x")

        outer = tk.Frame(self._dash_panel_body, bg="#111827", padx=0, pady=10)
        outer.pack(fill="x")

    # ── Action buttons row (inside collapsible body) ──────────────────────
        btn_strip = tk.Frame(outer, bg="#111827")
        btn_strip.pack(fill="x", pady=(0, 12))

        tk.Button(btn_strip, text="  ▶  CLUSTER NOW  ",
                font=("Poppins", 9, "bold"),
                bg="#E8A820", fg="#1a1a1a",
                relief="flat", padx=12, pady=6,
                cursor="hand2", command=self.run_clustering).pack(side="left", padx=(0, 6))

        self.dash_predict_btn = tk.Button(
            btn_strip, text="  🔍  PREDICT NEW  ",
            font=("Poppins", 9, "bold"),
            bg="#0F2D40", fg="#38bdf8",
            relief="flat", padx=12, pady=6,
            cursor="hand2", state="disabled",
            command=self.open_predict
        )
        self.dash_predict_btn.pack(side="left", padx=6)

    # Stat cards row
        cards_row = tk.Frame(outer, bg="#111827")
        cards_row.pack(fill="x", pady=(0, 10))
        for i in range(4):
            cards_row.columnconfigure(i, weight=1, uniform="card")

        card_defs = [
            ("Total Students", "total_card_val",  "#38bdf8", "👥"),
            ("PASS",           "pass_card_val",   "#4ade80", "✅"),
            ("FAIL",           "fail_card_val",   "#f87171", "❌"),
            ("Groups Formed",  "group_card_val",  "#fbbf24", "📊"),
        ]
        for col, (title, attr, color, icon) in enumerate(card_defs):
            card = tk.Frame(cards_row, bg="#1E2433", padx=16, pady=12)
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            tk.Label(card, text=icon, font=("Poppins", 18),
                bg="#1E2433", fg=color).pack(anchor="w")
            val_lbl = tk.Label(card, text="—", font=("Poppins", 22, "bold"),
                bg="#1E2433", fg=color)
            val_lbl.pack(anchor="w")
            tk.Label(card, text=title, font=("Poppins", 9),
                bg="#1E2433", fg="#9ca3af").pack(anchor="w")
            setattr(self, attr, val_lbl)

    # Group breakdown row
        groups_row = tk.Frame(outer, bg="#111827")
        groups_row.pack(fill="x", pady=(0, 10))
        for i in range(4):
            groups_row.columnconfigure(i, weight=1, uniform="grp")

        group_palette = {
            "A": ("#0F2D1F", "#4ade80", "⭐ Group A", "High Performers"),
            "B": ("#0A1F2E", "#38bdf8", "📈 Group B", "Avg & Improving"),
            "C": ("#2E0F0F", "#f87171", "🆘 Group C", "Struggling"),
            "D": ("#2E1F0A", "#fbbf24", "🔄 Group D", "Inconsistent"),
        }
        self.group_count_labels = {}
        for col, (letter, (bg, fg, title, sub)) in enumerate(group_palette.items()):
            card = tk.Frame(groups_row, bg=bg, padx=12, pady=10)
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            tk.Label(card, text=title, font=("Poppins", 11, "bold"),
                    bg=bg, fg=fg).pack(anchor="w")
            tk.Label(card, text=sub, font=("Poppins", 8),
                    bg=bg, fg="#9ca3af").pack(anchor="w")
            cnt = tk.Label(card, text="—", font=("Poppins", 20, "bold"),
                        bg=bg, fg=fg)
            cnt.pack(anchor="w", pady=(4, 0))
            tk.Label(card, text="students", font=("Poppins", 8),
                    bg=bg, fg="#9ca3af").pack(anchor="w")
            btn = tk.Button(card, text="View Tips",
                            font=("Poppins", 8, "bold"),
                            bg=bg, fg=fg, relief="flat",
                            cursor="hand2",
                            command=lambda l=letter: self._open_rec_with_insight(l))
            btn.pack(anchor="w", pady=(6, 0))
            self.group_count_labels[letter] = cnt

        # Influence bars
        influence_card = tk.Frame(outer, bg="#1E2433", padx=16, pady=12)
        influence_card.pack(fill="x", pady=(0, 4))

        # Header row with title + "Click for More Information" button side by side
        inf_header_row = tk.Frame(influence_card, bg="#1E2433")
        inf_header_row.pack(fill="x", pady=(0, 8))

        tk.Label(inf_header_row, text="Factor Influence on Teaching Recommendations (Decision Tree)",
                font=("Poppins", 10, "bold"),
                bg="#1E2433", fg="#E8A820").pack(side="left")

        self.dash_analysis_btn = tk.Button(
            inf_header_row, text="  📊  Click for More Information  ",
            font=("Poppins", 9, "bold"),
            bg="#1A3A5C", fg="#E8A820",
            relief="flat", padx=10, pady=4,
            cursor="hand2", state="disabled",
            command=self.show_ml_info
        )
        self.dash_analysis_btn.pack(side="right")

        self.influence_bars = {}
        factor_colors = [
            ("Absences",   "#f87171"),
            ("Quizzes",    "#38bdf8"),
            ("Exam",       "#4ade80"),
            ("Activities", "#fbbf24"),
        ]

        # 2-column grid container
        bars_grid = tk.Frame(influence_card, bg="#1E2433")
        bars_grid.pack(fill="x")
        bars_grid.columnconfigure(0, weight=1, uniform="barcol")
        bars_grid.columnconfigure(1, weight=1, uniform="barcol")

        for idx, (factor, color) in enumerate(factor_colors):
            grid_row = idx // 2
            grid_col = idx % 2

            cell = tk.Frame(bars_grid, bg="#1E2433", padx=(0 if grid_col == 0 else 8))
            cell.grid(row=grid_row, column=grid_col, sticky="ew", pady=4)

            tk.Label(cell, text=factor, font=("Poppins", 10),
                    bg="#1E2433", fg="#e2e8f0", width=12, anchor="w").pack(side="left")
            bar_bg = tk.Frame(cell, bg="#374151", height=14)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 6))
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=color, height=14, width=0)
            bar_fill.place(x=0, y=0, relheight=1)
            pct_lbl = tk.Label(cell, text="—", font=("Poppins", 9),
                            bg="#1E2433", fg=color)
            pct_lbl.pack(side="left")
            self.influence_bars[factor] = (bar_fill, pct_lbl, bar_bg)

    def toggle_dashboard(self):
        if self._dashboard_visible:
            self._dash_panel_body.pack_forget()
            self._dash_toggle_lbl.config(text="▶  ANALYSIS DASHBOARD  (click to expand)")
            self._dashboard_visible = False
            self._active_tab = "input"
        else:
            self._dash_panel_body.pack(fill="x")
            self._dash_toggle_lbl.config(text="▼  ANALYSIS DASHBOARD")
            self._dashboard_visible = True
            if self._chart_importances is not None:       # ← ADDED
                self.root.after(80, self._render_chart) 

    def _collapse_dashboard(self):
        if self._dashboard_visible:
            self._dash_panel_body.pack_forget()
            self._dash_toggle_lbl.config(text="▶  ANALYSIS DASHBOARD  (click to expand)")
            self._dashboard_visible = False

    def _open_rec_with_insight(self, letter):
        insight = self.dt_insights.get(letter)
        open_recommendation_popup(self.root, letter, dt_insight=insight)

    def refresh_dashboard(self):
        data   = self.student_list
        total  = len(data)
        passes = sum(1 for s in data if s.get("status") == "PASS")
        fails  = total - passes
        groups_formed = len(set(s.get("group", "—") for s in data if s.get("group") not in ("—", None)))

        self.total_card_val.config(text=str(total))
        self.pass_card_val.config(text=str(passes))
        self.fail_card_val.config(text=str(fails))
        self.group_card_val.config(text=str(groups_formed))

        group_counts = {}
        for s in data:
            g = s.get("group", "—")
            if g != "—":
                group_counts[g] = group_counts.get(g, 0) + 1
        for letter, lbl in self.group_count_labels.items():
            lbl.config(text=str(group_counts.get(letter, 0)))

        if self.dt_model is not None:
            importances = self.dt_model.feature_importances_
            self.root.after(200, lambda: self._draw_influence_bars(
                ["Absences", "Quizzes", "Exam", "Activities"], importances))

        self.dash_predict_btn.config(state="normal")
        self.dash_analysis_btn.config(state="normal")

    def _draw_influence_bars(self, feature_names, importances):
        for i, factor in enumerate(feature_names):
            if factor in self.influence_bars:
                bar_fill, pct_lbl, bar_bg = self.influence_bars[factor]
                bar_bg.update_idletasks()
                total_w = bar_bg.winfo_width()
                pct     = importances[i]
                fill_w  = int(total_w * pct)
                bar_fill.place(x=0, y=0, width=fill_w, relheight=1)
                pct_lbl.config(text=f"{int(round(pct * 100))}%")

    # ── STUDENT INPUT TAB ─────────────────────────────────────────────────────
    # NOTE: Auto-fill Subject/Section removed — enter per-row directly.
    def build_input_tab(self):
        # Count + generate row
        setup = tk.Frame(self.frame_input, bg="#0D1117", pady=8)
        setup.pack(fill="x", padx=30)
 
        tk.Label(setup, text="HOW MANY STUDENTS: ",
                 font=("Poppins", 11, "bold"), bg="#0D1117", fg="#ffffff").pack(side="left", padx=6)
 
        self.count_var   = tk.IntVar(value=1)
        self.count_label = tk.Label(setup, text="1", font=("Poppins", 13, "bold"),
                                    bg="#0D1117", fg="#E8A820", width=3)
        self.count_label.pack(side="left", padx=(0, 6))
 
        def update_label(val):
            self.count_label.config(text=str(int(float(val))))
 
        tk.Scale(setup, from_=1, to=100, orient="horizontal",
                 variable=self.count_var, command=update_label,
                 length=300, showvalue=False,
                 bg="#0D1117", fg="#E8A820", highlightthickness=0,
                 troughcolor="#1E2433", activebackground="#E8A820",
                 sliderlength=18, width=18,
                 font=("Poppins", 10)).pack(side="left", padx=4)
 
        tk.Button(setup, text="   GENERATE ROW/S   ", command=self.generate_roster,
                  bg="#1a1a1a", fg="#E8A820", font=("Poppins", 10, "bold"),
                  relief="flat", padx=10, pady=4).pack(side="left", padx=8)
 
        tk.Button(setup, text="      + ADD ROW      ", command=self.add_row,
                  bg="#3B6D11", fg="#0D1117", font=("Poppins", 10, "bold"),
                  relief="flat", padx=10, pady=4).pack(side="left", padx=8)
        tk.Button(setup, text="   📂 IMPORT EXCEL   ", command=self.import_excel,
                bg="#1A3A5C", fg="#38bdf8", font=("Poppins", 10, "bold"),
                relief="flat", padx=10, pady=4).pack(side="left", padx=8)

        # Column headers
        col_labels  = ("#", "First Name", "Last Name", "Subject", "Section",
                       "Absences", "Quizzes (%)", "Exam (%)", "Activities (%)", "")
        col_weights = (1, 3, 3, 3, 2, 2, 2, 2, 2, 1)

        col_hdr = tk.Frame(self.frame_input, bg="#3A3010")
        col_hdr.pack(fill="x", padx=30)
        for i, (lbl, wt) in enumerate(zip(col_labels, col_weights)):
            col_hdr.columnconfigure(i, weight=wt, uniform="hdr")
            tk.Label(col_hdr, text=lbl, font=("Poppins", 11, "bold"),
                     bg="#3A3010", fg="#E8A820",
                     anchor="center", pady=8).grid(row=0, column=i, sticky="ew")

        # Scrollable rows area
        canvas_frame = tk.Frame(self.frame_input, bg="#0D1117")
        canvas_frame.pack(fill="both", expand=True, padx=(30, 30))
        self.canvas = tk.Canvas(canvas_frame, bg="#0D1117", highlightthickness=0)

        style = ttk.Style()
        style.theme_use("clam")
        # ── Dark Combobox style to match row backgrounds ──────────────────────
        style.configure("Dark.TCombobox",
                        fieldbackground="#0D1117",
                        background="#0D1117",
                        foreground="white",
                        selectbackground="#1A3A5C",
                        selectforeground="#E8A820",
                        arrowcolor="#E8A820",
                        bordercolor="#9ca3af",
                        lightcolor="#0D1117",
                        darkcolor="#0D1117",
                        insertcolor="white")
        style.map("Dark.TCombobox",
                fieldbackground=[("readonly", "#0D1117"),
                                ("focus",    "#1A222E")],
                foreground=      [("readonly", "white")],
                selectbackground=[("readonly", "#1A3A5C")],
                background=      [("active",   "#1E2433"),
                                    ("readonly", "#0D1117")])

        style.configure("Vertical.TScrollbar",
                        background="#0D1117", troughcolor="#0D1117",
                        bordercolor="#0D1117", arrowcolor="#E8A820",
                        relief="flat", gripcount=0)
        style.map("Vertical.TScrollbar", background=[("active", "#1E2433")])

        sb = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview,
                           style="Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.rows_frame = tk.Frame(self.canvas, bg="#0D1117")
        self.cw = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.cw, width=e.width))

        def _input_scroll(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _input_scroll))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        btn_bar = tk.Frame(self.frame_input, bg="#111827", pady=0)
        btn_bar.pack(fill="x")

        tk.Label(btn_bar,
                 text="Laguna State Polytechnic University - San Pablo Campus | BS - Computer Science | OG - 6",
                 font=("Poppins", 10, "bold"), bg="#111827", fg="#9ca3af").pack(side="left", padx=12)

        tk.Button(btn_bar, text="SAVE & SUBMIT", command=self.save_to_db,
                  bg="#E8A820", fg="#1a1a1a", font=("Poppins", 10, "bold"),
                  relief="flat", padx=14, pady=6).pack(side="right", padx=12)

    def generate_roster(self):
        try:
            n = int(self.count_var.get())
            if n < 1 or n > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number (1–100).")
            return

        if self.entry_widgets:
            # Check if any existing row has data
            has_data = any(
                any(e.get().strip() for e in row)
                for row in self.entry_widgets
            )
            if has_data:
                confirmed = messagebox.askyesnocancel(
                    "Existing Data",
                    f"You have {len(self.entry_widgets)} existing row(s) with data.\n\n"
                    f"• YES — Add {n} new empty row(s) to the existing ones\n"
                    f"• NO — Clear all and start fresh with {n} row(s)\n"
                    f"• CANCEL — Do nothing"
                )
                if confirmed is None:   # CANCEL
                    return
                elif confirmed:         # YES — append
                    for _ in range(n):
                        self.add_row()
                    return
                else:                   # NO — clear and regenerate
                    for w in self.rows_frame.winfo_children():
                        w.destroy()
                    self.entry_widgets = []
                    self.row_frames    = []

        for _ in range(n):
            self.add_row()
        self.canvas.yview_moveto(0)

    def add_row(self):
        idx = len(self.entry_widgets)
        bg  = "#1A222E" if (idx + 1) % 2 == 0 else "#0D1117"
        col_weights = (1, 3, 3, 3, 2, 2, 2, 2, 2, 1)

        rf = tk.Frame(self.rows_frame, bg=bg, pady=2)
        rf.pack(fill="x")
        for i, wt in enumerate(col_weights):
            rf.columnconfigure(i, weight=wt, uniform="row")

        # ── Name validator: block digits ──────────────────────────────────
        def _no_digits(new_val):
            return not any(c.isdigit() for c in new_val)
        name_vcmd = (rf.register(_no_digits), '%P')

        tk.Label(rf, text=str(idx + 1), font=("Poppins", 12, "bold"),
                 bg=bg, fg="#E8A820", anchor="center").grid(row=0, column=0, sticky="ew", padx=2, pady=1)

        entries = []
        for i in range(8):
            # ── Column 2 = Subject dropdown ──────────────────────────────────
            if i == 2:
                var = tk.StringVar(value="")
                cb = ttk.Combobox(rf, textvariable=var,
                                  values=SUBJECT_OPTIONS,
                                  font=("Poppins", 10),
                                  state="readonly",
                                  style="Dark.TCombobox",
                                  justify="center")
                cb.grid(row=0, column=i + 1, sticky="ew", padx=2, pady=1, ipady=4)
                # Sync field color to alternating row bg on open/close
                cb.bind("<<ComboboxSelected>>",
                        lambda e, w=cb: w.configure(style="Dark.TCombobox"))
                cb._strvar = var
                entries.append(cb)
            # ── Column 3 = Section dropdown ──────────────────────────────────
            elif i == 3:
                var = tk.StringVar(value="")
                cb = ttk.Combobox(rf, textvariable=var,
                                  values=SECTION_OPTIONS,
                                  font=("Poppins", 10),
                                  state="readonly",
                                  style="Dark.TCombobox",
                                  justify="center")
                cb.grid(row=0, column=i + 1, sticky="ew", padx=2, pady=1, ipady=4)
                cb.bind("<<ComboboxSelected>>",
                        lambda e, w=cb: w.configure(style="Dark.TCombobox"))
                cb._strvar = var
                entries.append(cb)

        # ── All other columns = normal Entry ──────────────────────
            else:
                e = tk.Entry(rf, font=("Poppins", 10), justify="center",
                             relief="flat", bg=bg, fg="white",
                             highlightthickness=2, highlightbackground="#9ca3af",
                             highlightcolor="#E8A820")
                # First Name (i=0) and Last Name (i=1) block digits
                if i in (0, 1):
                    e.config(validate="key", validatecommand=name_vcmd)
                e.grid(row=0, column=i + 1, sticky="ew", padx=2, pady=1, ipady=5)

                if i >= 5:
                    def on_focus_out(event, entry=e):
                        val = entry.get().strip().replace("%", "")
                        if val:
                            entry.delete(0, tk.END)
                            entry.insert(0, val + "%")

                    def on_focus_in(event, entry=e):
                        val = entry.get().strip()
                        if val.endswith("%"):
                            entry.delete(0, tk.END)
                            entry.insert(0, val[:-1])

                    e.bind("<FocusOut>", on_focus_out)
                    e.bind("<FocusIn>",  on_focus_in)

                entries.append(e)

        tk.Button(rf, text="✕", font=("Poppins", 10, "bold"),
                  bg="#C79090", fg="#3A1A1A", relief="flat",
                  padx=4, pady=1, cursor="hand2",
                  command=lambda f=rf: self.confirm_delete_row(f)).grid(row=0, column=9, sticky="ew", padx=2)

        self.entry_widgets.append(entries)
        self.row_frames.append(rf)

    def confirm_delete_row(self, rf):
        if len(self.row_frames) == 1:
            messagebox.showwarning("Cannot Delete", "At least one row is required.")
            return
        idx = self.row_frames.index(rf) + 1
        confirmed = messagebox.askyesno(
            "Delete Row",
            f"Are you sure you want to delete Row {idx}?"
        )
        if confirmed:
            self.delete_row(rf)

    def delete_row(self, rf):
        i = self.row_frames.index(rf)
        self.row_frames.pop(i)
        self.entry_widgets.pop(i)
        rf.destroy()
        self.renumber_rows()

    def renumber_rows(self):
        for i, rf in enumerate(self.row_frames):
            for widget in rf.winfo_children():
                info = widget.grid_info()
                if info and info.get("column") == 0:   # int 0, not string "0"
                    widget.config(text=str(i + 1))
                    break

    # importing file
    def import_excel(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", ".xlsx *.xls"), ("CSV Files", ".csv")]
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            required = ["first_name", "last_name", "subject", "section", "absences", "quizzes", "exam", "activities"]
            missing  = [r for r in required if r not in df.columns]
            if missing:
                messagebox.showerror(
                    "Missing Columns",
                    f"Your file is missing these columns:\n{', '.join(missing)}\n\n"
                    f"Required columns:\nfirst_name, last_name, subject, section, absences, quizzes, exam, activities"
                )
                return

            # Clear existing rows
            for w in self.rows_frame.winfo_children():
                w.destroy()
            self.entry_widgets = []
            self.row_frames    = []

            records = []
            errors  = []

            for i, row in df.iterrows():
                try:
                    first      = str(row["first_name"]).strip()
                    last       = str(row["last_name"]).strip()
                    subject    = str(row["subject"]).strip()
                    section    = str(row["section"]).strip()
                    absences   = int(float(str(row["absences"]).strip()))
                    quizzes    = int(float(str(row["quizzes"]).strip().replace("%","")))
                    exam       = int(float(str(row["exam"]).strip().replace("%","")))
                    activities = int(float(str(row["activities"]).strip().replace("%","")))

                    if not first or not last:
                        errors.append(f"Row {i+2}: First/Last name missing.")
                        continue
                    if not subject or not section:
                        errors.append(f"Row {i+2}: Subject/Section missing.")
                        continue

                    records.append((first, last, absences, quizzes, exam, activities, subject, section, self.uid))

                    # Add visual row
                    self.add_row()
                    entries = self.entry_widgets[-1]
                    entries[0].insert(0, first)       # First Name
                    entries[1].insert(0, last)        # Last Name
                    # Subject — set dropdown if value matches, else default to first
                    if subject in SUBJECT_OPTIONS:
                        entries[2].set(subject)
                    else:
                        entries[2].set("")

                    # Section — set dropdown if value matches, else default to first
                    if section in SECTION_OPTIONS:
                        entries[3].set(section)
                    else:
                        entries[3].set("")
                    entries[4].insert(0, str(absences))
                    entries[5].insert(0, str(quizzes) + "%")
                    entries[6].insert(0, str(exam) + "%")
                    entries[7].insert(0, str(activities) + "%")

                except Exception as e:
                    errors.append(f"Row {i+2}: {e}")

            if errors:
                messagebox.showwarning(
                    "Some rows skipped",
                    f"{len(records)} row(s) loaded.\n\nSkipped:\n" + "\n".join(errors)
                )
            else:
                messagebox.showinfo(
                    "Import Successful",
                    f"{len(records)} student(s) imported from file.\n\nClick SAVE & SUBMIT to save to database."
                )

        except Exception as e:
            messagebox.showerror("Import Error", f"Could not read file:\n{e}")

    def save_to_db(self):
        if not self.entry_widgets:
            messagebox.showwarning("No Roster", "Generate a roster first.")
            return

        records       = []
        errors        = []
        local_records = []

        for i, row in enumerate(self.entry_widgets, start=1):
            first      = row[0].get().strip()
            last       = row[1].get().strip()
            subject    = row[2].get().strip()
            section    = row[3].get().strip()
            absences   = row[4].get().strip()
            quizzes    = row[5].get().strip().replace("%", "")
            exam       = row[6].get().strip().replace("%", "")
            activities = row[7].get().strip().replace("%", "")

            # Collect all errors per row (general list, not row-specific)
            row_errors = []
            if not first:    row_errors.append("First name is required")
            if not last:     row_errors.append("Last name is required")
            if first and any(c.isdigit() for c in first):
                row_errors.append("First name must contain letters only")
            if last and any(c.isdigit() for c in last):
                row_errors.append("Last name must contain letters only")
            if not subject:  row_errors.append("Subject is required")
            if not section:  row_errors.append("Section is required")

            abs_val = quiz_val = exam_val = act_val = None

            try:
                abs_val = int(absences) if absences else None
                if abs_val is None: row_errors.append("Absences is required")
                elif abs_val < 0:   row_errors.append("Absences cannot be negative")
            except ValueError:
                row_errors.append("Absences must be a whole number")

            try:
                quiz_val = int(quizzes) if quizzes else None
                if quiz_val is None:           row_errors.append("Quizzes is required")
                elif not (0 <= quiz_val <= 100): row_errors.append("Quizzes must be 0–100")
            except ValueError:
                row_errors.append("Quizzes must be a whole number")

            try:
                exam_val = int(exam) if exam else None
                if exam_val is None:           row_errors.append("Exam is required")
                elif not (0 <= exam_val <= 100): row_errors.append("Exam must be 0–100")
            except ValueError:
                row_errors.append("Exam must be a whole number")

            try:
                act_val = int(activities) if activities else None
                if act_val is None:           row_errors.append("Activities is required")
                elif not (0 <= act_val <= 100): row_errors.append("Activities must be 0–100")
            except ValueError:
                row_errors.append("Activities must be a whole number")

            if row_errors:
                errors.append(f"Row {i}: " + "; ".join(row_errors) + ".")
            else:
                records.append((first, last, abs_val, quiz_val, exam_val, act_val, subject, section, self.uid))
                local_records.append({
                    "first_name": first,
                    "last_name":  last,
                    "subject":    subject,
                    "section":    section,
                    "absences":   abs_val,
                    "quizzes":    quiz_val,
                    "exam":       exam_val,
                    "activities": act_val,
                    "group":      "—",
                    "status":     "—",
                })

        if errors:
            messagebox.showerror("Validation Error", "The rows must be all fill before submitting.")
            return

        def run_save():
            try:
                save_students(records)
                self.student_list.extend(local_records)
                self.root.after(0, lambda: messagebox.showinfo("Saved", f"{len(records)} student(s) saved."))
                self.root.after(0, self.force_clear)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Database Error", str(e)))

        threading.Thread(target=run_save, daemon=True).start()

    def force_clear(self):
        for row in self.entry_widgets:
            for e in row:
                e.delete(0, tk.END)
        self.load_from_db()

    # ── STUDENT RECORD TAB ────────────────────────────────────────────────────
    def build_record_tab(self):
        # Dashboard panel pinned at top (collapsible)
        self.build_dashboard_panel(self.frame_record)

        top = tk.Frame(self.frame_record, bg="#0D1117", pady=10)
        top.pack(fill="x", padx=30)

        tk.Label(top, text="STUDENT RECORD",
                 font=("Poppins", 11, "bold"),
                 bg="#0D1117", fg="white").pack(side="left", padx=6)

        # Search bar
        tk.Label(top, text="🔍",
                 font=("Poppins", 12), bg="#0D1117", fg="#9ca3af").pack(side="left", padx=(20, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_search())
        search_entry = tk.Entry(top, textvariable=self.search_var,
                                font=("Poppins", 10),
                                bg="#1E2433", fg="white", relief="flat",
                                highlightthickness=2,
                                highlightbackground="#374151",
                                highlightcolor="#E8A820",
                                insertbackground="white", width=24)
        search_entry.pack(side="left", padx=(0, 6), ipady=4)
        tk.Label(top, text="Search by name, subject, or section",
                 font=("Poppins", 9), bg="#0D1117", fg="#ffffff").pack(side="left")

        # ── Section filter ────────────────────────────────────────────────────
        self.filter_section_var = tk.StringVar(value="All Sections")
        self._section_menu_btn = tk.Button(
            top, text="⚙ Section: All",
            font=("Poppins", 9, "bold"),
            bg="#1E2433", fg="#38bdf8",
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._open_section_filter
        )
        self._section_menu_btn.pack(side="right", padx=4)

        # ── Subject filter ────────────────────────────────────────────────────
        self.filter_subject_var = tk.StringVar(value="All Subjects")
        self._subject_menu_btn = tk.Button(
            top, text="⚙ Subject: All",
            font=("Poppins", 9, "bold"),
            bg="#1E2433", fg="#fbbf24",
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._open_subject_filter
        )
        self._subject_menu_btn.pack(side="right", padx=4)

        tk.Button(top, text="   REFRESH   ", command=self.load_from_db,
                  bg="#1a1a1a", fg="#E8A820", font=("Poppins", 10, "bold"),
                  relief="flat", padx=10, pady=4).pack(side="right", padx=6)

        # Static column header
        self.rec_header_frame = tk.Frame(self.frame_record, bg="#3A3010")
        self.rec_header_frame.pack(fill="x", padx=30)

        # Scrollable content
        scroll_area = tk.Frame(self.frame_record, bg="#0D1117")
        scroll_area.pack(fill="both", expand=True, padx=30)

        self.rec_canvas = tk.Canvas(scroll_area, bg="#0D1117", highlightthickness=0)
        rec_sb          = ttk.Scrollbar(scroll_area, orient="vertical", command=self.rec_canvas.yview)
        self.rec_canvas.configure(yscrollcommand=rec_sb.set)
        rec_sb.pack(side="right", fill="y")
        self.rec_canvas.pack(side="left", fill="both", expand=True)

        self.rec_rows = tk.Frame(self.rec_canvas, bg="#0D1117")
        rec_cw        = self.rec_canvas.create_window((0, 0), window=self.rec_rows, anchor="nw")
        self.rec_rows.bind("<Configure>", lambda e: self.rec_canvas.configure(
            scrollregion=self.rec_canvas.bbox("all")))
        self.rec_canvas.bind("<Configure>", lambda e: self.rec_canvas.itemconfig(rec_cw, width=e.width))

        def _rec_scroll(event):
            self.rec_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.rec_canvas.bind("<Enter>", lambda e: self.rec_canvas.bind_all("<MouseWheel>", _rec_scroll))
        self.rec_canvas.bind("<Leave>", lambda e: self.rec_canvas.unbind_all("<MouseWheel>"))

        footer_bar = tk.Frame(self.frame_record, bg="#111827", pady=6)
        footer_bar.pack(fill="x")
        tk.Label(footer_bar,
                 text="Laguna State Polytechnic University - San Pablo Campus | BS - Computer Science | OG - 6",
                 font=("Poppins", 10, "bold"), bg="#111827", fg="#9ca3af").pack(side="left", padx=12)
        self.total_label = tk.Label(footer_bar, text="Total: 0 students",
                                    font=("Poppins", 10, "bold"), bg="#111827", fg="#9ca3af")
        self.total_label.pack(side="right", padx=12)

    def apply_search(self):
        query   = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        section = getattr(self, "filter_section_var", None)
        subject = getattr(self, "filter_subject_var", None)
        sec_val = section.get() if section else "All Sections"
        sub_val = subject.get() if subject else "All Subjects"

        result = self.student_list[:]

        if query:
            result = [
                s for s in result
                if query in s.get("first_name", "").lower()
                or query in s.get("last_name",  "").lower()
                or query in s.get("subject",    "").lower()
                or query in s.get("section",    "").lower()
            ]

        if sec_val not in ("All Sections", ""):
            result = [s for s in result if s.get("section", "—") == sec_val]

        if sub_val not in ("All Subjects", ""):
            result = [s for s in result if s.get("subject", "—") == sub_val]

        self._filtered_list = result
        self.render_record_table()

    def _open_section_filter(self):
        sections = ["All Sections"] + sorted(set(
            s.get("section", "—") for s in self.student_list
            if s.get("section", "—") not in ("—", None, "")
        ))
        self._open_filter_popup("Section", sections,
                                self.filter_section_var,
                                self._section_menu_btn,
                                "⚙ Section: ", "#38bdf8")

    def _open_subject_filter(self):
        subjects = ["All Subjects"] + sorted(set(
            s.get("subject", "—") for s in self.student_list
            if s.get("subject", "—") not in ("—", None, "")
        ))
        self._open_filter_popup("Subject", subjects,
                                self.filter_subject_var,
                                self._subject_menu_btn,
                                "⚙ Subject: ", "#fbbf24")

    def _open_filter_popup(self, kind, options, var, btn_ref, label_prefix, color):
        popup = tk.Toplevel(self.root)
        popup.configure(bg="#111827")
        popup.resizable(False, False)
        popup.grab_set()
        popup.overrideredirect(True)

        # Position below the button
        btn_ref.update_idletasks()
        bx = btn_ref.winfo_rootx()
        by = btn_ref.winfo_rooty() + btn_ref.winfo_height() + 4
        popup.geometry(f"+{bx}+{by}")

        tk.Frame(popup, bg="#1A3A5C", height=2).pack(fill="x")
        for opt in options:
            is_selected = var.get() == opt
            btn = tk.Button(
                popup, text=f"  {'✔  ' if is_selected else '     '}{opt}  ",
                font=("Poppins", 10),
                bg="#1E2433" if not is_selected else "#1A3A5C",
                fg=color if is_selected else "#e2e8f0",
                relief="flat", anchor="w",
                cursor="hand2",
                command=lambda o=opt: self._apply_filter(kind, o, var, btn_ref, label_prefix, popup)
            )
            btn.pack(fill="x", padx=2, pady=1)
        tk.Frame(popup, bg="#1A3A5C", height=2).pack(fill="x")

        popup.bind("<FocusOut>", lambda e: popup.destroy())
        popup.focus_set()

    def _apply_filter(self, kind, value, var, btn_ref, label_prefix, popup):
        var.set(value)
        short = value.replace("All Sections", "All").replace("All Subjects", "All")
        btn_ref.config(text=f"{label_prefix}{short}")
        popup.destroy()
        self.apply_search()   # re-run search/filter pipeline

    def show_ml_info(self):
        open_ml_info_popup(self.root, self.ml_stats)

    def open_predict(self):
        if self.knn_model is None:
            messagebox.showwarning("Not ready", "Run clustering first.")
            return

        def on_student_added(student):
            self.student_list.append(student)
            self._filtered_list = self.student_list[:]

        def switch_to_record():
            self.switch_tab("record")

        open_predict_popup(
            self.root,
            self.knn_model,
            self.scaler,
            self.student_list,
            on_student_added,
            switch_to_record
        )

    # ── RENDER RECORD TABLE ───────────────────────────────────────────────────
    def render_record_table(self):
        for w in self.rec_rows.winfo_children():
            w.destroy()
        # Reset header frame height (may have been set to 0 during clustered view)
        self.rec_header_frame.config(height=1)

        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        data  = self._filtered_list

        if not data:
            msg = "No students match your search." if query else "No records yet. Save students or click Refresh."
            tk.Label(self.rec_rows, text=msg,
                     font=("Poppins", 10), bg="#0D1117", fg="#aaa", pady=20).pack()
            self.total_label.config(text="TOTAL: 0 STUDENTS")
            return

        has_clusters = any(s.get("group", "—") not in ("—", None) for s in data)

        col_labels  = ("#", "First Name", "Last Name", "Subject", "Section",
                       "Absences", "Quizzes", "Exam", "Activities", "Status", "")
        col_weights = [3, 9, 9, 8, 6, 5, 5, 5, 6, 5, 3]

        # ── Show global header only when NOT clustered ─────────────────────
        for w in self.rec_header_frame.winfo_children():
            w.destroy()
        if not has_clusters:
            for col, (lbl, wt) in enumerate(zip(col_labels, col_weights)):
                self.rec_header_frame.columnconfigure(col, weight=wt, uniform="col")
                tk.Label(self.rec_header_frame, text=lbl,
                         font=("Poppins", 10, "bold"),
                         bg="#3A3010", fg="#E8A820",
                         anchor="center", pady=8).grid(row=0, column=col, sticky="ew")
        else:
            # Hide the global header strip when clustered
            self.rec_header_frame.config(height=0)

        def make_edit_btn(parent_frame, student_idx, row_bg):
            btn = tk.Button(parent_frame, text="EDIT",
                            font=("Poppins", 10),
                            bg=row_bg, fg="#E8A820",
                            relief="flat", cursor="hand2",
                            command=lambda idx=student_idx: self._edit_student(idx))
            return btn

        if not has_clusters:
            for i, s in enumerate(data, start=1):
                bg     = "#1A222E" if i % 2 == 0 else "#0D1117"
                status = compute_pass_fail(
                    s["absences"], s["quizzes"], s["exam"], s["activities"]
                )
                sfg    = "#4ade80" if status == "PASS" else "#f87171"
                
                values = [
                    str(i), s["first_name"], s["last_name"],
                    s.get("subject", "—"),
                    s.get("section", "—"),
                    str(s["absences"]),
                    str(s["quizzes"]) + "%",
                    str(s["exam"]) + "%",
                    str(s["activities"]) + "%",
                    status
                ]

                row = tk.Frame(self.rec_rows, bg=bg, pady=3)
                row.pack(fill="x")
                tk.Frame(self.rec_rows, bg="#3A3010", height=1).pack(fill="x")

                for col, (val, wt) in enumerate(zip(values, col_weights[:-1])):
                    row.columnconfigure(col, weight=wt, uniform="col")
                    is_status = col == len(values) - 1
                    tk.Label(row, text=val,
                             font=("Poppins", 10, "bold") if is_status else ("Poppins", 10),
                             bg=bg,
                             fg=sfg if is_status else "#ffffff",
                             anchor="center").grid(row=0, column=col, sticky="ew", pady=4)

                row.columnconfigure(len(values), weight=col_weights[-1], uniform="col")
                real_idx = self.student_list.index(s) if s in self.student_list else -1
                make_edit_btn(row, real_idx, bg).grid(row=0, column=len(values), sticky="ew", pady=4)

            self.total_label.config(text=f"TOTAL: {len(data)} STUDENTS")
            return

        # ── Clustered view ────────────────────────────────────────────────────
        group_info = {
            "A": {"name": "High Performers",         "bg": "#0F2D1F", "fg": "#4ade80", "header": "#1A4231"},
            "B": {"name": "Average but Improving",   "bg": "#0A1F2E", "fg": "#38bdf8", "header": "#0F2D40"},
            "C": {"name": "Struggling Students",     "bg": "#2E0F0F", "fg": "#f87171", "header": "#421A1A"},
            "D": {"name": "Inconsistent Performers", "bg": "#2E1F0A", "fg": "#fbbf24", "header": "#42300F"},
        }

        groups = {"A": [], "B": [], "C": [], "D": []}
        for s in data:
            g = s.get("group", "—")
            if g in groups:
                groups[g].append(s)

        for letter, students in groups.items():
            info  = group_info[letter]
            count = len(students)

            grp_hdr = tk.Frame(self.rec_rows, bg=info["header"], pady=6)
            grp_hdr.pack(fill="x", pady=(10, 0))
            tk.Label(grp_hdr,
                     text=f"  Group {letter}  —  {info['name']}  |  {count} student{'s' if count != 1 else ''}",
                     font=("Poppins", 11, "bold"),
                     bg=info["header"], fg=info["fg"]).pack(side="left", padx=10)

            if students:
                pass_count = sum(1 for s in students if s.get("status", "—") == "PASS")
                tk.Label(grp_hdr,
                         text=f" {pass_count} PASS    {count - pass_count} FAIL",
                         font=("Poppins", 9, "bold"),
                         bg=info["header"], fg="#9ca3af").pack(side="right", padx=14)

            # ── Per-group column headers ──────────────────────────────────────
            col_hdr_frame = tk.Frame(self.rec_rows, bg=info["header"], pady=2)
            col_hdr_frame.pack(fill="x")
            for col, (lbl, wt) in enumerate(zip(col_labels, col_weights)):
                col_hdr_frame.columnconfigure(col, weight=wt, uniform="col")
                tk.Label(col_hdr_frame, text=lbl,
                        font=("Poppins", 9, "bold"),
                        bg=info["header"], fg="#9ca3af",
                        anchor="center", pady=4).grid(row=0, column=col, sticky="ew")

            if not students:
                tk.Label(self.rec_rows, text="  No students in this group.",
                         font=("Poppins", 9, "italic"),
                         bg=info["bg"], fg="#aaa", pady=4).pack(fill="x")
            else:
                tk.Frame(self.rec_rows, bg=info["header"], height=1).pack(fill="x")
                
                for i, s in enumerate(students, start=1):
                    row = tk.Frame(self.rec_rows, bg=info["bg"], pady=3)
                    row.pack(fill="x")
                    tk.Frame(self.rec_rows, bg=info["header"], height=1).pack(fill="x")

                    status = s.get("status") or compute_pass_fail(
                        s["absences"], s["quizzes"], s["exam"], s["activities"]
                    )
                    sfg = "#4ade80" if status == "PASS" else "#f87171"
                    
                    values = [
                        str(i), s["first_name"], s["last_name"],
                        s.get("subject", "—"),
                        s.get("section", "—"),
                        str(s["absences"]),
                        str(s["quizzes"]) + "%",
                        str(s["exam"]) + "%",
                        str(s["activities"]) + "%",
                        status
                    ]

                    for col, (val, wt) in enumerate(zip(values, col_weights[:-1])):
                        row.columnconfigure(col, weight=wt, uniform="col")
                        is_status = col == len(values) - 1
                        tk.Label(row, text=val,
                                 font=("Poppins", 10, "bold") if is_status else ("Poppins", 10),
                                 bg=info["bg"],
                                 fg=sfg if is_status else "#e2e8f0",
                                 anchor="center").grid(row=0, column=col, sticky="ew", pady=4)

                    row.columnconfigure(len(values), weight=col_weights[-1], uniform="col")
                    real_idx = self.student_list.index(s) if s in self.student_list else -1
                    make_edit_btn(row, real_idx, info["bg"]).grid(
                        row=0, column=len(values), sticky="ew", pady=4)

            btn_row = tk.Frame(self.rec_rows, bg=info["bg"], pady=8)
            btn_row.pack(fill="x")
            tk.Button(btn_row,
                      text=f"View Recommendations for Group {letter}",
                      font=("Poppins", 10, "bold"),
                      bg=info["header"], fg=info["fg"],
                      relief="flat", padx=40, pady=5,
                      cursor="hand2",
                      command=lambda l=letter: self._open_rec_with_insight(l)
                      ).pack(anchor="center")

        self.total_label.config(text=f"TOTAL: {len(data)} STUDENTS")

    def _edit_student(self, idx):
        if idx < 0 or idx >= len(self.student_list):
            messagebox.showerror("Error", "Student not found.")
            return
        student = self.student_list[idx]

        def on_save(updated):
            self.student_list[idx].update(updated)
            self.render_record_table()
            messagebox.showinfo("Updated", "Student record updated successfully.")

        open_edit_popup(self.root, student, on_save, self.uid)

    # ── RUN ALL THREE ML ALGORITHMS ───────────────────────────────────────────
    def run_clustering(self):
        if not self.student_list:
            messagebox.showwarning("No Data", "Load or save students first.")
            return

        def do_cluster():
            try:
                X = np.array([
                    [float(s["absences"]), float(s["quizzes"]),
                     float(s["exam"]),     float(s["activities"])]
                    for s in self.student_list
                ])

                n_students = len(self.student_list)
                n_clusters = min(4, n_students)

                self.scaler  = StandardScaler()
                X_scaled     = self.scaler.fit_transform(X)

                # ── ALGORITHM 1: K-Means (grouping) ──────────────────────────
                self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                self.kmeans_model.fit(X_scaled)
                km_labels = self.kmeans_model.labels_

                cluster_means = {}
                for idx, label in enumerate(km_labels):
                    cluster_means.setdefault(label, []).append(X[idx].mean())

                ranked    = sorted(cluster_means.keys(),
                                   key=lambda c: np.mean(cluster_means[c]),
                                   reverse=True)
                group_map = {cid: ["A", "B", "C", "D"][rank] for rank, cid in enumerate(ranked)}

                for idx, s in enumerate(self.student_list):
                    s["group"] = group_map[km_labels[idx]]

                # ── ALGORITHM 2: Decision Tree (recommendations) ──────────────
                # Pass/fail is still simple if-else logic; DT identifies
                # which factor most influences each group's outcomes.
                feature_names = ["Absences", "Quizzes", "Exam", "Activities"]
                y_pass = [
                    compute_pass_fail(
                        float(s["absences"]), float(s["quizzes"]),
                        float(s["exam"]),     float(s["activities"])
                    )
                    for s in self.student_list
                ]

                self.dt_model = DecisionTreeClassifier(max_depth=4, random_state=42, criterion="gini")
                self.dt_model.fit(X, y_pass)

                importances = self.dt_model.feature_importances_
                sorted_idx  = np.argsort(importances)[::-1]

                # Apply simple pass/fail logic (not DT)
                for s in self.student_list:
                    s["status"] = compute_pass_fail(
                        s["absences"], s["quizzes"], s["exam"], s["activities"]
                    )

                # DT-based per-group insights for recommendations
                self.dt_insights = {}
                for letter in ["A", "B", "C", "D"]:
                    group_students = [s for s in self.student_list if s.get("group") == letter]
                    if group_students:
                        Xg = np.array([
                            [float(s["absences"]), float(s["quizzes"]),
                             float(s["exam"]),     float(s["activities"])]
                            for s in group_students
                        ])
                        yg = [
                            compute_pass_fail(
                                float(s["absences"]), float(s["quizzes"]),
                                float(s["exam"]),     float(s["activities"])
                            )
                            for s in group_students
                        ]
                        unique_labels = set(yg)
                        if len(unique_labels) > 1 and len(group_students) >= 2:
                            try:
                                dt_g = DecisionTreeClassifier(max_depth=3, random_state=42)
                                dt_g.fit(Xg, yg)
                                imp_g       = dt_g.feature_importances_
                                top_idx     = int(np.argmax(imp_g))
                                top_factor  = feature_names[top_idx]
                                top_pct     = int(round(imp_g[top_idx] * 100))
                                self.dt_insights[letter] = (
                                    f"For Group {letter} students, the Decision Tree identified "
                                    f"'{top_factor}' as the most influential factor "
                                    f"({top_pct}% importance). Focus teaching strategies "
                                    f"on improving this area for maximum impact."
                                )
                            except Exception:
                                self.dt_insights[letter] = None
                        else:
                            self.dt_insights[letter] = (
                                f"All Group {letter} students have the same outcome. "
                                f"Overall, '{feature_names[sorted_idx[0]]}' is the top class-wide factor."
                            )
                    else:
                        self.dt_insights[letter] = None

                pass_count = sum(1 for s in self.student_list if s.get("status") == "PASS")
                fail_count = n_students - pass_count

                # ── ALGORITHM 3: KNN (predicting new students) ────────────────
                y_group      = [s["group"] for s in self.student_list]
                k_neighbors  = min(3, n_students)
                self.knn_model = KNeighborsClassifier(
                    n_neighbors=k_neighbors,
                    metric="euclidean",
                    weights="distance"
                )
                self.knn_model.fit(X_scaled, y_group)

                # ── Stats for analysis popup ──────────────────────────────────
                group_counts = {}
                for s in self.student_list:
                    g = s.get("group", "—")
                    group_counts[g] = group_counts.get(g, 0) + 1

                group_summary = "  |  ".join(
                    f"Group {g}: {group_counts.get(g, 0)}" for g in ["A", "B", "C", "D"]
                )
                imp_readable = "  |  ".join(
                    f"{feature_names[i]}: {int(round(importances[i] * 100))}%"
                    for i in sorted_idx
                )

                self.ml_stats = {
                    "kmeans": {
                        "Total students analyzed": n_students,
                        "Number of groups formed": n_clusters,
                        "Students per group":      group_summary,
                    },
                    "dtree": {
                        "Purpose":                       "Identifies which factor most needs attention per group",
                        "Students in analysis":          n_students,
                        "Most influential factor":       feature_names[sorted_idx[0]],
                        "Second most influential factor":feature_names[sorted_idx[1]],
                        "Influence of each factor":      imp_readable,
                        "Where results appear":          "In each group's Teaching Recommendations popup",
                    },
                    "knn": {
                        "How new students are matched":  f"Compared to the {k_neighbors} most similar existing students",
                        "What is being compared":        "Quiz scores, exam scores, activities, and absences",
                        "Closer matches matter more":    "Yes — students with very similar scores have more influence",
                        "Predicted student added to":    "Student Record tab (after clicking ADD TO RECORD)",
                        "Ready to predict new students": "Yes — use PREDICT NEW in the dashboard panel",
                    },
                }

                self.root.after(0, self.render_record_table)
                self.root.after(0, self.refresh_dashboard)
                self.root.after(0, lambda: self.switch_tab("record"))
                self.root.after(0, self._collapse_dashboard)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Analysis Complete",
                    f"{n_students} students analyzed and grouped.\n"
                    f"{pass_count} PASS  •  {fail_count} FAIL\n\n"
                    f"Use PREDICT NEW to add a new student,\n"
                    f"or VIEW ANALYSIS for detailed insights."
                ))

            except Exception as e:
                err = str(e)
                self.root.after(0, lambda msg=err: messagebox.showerror("Clustering Error", msg))

        threading.Thread(target=do_cluster, daemon=True).start()

    # ── LOAD FROM DATABASE ────────────────────────────────────────────────────
    def load_from_db(self):
        def run():
            try:
                rows = get_all_students(self.uid)
                self.student_list = [{
                    "first_name": row[0],
                    "last_name":  row[1],
                    "absences":   row[2],
                    "quizzes":    row[3],
                    "exam":       row[4],
                    "activities": row[5],
                    "subject":    row[6] if len(row) > 6 else "—",
                    "section":    row[7] if len(row) > 7 else "—",
                    "group":      "—",
                    "status":     "—",
                } for row in rows]
                self._filtered_list = self.student_list[:]
                self.root.after(0, self.apply_search)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("DB Error", str(e)))

        threading.Thread(target=run, daemon=True).start()


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1350x730")
    root.state("zoomed")
    app = StudentClassifier(root)
    root.mainloop()