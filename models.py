from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # ADMIN / EMPLOYEE
    is_active = db.Column(db.Boolean, default=True)

    profile = db.relationship("EmployeeProfile", backref="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    job_title = db.Column(db.String(100))
    salary = db.Column(db.Float)

    profile_picture = db.Column(db.String(200))

from datetime import date, datetime
from extensions import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date, default=date.today)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # Present / Half-day / Absent / Leave

    user = db.relationship("User", backref="attendance_records")

class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    leave_type = db.Column(db.String(50))  # Paid / Sick / Unpaid
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reason = db.Column(db.Text)

    status = db.Column(db.String(20), default="Pending")  # Pending / Approved / Rejected
    admin_comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship("User", backref="leave_requests")



