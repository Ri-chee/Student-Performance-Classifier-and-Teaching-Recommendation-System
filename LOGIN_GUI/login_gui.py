import tkinter as tk
from tkinter import *
import os
import subprocess
import mysql.connector
from tkinter import messagebox
import hashlib
import mysql.connector
import json
from mysql.connector import Error
from PIL import Image, ImageTk
import random
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Shared validator: block digits in name/text fields ───────────────────────
def _make_no_digit_vcmd(widget):
    def _no_digits(new_val):
        return not any(c.isdigit() for c in new_val)
    return (widget.register(_no_digits), '%P')

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",
    "database": "spcatrs"
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        messagebox.showinfo(f"[DB ERROR] {e}")
    return None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# Colors
color1 = "grey"
color2 = "#161616"
color3 = "white"

master = Tk()

master.minsize(1350, 730)
master.state("zoomed")
master.title("STUDENT PERFORMANCE CLASSIFIER AND TEACHING RECOMMENDATION SYSTEM")

# Load Icons
login_button = PhotoImage(file=asset("gradient_icons/login.png"))

# Background Images
bkg_image     = Image.open(asset("images/LOGIN (1536 x 864 px).png"))
login_image   = Image.open(asset("images/LOGIN (1536 x 864 px).png"))
signup_button = PhotoImage(file=asset("gradient_icons/signup.png"))
bkg_image = bkg_image.resize((master.winfo_screenwidth(), master.winfo_screenheight()))

bg_photo = ImageTk.PhotoImage(bkg_image)
buttonappearlogin_default  = PhotoImage(file=asset("images/LoginDef.png"))
buttonappearlogin_active   = PhotoImage(file=asset("images/LoginAct.png"))
buttonappearsignup_default = PhotoImage(file=asset("images/SignDef.png"))
buttonappearsignup_active  = PhotoImage(file=asset("images/SignAct.png"))

main_bg  = Label(master, image=bg_photo)
main_bg.pack()

login_bg = Label(main_bg, image=bg_photo, bd=0)
login_bg.place(x=0, y=0)

# ── LOGIN FRAME ──────────────────────────────────────────────────────────────
login_frame = Frame(login_bg, bg=color2, height=540, width=420)

isLoginShown = False
isSignShown = False

def falseSign():
    global isSignShown
    isSignShown = False

def falseLogin():
    global isLoginShown
    isLoginShown = False

def trueLogin():
    global isLoginShown
    isLoginShown = True

def trueSign():
    global isSignShown
    isSignShown = True

def show_login():
    if isLoginShown == False:
        main_bg.config(image=bg_photo)
        main_bg.image = bg_photo
        login_bg.config(image=bg_photo)
        login_bg.image = bg_photo

        login_frame.place(x=987, y=175)
        signup_frame.place_forget()
        show_signup_btn.place_forget()
        show_signup_btn.place(x=520, y=498)
        show_login_btn.place(x=119, y=498)
        show_login_btn.config(image=buttonappearlogin_active)
        show_signup_btn.config(image=buttonappearsignup_default)
        falseSign()
        trueLogin()
        _clear_signup_fields()
    else:
        return

def _clear_signup_fields():
    """Clear and reset all signup form fields."""
    try:
        for field in [fname_entry, lname_entry, mname_entry,
                      email1_entry, reg_email_entry,
                      pass_entry1, confirm_entry]:
            field.delete(0, END)
        ext_var.set("None")
        match_hint.config(text="")
        # Hide OTP field and reset button position if visible
        otp_label.place_forget()
        otp_entry.place_forget()
        otp_entry.delete(0, END)
        signup_btn.place(relx=0.5, anchor="n", y=470)
        # Reset password visibility to hidden
        pass_entry1.config(show="*")
        confirm_entry.config(show="*")
        show_label1.config(text="Show Password")
        # Reset OTP state
        global current_otp, pending_username
        current_otp = ""
        pending_username = ""
    except NameError:
        # Fields not yet created (first call before signup frame built)
        pass

show_login_btn = Button(
    main_bg,
    bd=0,
    highlightthickness=0,
    activebackground="black",
    bg="black",
    image=buttonappearlogin_default,
    command=show_login
)
show_login_btn.place(x=119, y=498)

def show_sign():
    if isSignShown == False:
        blur_image = Image.open(asset("images/blur2.png"))
        blur_image = blur_image.resize((master.winfo_screenwidth(), master.winfo_screenheight()))
        blur_photo = ImageTk.PhotoImage(blur_image)
        main_bg.config(image=blur_photo)
        main_bg.image = blur_photo
        login_bg.config(image=blur_photo)
        login_bg.image = blur_photo

        signup_frame.place(x=320, y=150)
        login_frame.place_forget()
        show_login_btn.place_forget()
        show_signup_btn.config(image=buttonappearsignup_active)
        show_login_btn.config(image=buttonappearlogin_default)
        trueSign()
        falseLogin()
    else:
        return

show_signup_btn = Button(
    main_bg,
    bg="black",
    activebackground="black",
    image=buttonappearsignup_default,
    bd=0,
    highlightthickness=0,
    command=show_sign,
)
show_signup_btn.place(x=520, y=498)

# ── LOGIN FRAME WIDGETS ───────────────────────────────────────────────────────
login_info = Label(login_frame, text="LOGIN ACCOUNT", fg="#e6b024", bg=color2, font=("Poppins", 20))
login_info.place(relx=0.5, anchor="n", y=30)

# ── LOGIN MODE TOGGLE (Username / Google) — CENTERED ─────────────────────────
login_mode = StringVar(value="username")

