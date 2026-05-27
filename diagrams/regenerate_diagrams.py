from __future__ import annotations

from math import atan2, cos, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
OUT_ERD = BASE_DIR / "weldtrack-erd.png"
OUT_USE_CASE = BASE_DIR / "weldtrack-use-case.png"
OUT_SEQUENCE = BASE_DIR / "weldtrack-sequence.png"
OUT_ACTIVITY = BASE_DIR / "weldtrack-activity.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, chosen_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [text]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=chosen_font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_arrow_head(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: str = "#000000", width: int = 3, filled: bool = True) -> None:
    angle = atan2(end[1] - start[1], end[0] - start[0])
    arrow_len = 16
    arrow_w = 7
    left = (end[0] - arrow_len * cos(angle) + arrow_w * sin(angle), end[1] - arrow_len * sin(angle) - arrow_w * cos(angle))
    right = (end[0] - arrow_len * cos(angle) - arrow_w * sin(angle), end[1] - arrow_len * sin(angle) + arrow_w * cos(angle))
    if filled:
        draw.polygon([end, left, right], fill=color)
    else:
        draw.line([left, end, right], fill=color, width=width)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: str = "#000000", width: int = 3) -> None:
    draw.line([start, end], fill=color, width=width)
    draw_arrow_head(draw, start, end, color=color, width=width, filled=True)


def draw_orthogonal_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: str = "#000000", width: int = 2) -> None:
    if start[0] == end[0] or start[1] == end[1]:
        draw_arrow(draw, start, end, color=color, width=width)
    else:
        mid_y = (start[1] + end[1]) / 2
        points = [start, (start[0], mid_y), (end[0], mid_y), end]
        draw.line(points, fill=color, width=width)
        draw_arrow_head(draw, points[-2], points[-1], color=color, width=width)


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#4b5568",
    width: int = 3,
    dash_length: int = 12,
    gap_length: int = 8,
) -> None:
    total_length = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
    if total_length == 0:
        return
    steps = int(total_length // (dash_length + gap_length)) + 1
    for index in range(steps):
        t0 = index * (dash_length + gap_length) / total_length
        t1 = min((index * (dash_length + gap_length) + dash_length) / total_length, 1)
        if t0 >= 1:
            break
        x0 = start[0] + (end[0] - start[0]) * t0
        y0 = start[1] + (end[1] - start[1]) * t0
        x1 = start[0] + (end[0] - start[0]) * t1
        y1 = start[1] + (end[1] - start[1]) * t1
        draw.line([(x0, y0), (x1, y1)], fill=color, width=width)


def draw_dashed_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: str = "#000000", width: int = 3) -> None:
    draw_dashed_line(draw, start, end, color=color, width=width)
    draw_arrow_head(draw, start, end, color=color, width=width, filled=False)


def draw_rounded_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    fill: str,
    outline: str,
    radius: int = 18,
    width: int = 3,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_oval_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    fill: str,
    outline: str,
    width: int = 3,
) -> None:
    draw.ellipse(xy, fill=fill, outline=outline, width=width)


def draw_actor_figure(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    top_y: int,
    role: str,
    color: str,
) -> None:
    head_radius = 24
    head_center_y = top_y + head_radius
    body_top = top_y + 52
    body_bottom = top_y + 110
    arm_y = top_y + 72
    leg_split_y = top_y + 110

    draw.ellipse((center_x - head_radius, head_center_y - head_radius, center_x + head_radius, head_center_y + head_radius), outline=color, width=4)
    draw.line((center_x, body_top, center_x, body_bottom), fill=color, width=4)
    draw.line((center_x - 34, arm_y, center_x + 34, arm_y), fill=color, width=4)
    draw.line((center_x, body_bottom, center_x - 24, body_bottom + 42), fill=color, width=4)
    draw.line((center_x, body_bottom, center_x + 24, body_bottom + 42), fill=color, width=4)

    role_font = font(26, bold=True)
    bbox = draw.textbbox((0, 0), role, font=role_font)
    text_x = center_x - ((bbox[2] - bbox[0]) / 2)
    text_y = top_y + 166
    draw.text((text_x, text_y), role, font=role_font, fill="#172033")


