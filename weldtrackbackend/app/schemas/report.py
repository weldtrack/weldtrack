from datetime import date
from pydantic import BaseModel
from typing import List


# =========================
# DATE RANGE REQUEST
# =========================
class ReportDateRange(BaseModel):
    start_date: date
    end_date: date


# =========================
# INVENTORY REPORT
# =========================
class InventoryReport(BaseModel):
    total_items: int
    low_stock_items: int
    total_stock_value: float


# =========================
# PROJECT REPORT
# =========================
class ProjectReport(BaseModel):
    total_projects: int
    ongoing_projects: int
    completed_projects: int
    total_expenses: float


# =========================
# FINANCIAL REPORT
# =========================
class FinancialReport(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float


# =========================
# ATTENDANCE REPORT
# =========================
class AttendanceReport(BaseModel):
    total_staff: int
    total_hours: float
    average_hours_per_staff: float

    total_overtime_hours: float
    staff_with_overtime: int
    average_overtime_per_staff: float


# =========================
# FULL REPORT RESPONSE
# =========================
class DashboardReport(BaseModel):
    inventory: InventoryReport
    projects: ProjectReport
    financial: FinancialReport
    attendance: AttendanceReport