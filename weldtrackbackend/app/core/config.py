import os

"""
Authentication and security configuration.
"""

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "access_token")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "true").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax")
PASSWORD_HASH_ITERATIONS = 120_000
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"

FIXED_LABOR_RATE = 150.0 # PHP per hour

# Attendance rules use Philippine time as the single source of truth. Keep
# these values centralized so routes, status calculation, and future settings
# work all reference one schedule.
ATTENDANCE_TIMEZONE = os.getenv("ATTENDANCE_TIMEZONE", "Asia/Manila")
ATTENDANCE_MORNING_OPEN = os.getenv("ATTENDANCE_MORNING_OPEN", "07:00")
ATTENDANCE_LATE_AFTER = os.getenv("ATTENDANCE_LATE_AFTER", "08:00")
ATTENDANCE_MORNING_OUT_OPEN = os.getenv("ATTENDANCE_MORNING_OUT_OPEN", "12:00")
ATTENDANCE_AFTERNOON_IN_OPEN = os.getenv("ATTENDANCE_AFTERNOON_IN_OPEN", "13:00")
ATTENDANCE_REGULAR_HOURS = float(os.getenv("ATTENDANCE_REGULAR_HOURS", "8"))