def draw_centered_label_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    label: str,
    fill: str,
    outline: str,
    text_fill: str = "#172033",
    label_size: int = 28,
) -> None:
    draw_rounded_box(draw, xy, fill=fill, outline=outline)
    box_font = font(label_size, bold=True)
    max_width = xy[2] - xy[0] - 28
    lines = wrap_text(draw, label, box_font, max_width)
    line_height = box_font.getbbox("Ag")[3] + 4
    total_height = len(lines) * line_height
    top = xy[1] + ((xy[3] - xy[1]) - total_height) / 2 - 2
    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=box_font)
        x = xy[0] + ((xy[2] - xy[0]) - (bbox[2] - bbox[0])) / 2
        y = top + index * line_height
        draw.text((x, y), line, font=box_font, fill=text_fill)


def draw_entity_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    fill: str,
    outline: str,
) -> None:
    draw_rounded_box(draw, xy, fill="#ffffff", outline="#b8c1cc", radius=10, width=2)
    title_font = font(18, bold=True)
    body_font = font(13)
    key_font = font(12, bold=True)
    x1, y1, x2, y2 = xy
    header_h = 30
    draw.rectangle((x1, y1, x2, y1 + header_h), fill="#f5f7fa", outline="#b8c1cc", width=1)
    draw.line((x1, y1 + header_h, x2, y1 + header_h), fill="#b8c1cc", width=1)
    draw.text((x1 + 10, y1 + 7), title, font=title_font, fill="#1f2937")

    rows = [line for line in lines if line]
    pk_row = next((line for line in rows if line.endswith(" PK")), None)
    if pk_row is not None:
        rows.remove(pk_row)
    fields = [line[:-3] if line.endswith(" PK") or line.endswith(" FK") else line for line in rows]

    row_top = y1 + header_h
    pk_row_h = 22
    key_col_x = x1 + 10
    field_col_x = x1 + 86
    key_split_x = x1 + 72
    draw.line((key_split_x, row_top, key_split_x, y2), fill="#d0d7df", width=1)

    pk_y = row_top
    draw.line((x1, pk_y, x2, pk_y), fill="#d0d7df", width=1)
    if pk_row:
        draw.text((field_col_x, pk_y + 4), pk_row[:-3], font=body_font, fill="#374151")
        badge_x = key_col_x + 4
        badge_y = pk_y + 2
        draw.rounded_rectangle((badge_x, badge_y, badge_x + 36, badge_y + 16), radius=6, fill="#eef2f7", outline="#cbd5e1", width=1)
        draw.text((badge_x + 8, badge_y + 1), "PK", font=font(10, bold=True), fill="#374151")

    block_y = pk_y + pk_row_h
    draw.line((x1, block_y, x2, block_y), fill="#d0d7df", width=1)
    if fields:
        field_font = font(12)
        line_height = 15
        text_y = block_y + 4
        fk_count = 1
        for index, field_text in enumerate(fields):
            key_label = ""
            if index < len(rows):
                original_line = rows[index]
                if original_line.endswith(" FK"):
                    key_label = f"FK{fk_count}"
                    fk_count += 1
            draw.text((field_col_x, text_y + index * line_height), field_text, font=field_font, fill="#374151")
            if key_label:
                badge_x = key_col_x + 4
                badge_y = block_y + 2 + index * line_height
                draw.rounded_rectangle((badge_x, badge_y, badge_x + 36, badge_y + 16), radius=6, fill="#eef2f7", outline="#cbd5e1", width=1)
                draw.text((badge_x + 5, badge_y + 1), key_label, font=font(10, bold=True), fill="#374151")