# Centered toggle container
toggle_outer = Frame(login_frame, bg=color2)
toggle_outer.place(relx=0.5, anchor="n", y=80)

toggle_frame = Frame(toggle_outer, bg="#2a2a2a", bd=0, highlightthickness=0)
toggle_frame.pack()

def set_login_mode(mode):
    login_mode.set(mode)
    if mode == "username":
        btn_username.config(bg="#e6b024", fg="#161616")
        btn_google.config(bg="#2a2a2a", fg="#888888")
        username_section_frame.place(relx=0.5, anchor="n", y=150)
        google_section_frame.place_forget()
    else:
        btn_google.config(bg="#e6b024", fg="#161616")
        btn_username.config(bg="#2a2a2a", fg="#888888")
        google_section_frame.place(relx=0.5, anchor="n", y=150)
        username_section_frame.place_forget()

btn_username = Button(toggle_frame, text="Username", bg="#e6b024", fg="#161616",
                      font=("Poppins", 10, "bold"), bd=0, relief="flat",
                      width=14, pady=8, cursor="hand2",
                      command=lambda: set_login_mode("username"))
btn_username.pack(side=LEFT)

btn_google = Button(toggle_frame, text="Google Account", bg="#2a2a2a", fg="#888888",
                    font=("Poppins", 10, "bold"), bd=0, relief="flat",
                    width=14, pady=8, cursor="hand2",
                    command=lambda: set_login_mode("google"))
btn_google.pack(side=LEFT)

# ── USERNAME/PASSWORD SECTION ─────────────────────────────────────────────────
username_section_frame = Frame(login_frame, bg=color2)
username_section_frame.place(relx=0.5, anchor="n", y=150)

email_label = Label(username_section_frame, text="Username or Email", fg="#e6b024", bg=color2, font=("Poppins", 12))
email_label.pack(anchor="w")
email_entry = Entry(username_section_frame, relief="flat", width=40, fg=color2, font=("Poppins", 10, "bold"))
email_entry.pack(anchor="w", pady=(2, 8))
Frame(username_section_frame, height=2, width=304, bg="#333").pack(anchor="w")

pass_label = Label(username_section_frame, text="Password", fg="#e6b024", bg=color2, font=("Poppins", 12))
pass_label.pack(anchor="w", pady=(10, 0))
pass_entry = Entry(username_section_frame, relief="flat", width=40, fg=color2, font=("Poppins", 10, "bold"), show="•")
pass_entry.pack(anchor="w", pady=(2, 4))
Frame(username_section_frame, height=2, width=304, bg="#333").pack(anchor="w")

toggle_row = Frame(username_section_frame, bg=color2)
toggle_row.pack(anchor="w", pady=(6, 0))

rem_label = Label(toggle_row, bg=color2, fg="#e6b024", text="Show Password", font=("Poppins", 10))
rem_label.pack(side=RIGHT)

def toggle_password():
    if pass_entry.cget('show') == '':
        pass_entry.config(show='•')
        rem_label.config(text="Show Password")
    else:
        pass_entry.config(show='')
        rem_label.config(text="Hide Password")

rem_box = Checkbutton(toggle_row, bg=color2, state="normal", relief="flat", command=toggle_password)
rem_box.pack(side=RIGHT)

# ── GOOGLE SECTION ────────────────────────────────────────────────────────────
google_section_frame = Frame(login_frame, bg=color2)

Label(google_section_frame, text="Sign in with your Google account.",
      fg="#888888", bg=color2, font=("Poppins", 10)).pack(pady=(10, 16), anchor="center")

def google_login():
    try:
        import google_auth_oauthlib.flow
        import googleapiclient.discovery

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            asset("client_secret.json"),
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ]
        )
        creds = flow.run_local_server(port=0)

        import google.oauth2.credentials
        import googleapiclient.discovery
        service = googleapiclient.discovery.build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()

        google_email = user_info.get("email", "")
        google_name  = user_info.get("name", "")

        # Check if this Google email is registered
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM logincredentials WHERE Email = %s", (google_email,))
                user = cursor.fetchone()
            finally:
                cursor.close()
                conn.close()

            if user:
                messagebox.showinfo("Login Successful", f"Welcome, {user['Username'].capitalize()}!")
                open_homepage(user['UID'])
            else:
                messagebox.showerror("Not Registered",
                    f"No account found for {google_email}.\nPlease sign up first using this Google email.")
        else:
            messagebox.showerror("Connection Error", "Could not connect to the database.")

    except ImportError:
        messagebox.showerror("Missing Library",
            "Google Auth library is not installed.\n\nRun:\n  pip install google-auth-oauthlib google-api-python-client")
    except FileNotFoundError:
        messagebox.showerror("Missing File",
            "client_secret.json not found.\nPlease place your Google OAuth credentials file in the app directory.")
    except Exception as e:
        messagebox.showerror("Google Login Error", f"An error occurred:\n{e}")

google_btn_frame = Frame(google_section_frame, bg="white", bd=1, relief="solid")
google_btn_frame.pack(pady=4, anchor="center")
Button(google_btn_frame, text="  Sign in with Google  ",
       bg="white", fg="#444444",
       font=("Poppins", 10), bd=0, relief="flat",
       activebackground="#f5f5f5",
       cursor="hand2", padx=10, pady=8,
       command=google_login).pack()

# ── HOMEPAGE / AUTH HELPERS ───────────────────────────────────────────────────
def open_homepage(uid):
    with open("session.json", "w") as f:
        json.dump({"UID": uid}, f)
    master.withdraw()
    proc = subprocess.Popen(["python", asset("StudentClassifier.py")])
    proc.wait()
    master.deiconify()

