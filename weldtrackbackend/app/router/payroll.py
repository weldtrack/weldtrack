from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.attendance import AttendanceRecord
from app.models.payroll import Payslip, PayslipStatus
from app.models.user import User, UserRole
from app.schemas.payroll import PayslipCreate, PayslipResponse, PayslipStatusUpdate

router = APIRouter(prefix="/payroll", tags=["payroll"])
MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


@router.get("", response_model=list[PayslipResponse])
def list_payslips(
    staff_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = select(Payslip)
    if staff_id:
        query = query.where(Payslip.staff_id == staff_id)
    return db.scalars(
        query.order_by(desc(Payslip.period_end), desc(Payslip.created_at))
        .offset(skip)
        .limit(limit)
    ).all()


@router.get("/mine", response_model=list[PayslipResponse])
def list_my_payslips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.staff:
        raise HTTPException(status_code=403, detail="Only staff can view personal payslips")
    return db.scalars(
        select(Payslip)
        .where(
            Payslip.staff_id == current_user.id,
            Payslip.status.in_((PayslipStatus.approved, PayslipStatus.paid)),
        )
        .order_by(desc(Payslip.period_end), desc(Payslip.created_at))
    ).all()


@router.post("", response_model=PayslipResponse, status_code=status.HTTP_201_CREATED)
def create_payslip(
    payload: PayslipCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    staff = db.get(User, payload.staff_id)
    if staff is None or staff.role != UserRole.staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    hours = db.execute(
        select(
            func.coalesce(func.sum(AttendanceRecord.regular_hours), 0),
            func.coalesce(func.sum(AttendanceRecord.overtime_hours), 0),
        ).where(
            and_(
                AttendanceRecord.email == staff.email,
                AttendanceRecord.date >= payload.period_start.isoformat(),
                AttendanceRecord.date <= payload.period_end.isoformat(),
            )
        )
    ).one()
    regular_hours = Decimal(str(hours[0])).quantize(MONEY)
    overtime_hours = Decimal(str(hours[1])).quantize(MONEY)
    overtime_rate = (
        payload.overtime_rate
        if payload.overtime_rate is not None
        else money(payload.hourly_rate * Decimal("1.25"))
    )
    regular_pay = money(regular_hours * payload.hourly_rate)
    overtime_pay = money(overtime_hours * overtime_rate)
    gross_pay = money(regular_pay + overtime_pay + payload.allowances + payload.bonuses)
    net_pay = money(gross_pay - payload.deductions)
    if net_pay < 0:
        raise HTTPException(status_code=422, detail="Deductions cannot exceed gross pay")

    payslip = Payslip(
        staff_id=staff.id,
        staff_email=staff.email,
        period_start=payload.period_start,
        period_end=payload.period_end,
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        hourly_rate=money(payload.hourly_rate),
        overtime_rate=money(overtime_rate),
        regular_pay=regular_pay,
        overtime_pay=overtime_pay,
        allowances=money(payload.allowances),
        bonuses=money(payload.bonuses),
        deductions=money(payload.deductions),
        gross_pay=gross_pay,
        net_pay=net_pay,
        notes=payload.notes,
        created_by_id=admin.id,
    )
    db.add(payslip)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A payslip already exists for this staff member and pay period",
        ) from None
    db.refresh(payslip)
    return payslip


@router.patch("/{payslip_id}/status", response_model=PayslipResponse)
def update_payslip_status(
    payslip_id: str,
    payload: PayslipStatusUpdate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    payslip = db.get(Payslip, payslip_id)
    if payslip is None:
        raise HTTPException(status_code=404, detail="Payslip not found")
    transitions = {
        PayslipStatus.draft: {PayslipStatus.approved},
        PayslipStatus.approved: {PayslipStatus.paid},
        PayslipStatus.paid: set(),
    }
    if payload.status != payslip.status and payload.status not in transitions[payslip.status]:
        raise HTTPException(status_code=409, detail="Invalid payslip status transition")
    payslip.status = payload.status
    db.commit()
    db.refresh(payslip)
    return payslip


@router.delete("/{payslip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_payslip(
    payslip_id: str,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    payslip = db.get(Payslip, payslip_id)
    if payslip is None:
        raise HTTPException(status_code=404, detail="Payslip not found")
    if payslip.status != PayslipStatus.draft:
        raise HTTPException(status_code=409, detail="Only draft payslips can be deleted")
    db.delete(payslip)
    db.commit()