def draw_use_case(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    label: str,
    fill: str = "#ffffff",
    outline: str = "#000000",
) -> None:
    draw_oval_box(draw, xy, fill=fill, outline=outline, width=2)
    use_case_font = font(18)
    max_width = xy[2] - xy[0] - 20
    lines = wrap_text(draw, label, use_case_font, max_width)
    line_height = use_case_font.getbbox("Ag")[3] + 4
    total_height = len(lines) * line_height
    top = xy[1] + ((xy[3] - xy[1]) - total_height) / 2
    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=use_case_font)
        x = xy[0] + ((xy[2] - xy[0]) - (bbox[2] - bbox[0])) / 2
        y = top + index * line_height
        draw.text((x, y), line, font=use_case_font, fill="#000000")


def generate_use_case() -> None:
    width, height = 2000, 1400
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=28, fill="#ffffff", outline="#000000", width=3)
    draw.text((44, 42), "WeldTrack Use Case Diagram", font=font(34, bold=True), fill="#000000")

    boundary = (400, 120, 1650, 1320)
    draw.rectangle(boundary, outline="#cbd5e1", width=2)
    draw.text((410, 130), "WeldTrack System", font=font(20, bold=True), fill="#475569")

    draw_actor_figure(draw, 180, 400, "Customer", "#000000")
    draw_actor_figure(draw, 180, 900, "Staff", "#000000")
    draw_actor_figure(draw, 1820, 650, "Admin", "#000000")

    col1_x = 430
    col2_x = 835
    col3_x = 1240
    
    uc_col1 = [
        (col1_x, 180, "Manage Addresses"),
        (col1_x, 280, "Create Booking"),
        (col1_x, 380, "Track Projects"),
        (col1_x, 480, "Provide Feedback"),
        (col1_x, 900, "Record Attendance"),
        (col1_x, 1000, "Submit Photos (Before/After)"),
    ]
    uc_col2 = [
        (col2_x, 900, "View Assigned Tasks"),
        (col2_x, 1000, "Report Material Usage"),
    ]
    uc_col3 = [
        (col3_x, 180, "Approve & Schedule Bookings"),
        (col3_x, 300, "Complete Projects & Final Costing"),
        (col3_x, 420, "Manage Inventory & Stock"),
        (col3_x, 540, "Manage Service Catalog"),
        (col3_x, 660, "Generate PDF Reports"),
        (col3_x, 780, "Manage Users & Banning"),
        (col3_x, 900, "Assign Tasks to Staff"),
    ]

    def draw_uc_at(x, y, label):
        w, h = 320, 80
        draw_use_case(draw, (x, y, x + w, y + h), label)
        return (x, y, w, h)

    for i, (x, y, label) in enumerate(uc_col1):
        draw_uc_at(x, y, label)
        if i < 4:
            draw.line((180, 480, x, y + 40), fill="#94a3b8", width=1)
        else:
            draw.line((180, 980, x, y + 40), fill="#94a3b8", width=1)

    for x, y, label in uc_col2:
        draw_uc_at(x, y, label)
        draw.line((180, 980, x, y + 40), fill="#94a3b8", width=1)
        draw.line((1820, 730, x + 320, y + 40), fill="#94a3b8", width=1)

    for x, y, label in uc_col3:
        draw_uc_at(x, y, label)
        draw.line((1820, 730, x + 320, y + 40), fill="#94a3b8", width=1)

    image.save(OUT_USE_CASE)