def verify_login(username, password):
    conn = get_connection()
    if conn is None:
        messagebox.showerror("Connection Error", "Could not connect to the database.")
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM logincredentials WHERE (Username = %s OR Email = %s) AND Password = %s",
            (username, username, password)
        )
        return cursor.fetchone()
    except Exception as e:
        messagebox.showerror("Auth Error", f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def login():
    if login_mode.get() == "google":
        google_login()
        return
    username = email_entry.get().strip()
    password = pass_entry.get().strip()
    if username == "" or password == "":
        messagebox.showwarning("Missing Fields", "Please enter credentials.")
        return
    user = verify_login(username, password)
    if user:
        messagebox.showinfo("Login Successful", f"Welcome, {user['Username'].capitalize()}!")
        email_entry.delete(0, END)
        pass_entry.delete(0, END)
        open_homepage(user['UID'])
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")
        pass_entry.delete(0, END)

login_btn = Button(login_frame, fg="#e6b024", bg=color2, image=login_button,
                   bd=0, relief="flat", highlightthickness=0,
                   activebackground="black", command=login)
login_btn.place(relx=0.5, anchor="n", y=390)

forgot_btn = Button(login_frame, text="Forgot Password?", bg=color2,
                    fg="#888888", font=("Poppins", 9), bd=0, relief="flat",
                    activebackground=color2, activeforeground="#e6b024",
                    cursor="hand2", command=lambda: show_forgot_password())
forgot_btn.place(relx=0.5, anchor="n", y=450)

# Bind Enter key to login
email_entry.bind("<Return>", lambda e: login())
pass_entry.bind("<Return>",  lambda e: login())

# ── FORGOT PASSWORD ──────────────────────────────────────────────────────────
def show_forgot_password():
    blur_image = Image.open(asset("images/blur2.png"))
    blur_image = blur_image.resize((master.winfo_screenwidth(), master.winfo_screenheight()))
    blur_photo = ImageTk.PhotoImage(blur_image)
    main_bg.config(image=blur_photo)
    main_bg.image = blur_photo
    login_bg.config(image=blur_photo)
    login_bg.image = blur_photo

    login_frame.place_forget()
    show_login_btn.place_forget()
    show_signup_btn.place_forget()

    forgot_frame = Frame(main_bg, bg="#0D1117", height=600, width=700)
    forgot_frame.place(relx=0.5, rely=0.5, anchor="center")

    fp_header = Frame(forgot_frame, bg="#111827", height=95, width=700)
    fp_header.place(x=0, y=0)
    fp_header.pack_propagate(False)

    Button(forgot_frame, text="← Back", bg="#111827", fg="#888888",
           font=("Poppins", 9), bd=0, relief="flat",
           activebackground="#111827", activeforeground="#e6b024",
           cursor="hand2",
           command=lambda: _close_forgot(forgot_frame)).place(x=10, y=10)

    Label(forgot_frame, text="FORGOT PASSWORD",
          bg="#111827", fg="#e6b024",
          font=("Poppins", 22, "bold")).place(relx=0.5, anchor="n", x=0, y=20)
    Label(forgot_frame, text="Verify your identity to recover your password.",
          bg="#111827", fg="#888888",
          font=("Poppins", 10)).place(relx=0.5, anchor="n", x=0, y=58)

    # ── STEP 1: VERIFY IDENTITY (now includes Email field) ───────────────
    step1_frame = Frame(forgot_frame, bg="#0D1117", width=700, height=500)
    step1_frame.place(x=0, y=100)

    Label(step1_frame, text="── STEP 1: VERIFY IDENTITY ──",
          bg="#0D1117", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=15)

    # Row 1: First Name + Middle Name
    Label(step1_frame, text="First Name *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=-130, y=55)
    fp_fname = Entry(step1_frame, relief="flat", width=22,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
    fp_fname.place(relx=0.5, anchor="n", x=-130, y=78)

    Label(step1_frame, text="Middle Name", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=130, y=55)
    fp_mname = Entry(step1_frame, relief="flat", width=22,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
    fp_mname.place(relx=0.5, anchor="n", x=130, y=78)

    # Row 2: Last Name + Username
    Label(step1_frame, text="Last Name *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=-130, y=118)
    fp_lname = Entry(step1_frame, relief="flat", width=22,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
    fp_lname.place(relx=0.5, anchor="n", x=-130, y=141)

    Label(step1_frame, text="Username *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=130, y=118)
    fp_uname = Entry(step1_frame, relief="flat", width=22,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
    fp_uname.place(relx=0.5, anchor="n", x=130, y=141)

    # Row 3: Email Address (full width, centered) — used for OTP
    Label(step1_frame, text="Email Address * (used to send OTP)", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=0, y=181)
    fp_email = Entry(step1_frame, relief="flat", width=48,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
    fp_email.place(relx=0.5, anchor="n", x=0, y=204)

    step1_hint = Label(step1_frame, text="", bg="#0D1117", font=("Poppins", 9))
    step1_hint.place(relx=0.5, anchor="n", x=0, y=234)

    # ── STEP 1B: CHOOSE RECOVERY METHOD ──────────────────────────────────
    method_frame = Frame(forgot_frame, bg="#0D1117", width=700, height=500)

    Label(method_frame, text="── STEP 2: CHOOSE RECOVERY METHOD ──",
          bg="#0D1117", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=15)
    Label(method_frame, text="How would you like to reset your password?",
          bg="#0D1117", fg="#e6b024",
          font=("Poppins", 11)).place(relx=0.5, anchor="n", x=0, y=55)

    verified_user = [None]
    verified_email = [""]
    fp_current_otp = [""]

    # ── STEP: OTP FRAME ───────────────────────────────────────────────────
    otp_reset_frame = Frame(forgot_frame, bg="#0D1117", width=700, height=500)

    Label(otp_reset_frame, text="── OTP VERIFICATION ──",
          bg="#0D1117", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=15)
    Label(otp_reset_frame, text="OTP Verification Code *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=0, y=55)
    fp_otp_entry = Entry(otp_reset_frame, relief="flat", width=30,
                         fg="#0D1117", font=("Poppins", 10, "bold"), justify="center")
    fp_otp_entry.place(relx=0.5, anchor="n", x=0, y=80)

    Label(otp_reset_frame, text="New Password *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=0, y=125)
    fp_new_pass_otp = Entry(otp_reset_frame, relief="flat", width=30,
                            fg="#0D1117", font=("Poppins", 10, "bold"), show="*")
    fp_new_pass_otp.place(relx=0.5, anchor="n", x=0, y=148)

    Label(otp_reset_frame, text="Confirm New Password *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(relx=0.5, anchor="n", x=0, y=193)
    fp_conf_pass_otp = Entry(otp_reset_frame, relief="flat", width=30,
                             fg="#0D1117", font=("Poppins", 10, "bold"), show="*")
    fp_conf_pass_otp.place(relx=0.5, anchor="n", x=0, y=216)

    otp_hint = Label(otp_reset_frame, text="", bg="#0D1117", font=("Poppins", 9))
    otp_hint.place(relx=0.5, anchor="n", x=0, y=258)

    # ── STEP: SECURITY QUESTIONS FRAME ───────────────────────────────────
    sq_reset_frame = Frame(forgot_frame, bg="#0D1117", width=700, height=500)

    questions = [
        "What is the name of your first pet?",
        "What is your mother's maiden name?",
        "What was the name of your elementary school?"
    ]
    sq_entries = []
    sy = 20
    Label(sq_reset_frame, text="── STEP 2: SECURITY QUESTIONS ──",
          bg="#0D1117", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=sy)
    sy += 35
    for i, q in enumerate(questions):
        Label(sq_reset_frame, text=f"Q{i+1}: {q}", bg="#0D1117",
              fg="#e6b024", font=("Poppins", 9)).place(x=60, y=sy)
        sy += 25
        e = Entry(sq_reset_frame, relief="flat", width=60,
                  fg="#0D1117", font=("Poppins", 10, "bold"))
        e.place(x=60, y=sy)
        sq_entries.append(e)
        sy += 40

    Label(sq_reset_frame, text="New Password *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(x=60, y=sy + 10)
    fp_new_pass_sq = Entry(sq_reset_frame, relief="flat", width=28,
                           fg="#0D1117", font=("Poppins", 10, "bold"), show="*")
    fp_new_pass_sq.place(x=60, y=sy + 33)

    Label(sq_reset_frame, text="Confirm New Password *", bg="#0D1117",
          fg="#e6b024", font=("Poppins", 10)).place(x=370, y=sy + 10)
    fp_conf_pass_sq = Entry(sq_reset_frame, relief="flat", width=28,
                            fg="#0D1117", font=("Poppins", 10, "bold"), show="*")
    fp_conf_pass_sq.place(x=370, y=sy + 33)

    sq_hint = Label(sq_reset_frame, text="", bg="#0D1117", font=("Poppins", 9))
    sq_hint.place(x=60, y=sy + 60)

    # ── SHARED RESET HELPER ───────────────────────────────────────────────
    def do_db_reset(new_p, hint_label):
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE logincredentials SET Password = %s WHERE Username = %s",
                               (new_p, verified_user[0]['Username']))
                conn.commit()
            except Exception as ex:
                hint_label.config(text=f"✗ Error: {ex}", fg="#e24b4a")
                return False
            finally:
                cursor.close()
                conn.close()
        messagebox.showinfo("Success", "Password reset successfully! You can now log in.")
        _close_forgot(forgot_frame)
        return True

    # ── PERFORM OTP RESET ─────────────────────────────────────────────────
    def perform_otp_reset():
        otp   = fp_otp_entry.get().strip()
        new_p = fp_new_pass_otp.get().strip()
        conf  = fp_conf_pass_otp.get().strip()
        if not otp or not new_p or not conf:
            otp_hint.config(text="✗ Please fill all fields.", fg="#e24b4a"); return
        if otp != fp_current_otp[0]:
            otp_hint.config(text="✗ Invalid OTP.", fg="#e24b4a"); return
        if new_p != conf:
            otp_hint.config(text="✗ Passwords do not match.", fg="#e24b4a"); return
        if len(new_p) < 6:
            otp_hint.config(text="✗ Password must be at least 6 characters.", fg="#e24b4a"); return
        do_db_reset(new_p, otp_hint)

    # ── PERFORM SECURITY-Q RESET ──────────────────────────────────────────
    def perform_sq_reset():
        if verified_user[0] is None:
            return
        answers = [e.get().strip() for e in sq_entries]
        if any(a == "" for a in answers):
            sq_hint.config(text="✗ Please answer all questions.", fg="#e24b4a"); return
        new_p = fp_new_pass_sq.get().strip()
        conf  = fp_conf_pass_sq.get().strip()
        if not new_p or not conf:
            sq_hint.config(text="✗ Please fill in new password fields.", fg="#e24b4a"); return
        if new_p != conf:
            sq_hint.config(text="✗ Passwords do not match.", fg="#e24b4a"); return
        if len(new_p) < 6:
            sq_hint.config(text="✗ Password must be at least 6 characters.", fg="#e24b4a"); return

        user = verified_user[0]
        if (answers[0].lower() == str(user.get('SecurityQ1', '')).lower() and
            answers[1].lower() == str(user.get('SecurityQ2', '')).lower() and
            answers[2].lower() == str(user.get('SecurityQ3', '')).lower()):
            do_db_reset(new_p, sq_hint)
        else:
            sq_hint.config(text="✗ Incorrect answers. Try again.", fg="#e24b4a")

    # ── VERIFY IDENTITY ───────────────────────────────────────────────────
    def verify_identity():
        fname  = fp_fname.get().strip()
        lname  = fp_lname.get().strip()
        uname  = fp_uname.get().strip()
        email  = fp_email.get().strip()
        if not fname or not lname or not uname:
            step1_hint.config(text="✗ Please fill all required fields.", fg="#e24b4a"); return
        if not email:
            step1_hint.config(text="✗ Email address is required.", fg="#e24b4a"); return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            step1_hint.config(text="✗ Please enter a valid email address.", fg="#e24b4a"); return

        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM logincredentials
                    WHERE Username = %s AND FirstName = %s AND LastName = %s
                """, (uname, fname, lname))
                user = cursor.fetchone()
            finally:
                cursor.close()
                conn.close()
            if user:
                # Verify that the provided email matches the registered email
                if user.get('Email', '').lower() != email.lower():
                    step1_hint.config(text="✗ Email does not match our records.", fg="#e24b4a")
                    return
                verified_user[0]  = user
                verified_email[0] = email
                step1_frame.place_forget()
                method_frame.place(x=0, y=100)
                next_btn.place_forget()
                choose_otp_btn.place(relx=0.5, anchor="n", x=-120, y=420)
                choose_sq_btn.place(relx=0.5, anchor="n", x=120, y=420)
            else:
                step1_hint.config(text="✗ No matching account found.", fg="#e24b4a")

    # ── CHOOSE OTP METHOD ─────────────────────────────────────────────────
    def choose_otp():
        if verified_user[0] is None:
            return
        email = verified_email[0]
        new_otp = str(random.randint(100000, 999999))
        success, msg = send_otp_email(email, new_otp)
        if success:
            messagebox.showinfo("OTP Sent", f"An OTP has been sent to {email}.")
            fp_current_otp[0] = new_otp
            method_frame.place_forget()
            choose_otp_btn.place_forget()
            choose_sq_btn.place_forget()
            otp_reset_frame.place(x=0, y=100)
            otp_reset_btn.place(relx=0.5, anchor="n", x=0, y=440)
        else:
            messagebox.showerror("Email Error", f"Failed to send OTP:\n{msg}")

    # ── CHOOSE SECURITY QUESTIONS METHOD ─────────────────────────────────
    def choose_sq():
        method_frame.place_forget()
        choose_otp_btn.place_forget()
        choose_sq_btn.place_forget()
        sq_reset_frame.place(x=0, y=100)
        sq_reset_btn.place(relx=0.5, anchor="n", x=0, y=440)

    # ── BUTTONS ───────────────────────────────────────────────────────────
    next_btn = Button(forgot_frame, text="  NEXT →  ",
                      bg="#e6b024", fg="#0D1117",
                      font=("Poppins", 11, "bold"), bd=0, relief="flat",
                      cursor="hand2", padx=40, pady=10,
                      command=verify_identity)
    next_btn.place(relx=0.5, anchor="n", x=0, y=460)

    choose_otp_btn = Button(forgot_frame, text="  📧  Send OTP to Email  ",
                            bg="#e6b024", fg="#0D1117",
                            font=("Poppins", 10, "bold"), bd=0, relief="flat",
                            cursor="hand2", padx=20, pady=10,
                            command=choose_otp)

    choose_sq_btn = Button(forgot_frame, text="  🔒  Answer Security Questions  ",
                           bg="#333333", fg="#e6b024",
                           font=("Poppins", 10, "bold"), bd=0, relief="flat",
                           cursor="hand2", padx=20, pady=10,
                           command=choose_sq)

    otp_reset_btn = Button(forgot_frame, text="  RESET PASSWORD  ",
                           bg="#e6b024", fg="#0D1117",
                           font=("Poppins", 11, "bold"), bd=0, relief="flat",
                           cursor="hand2", padx=25, pady=10,
                           command=perform_otp_reset)

    sq_reset_btn = Button(forgot_frame, text="  RESET PASSWORD  ",
                          bg="#e6b024", fg="#0D1117",
                          font=("Poppins", 11, "bold"), bd=0, relief="flat",
                          cursor="hand2", padx=25, pady=10,
                          command=perform_sq_reset)

    # ── ENTER KEY BINDINGS FOR FORGOT PASSWORD ────────────────────────────
    fp_fname.bind("<Return>",        lambda e: verify_identity())
    fp_lname.bind("<Return>",        lambda e: verify_identity())
    fp_uname.bind("<Return>",        lambda e: verify_identity())
    fp_email.bind("<Return>",        lambda e: verify_identity())
    fp_otp_entry.bind("<Return>",    lambda e: perform_otp_reset())
    fp_new_pass_otp.bind("<Return>", lambda e: perform_otp_reset())
    fp_conf_pass_otp.bind("<Return>", lambda e: perform_otp_reset())
    fp_new_pass_sq.bind("<Return>",  lambda e: perform_sq_reset())
    fp_conf_pass_sq.bind("<Return>", lambda e: perform_sq_reset())
    for eq in sq_entries:
        eq.bind("<Return>", lambda e: perform_sq_reset())


def _close_forgot(forgot_frame):
    forgot_frame.destroy()
    main_bg.config(image=bg_photo)
    main_bg.image = bg_photo
    login_bg.config(image=bg_photo)
    login_bg.image = bg_photo
    login_frame.place(x=987, y=175)
    show_login_btn.place(x=119, y=498)
    show_signup_btn.place(x=520, y=498)
    show_login_btn.config(image=buttonappearlogin_active)
    show_signup_btn.config(image=buttonappearsignup_default)
    global isLoginShown, isSignShown
    isLoginShown = True
    isSignShown = False


# ── SIGN UP FRAME ─────────────────────────────────────────────────────────────
def register_user(username, email, password, first_name, last_name, middle_name, ext_name):
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO logincredentials
               (Username, Email, Password, FirstName, LastName, MiddleName, ExtName)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (username, email, password, first_name, last_name, middle_name, ext_name)
        )
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Register Error", f"{e}")
        return False
    finally:
        cursor.close()
        conn.close()

signup_frame = Frame(main_bg, bg="#0D1117", height=560, width=900)

header_bar = Frame(signup_frame, bg="#111827", height=95, width=900)
header_bar.place(x=0, y=0)

back_btn = Button(signup_frame, text="← Back", bg="#111827", fg="#888888",
                  font=("Poppins", 9), bd=0, relief="flat",
                  activebackground="#111827", activeforeground="#e6b024",
                  cursor="hand2", command=show_login)
back_btn.place(x=10, y=10)

signup_title = Label(signup_frame, text="CREATE ACCOUNT",
                     bg="#111827", fg="#e6b024",
                     font=("Poppins", 22, "bold"))
signup_title.place(x=320, y=25)

signup_subtitle = Label(signup_frame, text="Student Performance Classifier & Teaching Recommendation System",
                        bg="#111827", fg="#888888",
                        font=("Poppins", 10))
signup_subtitle.place(x=260, y=60)

personal_label = Label(signup_frame, text="──────────────────────────── PERSONAL INFORMATION ────────────────────────────",
                       bg="#0D1117", fg="#888888",
                       font=("Poppins", 9))
personal_label.place(x=113, y=110)

Label(signup_frame, text="First Name *", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 10)).place(x=100, y=140)
_fname_vcmd = _make_no_digit_vcmd(signup_frame)
fname_entry = Entry(signup_frame, relief="flat", width=25,
                    fg="#111827", font=("Poppins", 10, "bold"),
                    validate="key", validatecommand=_fname_vcmd)
fname_entry.place(x=100, y=165)

Label(signup_frame, text="Middle Name", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 10)).place(x=350, y=140)
_mname_vcmd = _make_no_digit_vcmd(signup_frame)
mname_entry = Entry(signup_frame, relief="flat", width=25,
                    fg="#111827", font=("Poppins", 10, "bold"),
                    validate="key", validatecommand=_mname_vcmd)
mname_entry.place(x=350, y=165)

Label(signup_frame, text="Last Name *", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 10)).place(x=610, y=140)
_lname_vcmd = _make_no_digit_vcmd(signup_frame)
lname_entry = Entry(signup_frame, relief="flat", width=25,
                    fg="#111827", font=("Poppins", 10, "bold"),
                    validate="key", validatecommand=_lname_vcmd)
lname_entry.place(x=610, y=165)

Label(signup_frame, text="Extension", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 10)).place(x=100, y=205)
ext_var = StringVar(signup_frame)
ext_var.set("None")
ext_options = ["None", "Jr.", "Sr.", "II", "III", "IV"]
ext_menu = OptionMenu(signup_frame, ext_var, *ext_options)
ext_menu.config(bg="#0D1117", fg="#e6b024", activebackground="#374151",
                activeforeground="#e6b024", relief="flat",
                font=("Poppins", 9), width=8, bd=0)
ext_menu.place(x=180, y=200)

rule_label = Label(signup_frame, text="This system is exclusively for authorized teaching personnel only.", bg="#0D1117",
                   fg="#e6b024", font=("Poppins", 10))
rule_label.place(x=370, y=195)
rule1_label = Label(signup_frame, text="Please register using your official credentials.", bg="#0D1117",
                    fg="#e6b024", font=("Poppins", 10))
rule1_label.place(x=423, y=215)

creds_label = Label(signup_frame, text="──────────────────────────── ACCOUNT CREDENTIALS ────────────────────────────",
                    bg="#0D1117", fg="#888",
                    font=("Poppins", 9))
creds_label.place(x=113, y=248)

Label(signup_frame, text="Username *", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 11)).place(x=100, y=278)
email1_entry = Entry(signup_frame, relief="flat", width=28,
                     fg="#0D1117", font=("Poppins", 10, "bold"))
email1_entry.place(x=100, y=303)

Label(signup_frame, text="Email Address *", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 11)).place(x=490, y=278)
reg_email_entry = Entry(signup_frame, relief="flat", width=28,
                        fg="#0D1117", font=("Poppins", 10, "bold"))
reg_email_entry.place(x=490, y=303)

Label(signup_frame, text="Password *", bg="#0D1117",
      fg="#e6b024", font=("Poppins", 11)).place(x=100, y=338)
pass_entry1 = Entry(signup_frame, relief="flat", width=28,
                    fg="#111827", font=("Poppins", 10, "bold"), show="*")
pass_entry1.place(x=100, y=363)

Label(signup_frame, text="Confirm Password *",
      bg="#0D1117", fg="#e6b024", font=("Poppins", 11)).place(x=490, y=338)
confirm_entry = Entry(signup_frame, relief="flat", width=28,
                      fg="#111827", font=("Poppins", 10, "bold"), show="*")
confirm_entry.place(x=490, y=363)

match_hint = Label(signup_frame, text="", bg="#0D1117", font=("Poppins", 10))
match_hint.place(x=490, y=388)

def check_password_match(event=None):
    if confirm_entry.get() == "":
        match_hint.config(text="", fg="#888")
    elif pass_entry1.get() == confirm_entry.get():
        match_hint.config(text="✓ Passwords match", fg="#1d9e75")
    else:
        match_hint.config(text="✗ Passwords do not match", fg="#e24b4a")

confirm_entry.bind("<KeyRelease>", check_password_match)
pass_entry1.bind("<KeyRelease>", check_password_match)

def toggle_password1():
    if pass_entry1.cget('show') == '':
        pass_entry1.config(show='*')
        confirm_entry.config(show='*')
        show_label1.config(text="Show Password")
    else:
        pass_entry1.config(show='')
        confirm_entry.config(show='')
        show_label1.config(text="Hide Password")

show_box1 = Checkbutton(signup_frame, bg="#0D1117", relief="flat", command=toggle_password1)
show_box1.place(x=100, y=390)
show_label1 = Label(signup_frame, bg="#0D1117", fg="#e6b024",
                    text="Show Password", font=("Poppins", 9))
show_label1.place(x=125, y=392)

otp_label = Label(signup_frame, text="OTP Verification Code *", bg="#0D1117", fg="#e6b024", font=("Poppins", 11))
otp_entry = Entry(signup_frame, relief="flat", width=40, fg="#111827", font=("Poppins", 10, "bold"))

signup_btn = Button(signup_frame, bg=color2, image=signup_button, bd=0, relief="flat",
                    highlightthickness=0, activebackground="black", command=lambda: auRegistration())
signup_btn.place(relx=0.5, anchor="n", y=470)

# ── SECURITY QUESTIONS AFTER SIGNUP ──────────────────────────────────────────
def show_security_questions(username):
    blur_image = Image.open(asset("images/blur2.png"))
    blur_image = blur_image.resize((master.winfo_screenwidth(), master.winfo_screenheight()))
    blur_photo = ImageTk.PhotoImage(blur_image)
    main_bg.config(image=blur_photo)
    main_bg.image = blur_photo
    login_bg.config(image=blur_photo)
    login_bg.image = blur_photo

    signup_frame.place_forget()
    show_login_btn.place_forget()
    show_signup_btn.place_forget()

    sq_outer = Frame(main_bg, bg="#0D1117", height=520, width=600)
    sq_outer.place(relx=0.5, rely=0.5, anchor="center")

    sq_header = Frame(sq_outer, bg="#111827", height=95, width=600)
    sq_header.place(x=0, y=0)
    sq_header.pack_propagate(False)

    Label(sq_outer, text="SECURITY QUESTIONS",
          bg="#111827", fg="#e6b024",
          font=("Poppins", 22, "bold")).place(relx=0.5, anchor="n", x=0, y=20)
    Label(sq_outer, text="These will be used to verify your identity if you forget your password.",
          bg="#111827", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=60)

    sq_questions = [
        "What is the name of your first pet?",
        "What is your mother's maiden name?",
        "What was the name of your elementary school?"
    ]
    entries = []
    y = 115
    Label(sq_outer, text="── ANSWER ALL THREE QUESTIONS ──",
          bg="#0D1117", fg="#888888",
          font=("Poppins", 9)).place(relx=0.5, anchor="n", x=0, y=y)
    y += 35
    for i, q in enumerate(sq_questions):
        Label(sq_outer, text=f"Q{i+1}: {q}", bg="#0D1117",
              fg="#e6b024", font=("Poppins", 10)).place(x=60, y=y)
        y += 28
        e = Entry(sq_outer, relief="flat", width=60,
                  fg="#0D1117", font=("Poppins", 10, "bold"))
        e.place(x=60, y=y)
        entries.append(e)
        y += 48

    hint_lbl = Label(sq_outer, text="", bg="#0D1117", font=("Poppins", 9))
    hint_lbl.place(x=60, y=y)

    def save_answers():
        answers = [e.get().strip() for e in entries]
        if any(a == "" for a in answers):
            hint_lbl.config(text="✗ Please answer all 3 questions.", fg="#e24b4a")
            return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE logincredentials
                    SET SecurityQ1 = %s, SecurityQ2 = %s, SecurityQ3 = %s
                    WHERE Username = %s
                """, (answers[0], answers[1], answers[2], username))
                conn.commit()
            except Exception as ex:
                messagebox.showerror("Error", f"{ex}")
                return
            finally:
                cursor.close()
                conn.close()

        sq_outer.destroy()
        main_bg.config(image=bg_photo)
        main_bg.image = bg_photo
        login_bg.config(image=bg_photo)
        login_bg.image = bg_photo
        show_login_btn.place(x=119, y=498)
        show_signup_btn.place(x=520, y=498)
        show_login_btn.config(image=buttonappearlogin_active)
        show_signup_btn.config(image=buttonappearsignup_default)
        global isLoginShown, isSignShown
        isLoginShown = True
        isSignShown  = False
        login_frame.place(x=987, y=175)

        for e in [fname_entry, lname_entry, mname_entry,
                  email1_entry, reg_email_entry, pass_entry1, confirm_entry]:
            e.delete(0, END)
        ext_var.set("None")
        match_hint.config(text="")
        messagebox.showinfo("Success", "Account created! Welcome!")

    save_btn = Button(sq_outer, text="  SAVE & CONTINUE  ",
                      bg="#e6b024", fg="#0D1117",
                      font=("Poppins", 11, "bold"), bd=0, relief="flat",
                      cursor="hand2", padx=40, pady=10,
                      command=save_answers)
    save_btn.place(relx=0.5, anchor="n", x=0, y=y + 20)

    for e in entries:
        e.bind("<Return>", lambda ev: save_answers())

# ── SEND OTP EMAIL ────────────────────────────────────────────────────────────
def send_otp_email(email, otp):
    config_path = os.path.join(BASE_DIR, "smtp_config.json")
    if not os.path.exists(config_path):
        template = {
            "sender_email": "YOUR_GMAIL_ADDRESS@gmail.com",
            "sender_password": "YOUR_GMAIL_APP_PASSWORD",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 465
        }
        try:
            with open(config_path, "w") as f:
                json.dump(template, f, indent=4)
        except Exception:
            pass
        return False, "smtp_config.json was not found. Created a template."

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        sender      = config.get("sender_email")
        pwd         = config.get("sender_password")
        server_host = config.get("smtp_server", "smtp.gmail.com")
        port        = config.get("smtp_port", 465)

        if not sender or not pwd or "YOUR_GMAIL" in sender or "YOUR_GMAIL" in pwd:
            return False, "SMTP configuration not configured in smtp_config.json."

        msg = MIMEMultipart()
        msg['From']    = sender
        msg['To']      = email
        msg['Subject'] = "Your OTP Verification Code"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #161616; text-align: center;">Account Verification</h2>
                <p>Thank you for registering. Please use the following One-Time Password (OTP) to complete your signup process:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #e6b024; background-color: #161616; padding: 10px 20px; border-radius: 5px;">{otp}</span>
                </div>
                <p style="color: #666666; font-size: 12px; text-align: center;">This OTP is valid for 10 minutes. If you did not request this code, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        if port == 465:
            server = smtplib.SMTP_SSL(server_host, port)
        else:
            server = smtplib.SMTP(server_host, port)
            server.starttls()

        server.login(sender, pwd)
        server.sendmail(sender, email, msg.as_string())
        server.close()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, str(e)

current_otp      = ""
pending_username = ""

# ── REGISTRATION HANDLER ──────────────────────────────────────────────────────
def auRegistration():
    global current_otp, pending_username
    first_name  = fname_entry.get().strip()
    last_name   = lname_entry.get().strip()
    middle_name = mname_entry.get().strip()
    ext_name    = ext_var.get() if ext_var.get() != "None" else ""
    username    = email1_entry.get().strip()
    reg_email   = reg_email_entry.get().strip()
    password    = pass_entry1.get().strip()
    confirm     = confirm_entry.get().strip()

    if not first_name or not last_name:
        messagebox.showwarning("Missing Fields", "First name and last name are required."); return
    if any(c.isdigit() for c in first_name):
        messagebox.showerror("Invalid Input", "First name must contain letters only."); return
    if any(c.isdigit() for c in last_name):
        messagebox.showerror("Invalid Input", "Last name must contain letters only."); return
    if middle_name and any(c.isdigit() for c in middle_name):
        messagebox.showerror("Invalid Input", "Middle name must contain letters only."); return
    if not username or not password:
        messagebox.showwarning("Missing Fields", "Username and password are required."); return
    if not reg_email:
        messagebox.showwarning("Missing Fields", "Email address is required."); return
    if not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address."); return
    if len(username) < 4:
        messagebox.showwarning("Invalid Username", "Username must be at least 4 characters."); return
    if len(password) < 6:
        messagebox.showwarning("Weak Password", "Password must be at least 6 characters."); return
    if password != confirm:
        messagebox.showerror("Password Mismatch", "Passwords do not match."); return

    if current_otp != "" and username == pending_username:
        entered_otp = otp_entry.get().strip()
        if entered_otp == "":
            messagebox.showwarning("Missing OTP", "Please enter the OTP verification code."); return
        if entered_otp == current_otp:
            if register_user(username, reg_email, password, first_name, last_name, middle_name, ext_name):
                current_otp      = ""
                pending_username = ""
                otp_label.place_forget()
                otp_entry.place_forget()
                signup_btn.place(relx=0.5, anchor="n", y=470)
                show_security_questions(username)
        else:
            messagebox.showerror("Verification Failed", "Invalid OTP. Please try again.")
        return

    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Username FROM logincredentials WHERE Username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Registration Error", "Username already exists."); return
        finally:
            cursor.close()
            conn.close()

    new_otp = str(random.randint(100000, 999999))
    success, msg = send_otp_email(reg_email, new_otp)
    if success:
        messagebox.showinfo("OTP Sent", f"A 6-digit verification code has been sent to {reg_email}.")
        current_otp      = new_otp
        pending_username = username
        otp_label.place(relx=0.5, anchor="n", y=425)
        otp_entry.place(relx=0.5, anchor="n", y=450)
        signup_btn.place(relx=0.5, anchor="n", y=490)
        otp_entry.delete(0, END)
        otp_entry.focus_set()
    else:
        messagebox.showerror("Email Error", f"Failed to send OTP:\n{msg}")

fname_entry.bind("<Return>",      lambda e: auRegistration())
lname_entry.bind("<Return>",      lambda e: auRegistration())
mname_entry.bind("<Return>",      lambda e: auRegistration())
email1_entry.bind("<Return>",     lambda e: auRegistration())
reg_email_entry.bind("<Return>",  lambda e: auRegistration())
pass_entry1.bind("<Return>",      lambda e: auRegistration())
confirm_entry.bind("<Return>",    lambda e: auRegistration())
otp_entry.bind("<Return>",        lambda e: auRegistration())

master.mainloop()