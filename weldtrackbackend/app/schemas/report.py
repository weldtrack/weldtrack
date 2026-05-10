from datetime import date
from pydantic import BaseModel
from typing import List


class ReportDateRange(BaseModel):
    start_date: date
    end_date: date


class InventoryReport(BaseModel):
    total_items: int
    low_stock_items: int
    total_stock_value: float


class ProjectReport(BaseModel):
    total_projects: int
    ongoing_projects: int
    completed_projects: int
    total_expenses: float


class FinancialReport(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float


class AttendanceReport(BaseModel):
    total_staff: int
    total_hours: float
    average_hours_per_staff: float

    total_overtime_hours: float
    staff_with_overtime: int
    average_overtime_per_staff: float


class DashboardReport(BaseModel):
    inventory: InventoryReport
    projects: ProjectReport
    financial: FinancialReport
    attendance: AttendanceReport