def generate_erd() -> None:
    width, height = 2200, 1560
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=26, fill="white", outline="#cbd5e1", width=3)
    draw.text((48, 44), "WeldTrack ER Diagram", font=font(34, bold=True), fill="#0f172a")

    entity_specs = {
        "USERS": ((76, 108, 430, 342), "#ffffff", ["id PK", "email", "hashed_password", "role", "is_banned", "is_online", "created_at"]),
        "CUSTOMER_ADDRESSES": ((76, 370, 430, 632), "#ffffff", ["id PK", "user_id FK", "label", "province", "municipality", "barangay", "house", "is_active"]),
        "EMAIL_VERIFICATIONS": ((76, 670, 430, 892), "#ffffff", ["id PK", "user_id FK", "is_verified", "verification_code", "code_expires_at"]),
        "ATTENDANCE_RECORDS": ((76, 930, 430, 1132), "#ffffff", ["id PK", "email", "date", "hours_worked", "regular_hours", "overtime_hours"]),
        "FEEDBACKS": ((76, 1220, 430, 1422), "#ffffff", ["id PK", "customer_name", "email", "project_type", "rating", "comment"]),
        "BOOKINGS": ((560, 108, 1040, 416), "#ffffff", ["id PK", "project_type", "status", "customer_name", "email", "phone", "estimated_cost", "material_cost", "total_price"]),
        "SERVICES": ((560, 468, 1040, 676), "#ffffff", ["id PK", "name", "description", "price", "image_url"]),
        "BOOKING_MATERIALS": ((560, 734, 1040, 970), "#ffffff", ["id PK", "booking_id FK", "item_id", "name", "qty", "unit_price", "subtotal"]),
        "STAFF_TASKS": ((1110, 108, 1590, 392), "#ffffff", ["id PK", "project_name", "title", "booking_id FK", "due_date", "status", "location fields"]),
        "STAFF_TASK_ASSIGNEES": ((1110, 422, 1590, 640), "#ffffff", ["task_id FK", "staff_id FK"]),
        "TASK_MATERIAL_USAGES": ((1110, 702, 1590, 1020), "#ffffff", ["id PK", "task_id FK", "booking_id FK", "submitted_by_staff_id FK", "before_image_url", "after_image_url"]),
        "TASK_MATERIAL_USAGE_LINES": ((1110, 1070, 1590, 1290), "#ffffff", ["id PK", "usage_id FK", "item_id", "quantity"]),
    }

    def link(a: str, b: str, label: str | None = None, label_pos: tuple[int, int] | None = None) -> None:
        ax1, ay1, ax2, ay2 = entity_specs[a][0]
        bx1, by1, bx2, by2 = entity_specs[b][0]
        start = (ax2, (ay1 + ay2) / 2)
        end = (bx1, (by1 + by2) / 2)
        if bx1 > ax2:
            mid_x = (ax2 + bx1) / 2
            draw.line([start, (mid_x, start[1]), (mid_x, end[1]), end], fill="#334155", width=4)
            draw_arrow(draw, (mid_x, end[1]), (end[0] - 8, end[1]), color="#334155", width=4)
        else:
            mid_x = ax2 + 30
            draw.line([start, (mid_x, start[1]), (mid_x, end[1]), end], fill="#334155", width=4)
            draw_arrow(draw, (mid_x, end[1]), (end[0] - 8, end[1]), color="#334155", width=4)
        if label and label_pos:
            lx, ly = label_pos
            draw.rounded_rectangle((lx, ly, lx + 52, ly + 26), radius=10, fill="white", outline="#cbd5e1", width=2)
            draw.text((lx + 11, ly + 4), label, font=font(14), fill="#475569")

    def left_gutter_link(a: str, b: str, label: str | None = None, label_pos: tuple[int, int] | None = None) -> None:
        ax1, ay1, ax2, ay2 = entity_specs[a][0]
        bx1, by1, bx2, by2 = entity_specs[b][0]
        center_x = (ax1 + ax2) / 2
        start_y = ay2
        end_y = by1
        draw.line([(center_x, start_y), (center_x, end_y)], fill="#334155", width=4)
        draw_arrow(draw, (center_x, end_y - 1), (center_x, end_y + 8), color="#334155", width=4)
        if label and label_pos:
            lx, ly = label_pos
            draw.rounded_rectangle((lx, ly, lx + 52, ly + 26), radius=10, fill="white", outline="#cbd5e1", width=2)
            draw.text((lx + 11, ly + 4), label, font=font(14), fill="#475569")

    link("USERS", "BOOKINGS", "1-*", (456, 194))
    left_gutter_link("USERS", "CUSTOMER_ADDRESSES", "1-1", (227, 343))
    link("BOOKINGS", "BOOKING_MATERIALS", "1-*", (1044, 580))
    link("BOOKINGS", "STAFF_TASKS", "1-*", (1044, 206))

    # Link BOOKINGS to SERVICES (Vertical)
    bookings_xy = entity_specs["BOOKINGS"][0]
    services_xy = entity_specs["SERVICES"][0]
    v_mid_x = (bookings_xy[0] + bookings_xy[2]) / 2
    draw.line([(v_mid_x, bookings_xy[3]), (v_mid_x, services_xy[1])], fill="#334155", width=4)
    draw_arrow(draw, (v_mid_x, services_xy[1] - 1), (v_mid_x, services_xy[1] + 8), color="#334155", width=4)
    draw.rounded_rectangle((v_mid_x - 26, 429, v_mid_x + 26, 455), radius=10, fill="white", outline="#cbd5e1", width=2)
    draw.text((v_mid_x - 15, 433), "1-*", font=font(14), fill="#475569")

    link("BOOKING_MATERIALS", "TASK_MATERIAL_USAGES", None)
    left_gutter_link("STAFF_TASKS", "STAFF_TASK_ASSIGNEES", "1-*", (1324, 394))
    left_gutter_link("STAFF_TASK_ASSIGNEES", "TASK_MATERIAL_USAGES", "1-*", (1324, 658))
    left_gutter_link("TASK_MATERIAL_USAGES", "TASK_MATERIAL_USAGE_LINES", "1-*", (1324, 1032))
    left_gutter_link("CUSTOMER_ADDRESSES", "EMAIL_VERIFICATIONS", "1-1", (227, 638))

    for title, (xy, fill, lines) in entity_specs.items():
        draw_entity_box(draw, xy, title, lines, fill, "#b8c1cc")

    image.save(OUT_ERD)


