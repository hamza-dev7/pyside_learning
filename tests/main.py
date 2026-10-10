"""Gym management app - Qt Quick (QML) front-end, Python back-end.

Run:   python main.py
Data:  gym.db next to this file. It uses the same table layout as the
       widgets version, so you can copy your old gym.db here to keep members.
"""

import calendar
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gym.db"
QML_MAIN = BASE_DIR / "qml" / "Main.qml"

PLANS = [1, 3, 6, 12]  # the available memberships, in months

# Design tokens. QML reads these as `theme.accent`, `theme.surface`, ...
# Change a colour here and the whole app follows.
THEME = {
    "bg": "#0a0a0b",           # window background
    "surface": "#121214",      # cards, inputs, list
    "surfaceHi": "#1b1b1f",    # hovered surface
    "border": "#2b2b31",
    "borderHi": "#4a4a54",
    "scroll": "#3a3a42",
    "text": "#f4f4f5",
    "muted": "#8b8b95",
    "accent": "#c6ff3d",       # electric lime
    "accentHover": "#d6ff6b",
    "accentPress": "#a8de2c",
    "onAccent": "#0a0a0b",     # text drawn on top of the accent colour
    "danger": "#ff4d5e",
    "dangerPress": "#d93a4a",
}


# --------------------------------------------------------------------------
# Data layer (plain Python + SQLite, no Qt)
# --------------------------------------------------------------------------
def add_months(d, months):
    """d shifted forward by `months`, clamping the day (Jan 31 + 1 -> Feb 28)."""
    index = d.month - 1 + months
    year = d.year + index // 12
    month = index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def plan_label(months):
    return f"{months} month" if months == 1 else f"{months} months"


def describe_member(row):
    """Turn a database row into a plain dict that QML can read."""
    months = row["plan_months"] or 0
    info = {
        "id": row["id"],
        "fullName": row["full_name"],
        "phone": row["phone"] or "",
        "hasPlan": months > 0,
        "planMonths": months,
        "planLabel": "",
        "startDate": "",
        "endDate": "",
        "daysLeft": 0,
        "status": "none",
        "statusText": "No membership",
    }
    if months:
        end = date.fromisoformat(row["end_date"])
        days_left = (end - date.today()).days
        info.update(
            planLabel=plan_label(months),
            startDate=row["start_date"],
            endDate=row["end_date"],
            daysLeft=days_left,
        )
        if days_left >= 0:
            unit = "day" if days_left == 1 else "days"
            info.update(status="active", statusText=f"Active · {days_left} {unit} left")
        else:
            info.update(status="expired", statusText="Expired")
    return info


class GymDatabase:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name   TEXT NOT NULL,
                    phone       TEXT,
                    plan_months INTEGER,
                    start_date  TEXT,
                    end_date    TEXT
                )
                """
            )

    def list_members(self):
        rows = self.conn.execute(
            "SELECT id, full_name FROM members ORDER BY id"
        ).fetchall()
        return [{"id": r["id"], "fullName": r["full_name"]} for r in rows]

    def get_member(self, member_id):
        row = self.conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()
        return describe_member(row) if row else None

    def add_member(self, full_name, phone):
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO members (full_name, phone) VALUES (?, ?)",
                (full_name, phone),
            )
        return cur.lastrowid

    def set_membership(self, member_id, months):
        start = date.today()
        end = add_months(start, months)
        with self.conn:
            self.conn.execute(
                "UPDATE members SET plan_months = ?, start_date = ?, end_date = ? "
                "WHERE id = ?",
                (months, start.isoformat(), end.isoformat(), member_id),
            )

    def cancel_membership(self, member_id):
        with self.conn:
            self.conn.execute(
                "UPDATE members SET plan_months = NULL, start_date = NULL, "
                "end_date = NULL WHERE id = ?",
                (member_id,),
            )

    def delete_member(self, member_id):
        with self.conn:
            self.conn.execute("DELETE FROM members WHERE id = ?", (member_id,))


# --------------------------------------------------------------------------
# The object QML talks to
# --------------------------------------------------------------------------
class Backend(QObject):
    """Everything QML is allowed to use.

    Method names are camelCase on purpose: that is the QML convention, and QML
    calls them by exactly these names (backend.addMember(...)).
    """

    # Emitted after every change. QML re-reads whatever it is showing.
    updated = Signal()

    def __init__(self, db):
        super().__init__()
        self._db = db

    # -- properties (read from QML like `backend.members`) -------------------
    @Property("QVariantList", constant=True)
    def plans(self):
        return PLANS

    @Property("QVariantList", notify=updated)
    def members(self):
        return self._db.list_members()

    # -- slots (called from QML like `backend.addMember(name, phone)`) -------
    @Slot(int, result="QVariantMap")
    def getMember(self, member_id):
        return self._db.get_member(member_id) or {}

    @Slot(str, str, result=int)
    def addMember(self, full_name, phone):
        name = " ".join(full_name.split())
        if not name:
            return -1
        new_id = self._db.add_member(name, phone.strip())
        self.updated.emit()
        return new_id

    @Slot(int, int)
    def setMembership(self, member_id, months):
        if months in PLANS:
            self._db.set_membership(member_id, months)
            self.updated.emit()

    @Slot(int)
    def cancelMembership(self, member_id):
        self._db.cancel_membership(member_id)
        self.updated.emit()

    @Slot(int)
    def deleteMember(self, member_id):
        self._db.delete_member(member_id)
        self.updated.emit()


# --------------------------------------------------------------------------
def main():
    # "Basic" is the Qt Quick Controls style that lets us fully restyle
    # buttons and text fields. Must be set before the app is created.
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend(GymDatabase(DB_PATH))
    context = engine.rootContext()
    context.setContextProperty("backend", backend)  # data + actions
    context.setContextProperty("theme", THEME)      # colours

    engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
    if not engine.rootObjects():
        sys.exit(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
