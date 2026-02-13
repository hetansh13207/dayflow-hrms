from flask_login import login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, redirect, url_for, flash
from models import User, EmployeeProfile, Attendance, LeaveRequest
from extensions import db, login_manager
from datetime import date, datetime
from config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------- AUTH ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # ✅ BLOCK logged-in users
    if current_user.is_authenticated:
        if current_user.role == "ADMIN":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("employee_dashboard"))

    if request.method == "POST":
        employee_id = request.form["employee_id"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("signup"))

        user = User(
            employee_id=employee_id,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully")
        return redirect(url_for("login"))

    return render_template("auth/signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    # ✅ BLOCK logged-in users
    if current_user.is_authenticated:
        if current_user.role == "ADMIN":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("employee_dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            if user.role == "ADMIN":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("employee_dashboard"))

        flash("Invalid email or password")
        return redirect(url_for("login"))

    return render_template("auth/login.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------- DASHBOARDS ----------------
@app.route("/employee/dashboard")
@login_required
def employee_dashboard():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))
    return render_template("employee/dashboard.html")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))
    return render_template("admin/dashboard.html")

@app.route("/employee/profile")
@login_required
def employee_profile():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()
    return render_template("employee/profile.html", profile=profile)

@app.route("/employee/profile/edit", methods=["GET", "POST"])
@login_required
def edit_employee_profile():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    profile = EmployeeProfile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        profile = EmployeeProfile(user_id=current_user.id)
        db.session.add(profile)

    if request.method == "POST":
        profile.full_name = request.form["full_name"]
        profile.phone = request.form["phone"]
        profile.address = request.form["address"]

        db.session.commit()
        return redirect(url_for("employee_profile"))

    return render_template("employee/edit_profile.html", profile=profile)

@app.route("/admin/employees")
@login_required
def admin_employees():
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    employees = User.query.filter_by(role="EMPLOYEE").all()
    return render_template("admin/employees.html", employees=employees)

@app.route("/admin/employee/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit_employee(user_id):
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)

    profile = EmployeeProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = EmployeeProfile(user_id=user.id)
        db.session.add(profile)

    if request.method == "POST":
        profile.full_name = request.form["full_name"]
        profile.phone = request.form["phone"]
        profile.address = request.form["address"]
        profile.job_title = request.form["job_title"]
        profile.salary = request.form["salary"]

        db.session.commit()
        return redirect(url_for("admin_employees"))

    return render_template("admin/edit_employee.html", user=user, profile=profile)

@app.route("/employee/attendance")
@login_required
def employee_attendance():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    records = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.date.desc()).all()
    today = date.today()

    today_record = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    return render_template(
        "employee/attendance.html",
        records=records,
        today_record=today_record
    )

@app.route("/employee/checkin")
@login_required
def employee_checkin():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    today = date.today()

    record = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    if not record:
        record = Attendance(
            user_id=current_user.id,
            date=today,
            check_in=datetime.now(),
            status="Present"
        )
        db.session.add(record)
    else:
        if not record.check_in:
            record.check_in = datetime.now()

    db.session.commit()
    return redirect(url_for("employee_attendance"))

@app.route("/employee/checkout")
@login_required
def employee_checkout():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    today = date.today()

    record = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()

    if record and not record.check_out:
        record.check_out = datetime.now()

    db.session.commit()
    return redirect(url_for("employee_attendance"))

@app.route("/admin/attendance")
@login_required
def admin_attendance():
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template("admin/attendance.html", records=records)

@app.route("/employee/leave", methods=["GET", "POST"])
@login_required
def employee_leave():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    if request.method == "POST":
        start_date = datetime.strptime(
            request.form["start_date"], "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            request.form["end_date"], "%Y-%m-%d"
        ).date()

        leave = LeaveRequest(
            user_id=current_user.id,
            leave_type=request.form["leave_type"],
            start_date=start_date,
            end_date=end_date,
            reason=request.form["reason"]
        )

        db.session.add(leave)
        db.session.commit()
        return redirect(url_for("employee_leave"))

    leaves = LeaveRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(LeaveRequest.created_at.desc()).all()

    return render_template("employee/leave.html", leaves=leaves)

@app.route("/admin/leaves")
@login_required
def admin_leaves():
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    leaves = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    return render_template("admin/leaves.html", leaves=leaves)

@app.route("/admin/leave/<int:leave_id>", methods=["GET", "POST"])
@login_required
def admin_leave_action(leave_id):
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    leave = LeaveRequest.query.get_or_404(leave_id)

    if request.method == "POST":
        leave.status = request.form["status"]
        leave.admin_comment = request.form["admin_comment"]
        db.session.commit()
        return redirect(url_for("admin_leaves"))

    return render_template("admin/leave_action.html", leave=leave)

@app.route("/employee/payroll")
@login_required
def employee_payroll():
    if current_user.role != "EMPLOYEE":
        return redirect(url_for("login"))

    profile = EmployeeProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    return render_template(
        "employee/payroll.html",
        profile=profile
    )

@app.route("/admin/payroll")
@login_required
def admin_payroll():
    if current_user.role != "ADMIN":
        return redirect(url_for("login"))

    employees = User.query.filter_by(role="EMPLOYEE").all()
    return render_template(
        "admin/payroll.html",
        employees=employees
    )


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