def generate_sequence_diagram() -> None:
    width, height = 1900, 1200
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=28, fill="#ffffff", outline="#cbd5e1", width=3)
    draw.text((44, 42), "WeldTrack Sequence Diagram - Approve Booking", font=font(34, bold=True), fill="#0f172a")

    participants = [
        (180, "Customer"),
        (520, "Frontend"),
        (900, "Booking Store"),
        (1270, "Backend API"),
        (1640, "Services"),
    ]
    header_y = 150
    lifeline_bottom = 1040
    box_w = 220
    box_h = 48

    for center_x, label in participants:
        left = center_x - box_w // 2
        right = center_x + box_w // 2
        draw.rounded_rectangle((left, header_y, right, header_y + box_h), radius=18, fill="#ffffff", outline="#cbd5e1", width=2)
        bbox = draw.textbbox((0, 0), label, font=font(24, bold=True))
        draw.text((center_x - (bbox[2] - bbox[0]) / 2, header_y + 12), label, font=font(24, bold=True), fill="#172033")
        draw_dashed_line(draw, (center_x, header_y + box_h), (center_x, lifeline_bottom), color="#000000", width=2, dash_length=10, gap_length=8)

    def message(y: int, start_idx: int, end_idx: int, text: str, dashed: bool = False) -> None:
        start_x = participants[start_idx][0]
        end_x = participants[end_idx][0]
        label_font = font(16)
        max_text_width = abs(end_x - start_x) - 40
        lines = wrap_text(draw, text, label_font, max_text_width)
        line_height = label_font.getbbox("Ag")[3] + 4
        total_text_height = len(lines) * line_height
        for i, line in enumerate(lines):
            text_bbox = draw.textbbox((0, 0), line, font=label_font)
            text_w = text_bbox[2] - text_bbox[0]
            text_x = (start_x + end_x) / 2 - text_w / 2
            text_y = y - total_text_height - 10 + (i * line_height)
            draw.text((text_x, text_y), line, font=label_font, fill="#172033")
        if dashed:
            draw_dashed_arrow(draw, (start_x, y), (end_x, y), color="#000000", width=3)
        else:
            draw_arrow(draw, (start_x, y), (end_x, y), color="#000000", width=3)

    def activation(center_idx: int, y0: int, y1: int) -> None:
        x = participants[center_idx][0]
        draw.rounded_rectangle((x - 10, y0, x + 10, y1), radius=6, fill="#ffffff", outline="#000000", width=1)

    message(260, 0, 1, "Select service and fill details")
    message(320, 1, 2, "Submit booking request")
    activation(2, 300, 420)
    message(440, 2, 3, "POST /bookings (Pending status)")
    message(500, 3, 2, "Booking created successfully", dashed=True)
    message(560, 2, 1, "Notify customer of pending status", dashed=True)
    message(660, 0, 1, "Staff opens booking approval")
    message(720, 1, 4, "GET /services (fetch base prices)")
    message(780, 4, 1, "Return service list with current prices", dashed=True)
    message(840, 0, 1, "Set estimated cost and schedule date")
    message(900, 1, 2, "Confirm booking with final cost and schedule")
    activation(2, 880, 980)
    message(1020, 2, 3, "PATCH /bookings/{id} (Confirmed status)")
    draw.text((48, 1120), "Key point: the frontend loads /services to get the admin-set price before confirming the booking.", font=font(18), fill="#475569")
    image.save(OUT_SEQUENCE)


def draw_diamond(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, outline: str) -> None:
    x1, y1, x2, y2 = xy
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    draw.polygon([(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)], fill=fill, outline=outline, width=2)


def generate_activity_diagram() -> None:
    width, height = 1500, 1800
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=28, fill="#ffffff", outline="#cbd5e1", width=3)
    draw.text((44, 42), "WeldTrack Activity Diagram - Booking Lifecycle", font=font(34, bold=True), fill="#0f172a")

    lane_y = 120
    lane_h = 1600
    l1_x, l2_x, l3_x = 50, 516, 982
    lane_w = 466

    draw.line((l2_x, lane_y, l2_x, lane_y + lane_h), fill="#cbd5e1", width=2)
    draw.line((l3_x, lane_y, l3_x, lane_y + lane_h), fill="#cbd5e1", width=2)
    draw.text((l1_x + 150, lane_y + 10), "Customer", font=font(24, bold=True), fill="#475569")
    draw.text((l2_x + 180, lane_y + 10), "Admin", font=font(24, bold=True), fill="#475569")
    draw.text((l3_x + 180, lane_y + 10), "Staff", font=font(24, bold=True), fill="#475569")
    draw.line((l1_x, lane_y + 50, l1_x + lane_w * 3, lane_y + 50), fill="#cbd5e1", width=2)

    def get_lane_center(lane_idx):
        if lane_idx == 0: return l1_x + lane_w / 2
        if lane_idx == 1: return l2_x + lane_w / 2
        return l3_x + lane_w / 2

    current_y = 220

    def node(lane_idx: int, label: str, shape: str = "action", w: int = 240, h: int = 60, y: int | None = None) -> tuple[int, int, int, int]:
        nonlocal current_y
        use_y = y if y is not None else current_y
        cx = get_lane_center(lane_idx)
        rect = (cx - w // 2, use_y, cx + w // 2, use_y + h)
        if shape == "action":
            draw_rounded_box(draw, rect, fill="#ffffff", outline="#000000", radius=15, width=2)
            f = font(16)
            lines = wrap_text(draw, label, f, w - 20)
            lh = f.getbbox("Ag")[3] + 4
            th = len(lines) * lh
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=f)
                draw.text((cx - (bbox[2] - bbox[0]) / 2, use_y + (h - th) / 2 + i * lh), line, font=f, fill="#000000")
        elif shape == "decision":
            draw_diamond(draw, rect, fill="#ffffff", outline="#000000")
            f = font(14, bold=True)
            bbox = draw.textbbox((0, 0), label, font=f)
            draw.text((cx - (bbox[2] - bbox[0]) / 2, use_y + (h - (bbox[3] - bbox[1])) / 2), label, font=f, fill="#000000")
        elif shape == "start":
            draw.ellipse((cx - 15, use_y, cx + 15, use_y + 30), fill="#000000")
            rect = (cx - 15, use_y, cx + 15, use_y + 30)
        elif shape == "end":
            draw.ellipse((cx - 20, use_y, cx + 20, use_y + 40), outline="#000000", width=2)
            draw.ellipse((cx - 12, use_y + 8, cx + 12, use_y + 32), fill="#000000")
            rect = (cx - 20, use_y, cx + 20, use_y + 40)
        if y is None: current_y += h + 80
        return rect

    s1 = node(0, "", "start", h=30)
    r1 = node(0, "Submits booking request")
    draw_orthogonal_arrow(draw, (get_lane_center(0), s1[3]), (get_lane_center(0), r1[1]))
    r2 = node(1, "Reviews booking details")
    draw_orthogonal_arrow(draw, (get_lane_center(0), r1[3]), (get_lane_center(1), r2[1]))
    d1 = node(1, "Is Valid?", "decision", w=160, h=80)
    draw_orthogonal_arrow(draw, (get_lane_center(1), r2[3]), (get_lane_center(1), d1[1]))

    r3 = node(1, "Sets schedule and estimated cost", h=50) # Reduced h to fix "extra in bottom"
    draw_orthogonal_arrow(draw, (get_lane_center(1), d1[3]), (get_lane_center(1), r3[1]))
    draw.text((get_lane_center(1) + 10, d1[3] + 10), "Yes", font=font(14), fill="#000000")

    # Cancellation path - moved LOWER and restored width
    # We use explicit y to avoid affecting the main path's current_y
    r_cancel_y = r3[3] + 100
    r_cancel = node(1, "Cancel Booking", y=r_cancel_y, w=240)
    
    # Connection for "No" - routed from left of d1, down past r3, then to left of r_cancel
    draw.line([(get_lane_center(1) - 80, d1[1] + 40), (get_lane_center(1) - 150, d1[1] + 40), (get_lane_center(1) - 150, r_cancel[1] + 30), (r_cancel[0], r_cancel[1] + 30)], fill="#000000", width=2)
    draw_arrow_head(draw, (r_cancel[0] - 10, r_cancel[1] + 30), (r_cancel[0], r_cancel[1] + 30), color="#000000")
    draw.text((get_lane_center(1) - 110, d1[1] + 15), "No", font=font(14), fill="#000000")
    
    e_fail = node(1, "", "end", y=r_cancel[3] + 80)
    draw_orthogonal_arrow(draw, (get_lane_center(1), r_cancel[3]), (get_lane_center(1), e_fail[1]))

    r4 = node(2, "Performs welding service at site")
    draw_orthogonal_arrow(draw, (get_lane_center(1), r3[3]), (get_lane_center(2), r4[1]))
    r5 = node(2, "Reports material usage & uploads photos")
    draw_orthogonal_arrow(draw, (get_lane_center(2), r4[3]), (get_lane_center(2), r5[1]))
    
    r6 = node(1, "Verifies work and calculates final price")
    draw_orthogonal_arrow(draw, (get_lane_center(2), r5[3]), (get_lane_center(1), r6[1]))
    r7 = node(1, "Marks Booking as Completed")
    draw_orthogonal_arrow(draw, (get_lane_center(1), r6[3]), (get_lane_center(1), r7[1]))
    e_success = node(1, "", "end")
    draw_orthogonal_arrow(draw, (get_lane_center(1), r7[3]), (get_lane_center(1), e_success[1]))

    image.save(OUT_ACTIVITY)


def main() -> None:
    generate_erd()
    generate_use_case()
    generate_sequence_diagram()
    generate_activity_diagram()

if __name__ == "__main__":
    main()
