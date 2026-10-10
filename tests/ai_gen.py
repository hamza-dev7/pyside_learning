"""Simple gym management app (PySide6 + SQLite).

Run:  python gym_app.py
Data is stored in gym.db next to this file.
"""

import calendar
import sqlite3
import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIntValidator, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

DB_PATH = Path(__file__).with_name("gym.db")

# label shown to the user -> number of months
PLANS = {"1 month": 1, "3 months": 3, "6 months": 6, "12 months": 12}
PLAN_LABELS = {months: label for label, months in PLANS.items()}

STYLE = """
QLabel#homeTitle { font-size: 30px; font-weight: 700; }
QLabel#pageTitle { font-size: 20px; font-weight: 600; }
QLabel#hint { color: #8a8a8a; }
QPushButton { padding: 6px 14px; }
QPushButton#homeButton { font-size: 16px; padding: 16px; }
QPushButton#dangerButton { color: #ff5c5c; }
"""


def apply_dark_palette(app: QApplication):
    """Black colour scheme. Only colours change; widget shapes stay untouched."""
    app.setStyle("Fusion")  # the built-in style that fully respects a custom palette
    role = QPalette.ColorRole
    group = QPalette.ColorGroup

    colors = {
        role.Window: "#09010d",           # window / page background
        role.WindowText: "#c041ff",       # normal text
        role.Base: "#09010d",             # text boxes, table, dropdown lists
        role.AlternateBase: "#0e0114",
        role.Text: "#f2f2f2",
        role.PlaceholderText: "#634175",  # grey hint text in empty inputs
        role.Button: "#0e0114",           # button background
        role.ButtonText: "#c041ff",
        role.ToolTipBase: "#1a1a1a",
        role.ToolTipText: "#f2f2f2",
        role.BrightText: "#ff5c5c",
        role.Link: "#8ab4ff",
        role.Highlight: "#3a3a3a",        # selected / hovered list item
        role.HighlightedText: "#ffffff",
    }
    palette = QPalette()
    for color_role, hex_color in colors.items():
        palette.setColor(color_role, QColor(hex_color))
    # greyed-out (disabled) text, e.g. "Add membership" when a plan already exists
    for color_role in (role.WindowText, role.Text, role.ButtonText):
        palette.setColor(group.Disabled, color_role, QColor("#5c5c5c"))
    app.setPalette(palette)


# --------------------------------------------------------------------------
# Data layer
# --------------------------------------------------------------------------
def add_months(d: date, months: int) -> date:
    """Return d shifted forward by `months`, clamping the day (Jan 31 + 1 -> Feb 28)."""
    index = d.month - 1 + months
    year = d.year + index // 12
    month = index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class Database:
    def __init__(self, path: Path):
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

    def add_member(self, full_name: str, phone: str) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO members (full_name, phone) VALUES (?, ?)",
                (full_name, phone),
            )
        return cur.lastrowid

    def all_members(self):
        return self.conn.execute(
            "SELECT id, full_name FROM members ORDER BY id"
        ).fetchall()

    def get_member(self, member_id: int):
        return self.conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ).fetchone()

    def set_membership(self, member_id: int, months: int):
        start = date.today()
        end = add_months(start, months)
        with self.conn:
            self.conn.execute(
                "UPDATE members SET plan_months = ?, start_date = ?, end_date = ? "
                "WHERE id = ?",
                (months, start.isoformat(), end.isoformat(), member_id),
            )

    def cancel_membership(self, member_id: int):
        with self.conn:
            self.conn.execute(
                "UPDATE members SET plan_months = NULL, start_date = NULL, "
                "end_date = NULL WHERE id = ?",
                (member_id,),
            )

    def delete_member(self, member_id: int):
        with self.conn:
            self.conn.execute("DELETE FROM members WHERE id = ?", (member_id,))


def confirm(parent, title: str, text: str) -> bool:
    answer = QMessageBox.question(parent, title, text)
    return answer == QMessageBox.StandardButton.Yes


# --------------------------------------------------------------------------
# Member info widget (used by both the list -> info page and the search page)
# --------------------------------------------------------------------------
class MemberInfoWidget(QGroupBox):
    changed = Signal()      # membership was added / changed / cancelled
    deleted = Signal(int)   # member was deleted (emits the old id)

    def __init__(self, db: Database):
        super().__init__("Member info")
        self.db = db
        self.member_id = None

        self.id_label = QLabel()
        self.name_label = QLabel()
        self.phone_label = QLabel()
        self.plan_label = QLabel()
        self.start_label = QLabel()
        self.end_label = QLabel()
        self.status_label = QLabel()

        form = QFormLayout()
        form.addRow("ID:", self.id_label)
        form.addRow("Full name:", self.name_label)
        form.addRow("Phone:", self.phone_label)
        form.addRow("Membership:", self.plan_label)
        form.addRow("Started:", self.start_label)
        form.addRow("Expires:", self.end_label)
        form.addRow("Status:", self.status_label)

        self.add_btn = QPushButton("Add membership")
        self.change_btn = QPushButton("Change membership")
        self.cancel_btn = QPushButton("Cancel membership")
        self.delete_btn = QPushButton("Delete member")
        self.delete_btn.setObjectName("dangerButton")

        self.add_btn.clicked.connect(self.add_membership)
        self.change_btn.clicked.connect(self.change_membership)
        self.cancel_btn.clicked.connect(self.cancel_membership)
        self.delete_btn.clicked.connect(self.delete_member)

        membership_row = QHBoxLayout()
        membership_row.addWidget(self.add_btn)
        membership_row.addWidget(self.change_btn)
        membership_row.addWidget(self.cancel_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addLayout(membership_row)
        layout.addWidget(self.delete_btn)

    # -- display -----------------------------------------------------------
    def load(self, member_id: int) -> bool:
        """Show the member with this id. Returns False if it doesn't exist."""
        row = self.db.get_member(member_id)
        if row is None:
            self.member_id = None
            return False

        self.member_id = row["id"]
        self.id_label.setText(str(row["id"]))
        self.name_label.setText(row["full_name"])
        self.phone_label.setText(row["phone"] or "-")

        has_plan = row["plan_months"] is not None
        if has_plan:
            end = date.fromisoformat(row["end_date"])
            days_left = (end - date.today()).days
            self.plan_label.setText(PLAN_LABELS[row["plan_months"]])
            self.start_label.setText(row["start_date"])
            self.end_label.setText(row["end_date"])
            if days_left >= 0:
                self.status_label.setText(f"Active ({days_left} day(s) left)")
            else:
                self.status_label.setText("Expired")
        else:
            for label in (self.plan_label, self.start_label, self.end_label):
                label.setText("-")
            self.status_label.setText("No membership")

        self.add_btn.setEnabled(not has_plan)
        self.change_btn.setEnabled(has_plan)
        self.cancel_btn.setEnabled(has_plan)
        return True

    # -- actions -----------------------------------------------------------
    def _choose_plan(self, title: str, current_months=None):
        labels = list(PLANS)
        current = labels.index(PLAN_LABELS[current_months]) if current_months else 0
        label, ok = QInputDialog.getItem(
            self, title, "Choose a plan (starts today):", labels, current, False
        )
        return PLANS[label] if ok else None

    def add_membership(self):
        months = self._choose_plan("Add membership")
        if months is not None:
            self.db.set_membership(self.member_id, months)
            self.load(self.member_id)
            self.changed.emit()

    def change_membership(self):
        row = self.db.get_member(self.member_id)
        months = self._choose_plan("Change membership", row["plan_months"])
        if months is not None:
            self.db.set_membership(self.member_id, months)
            self.load(self.member_id)
            self.changed.emit()

    def cancel_membership(self):
        if confirm(self, "Cancel membership", "Cancel this member's membership?"):
            self.db.cancel_membership(self.member_id)
            self.load(self.member_id)
            self.changed.emit()

    def delete_member(self):
        name = self.name_label.text()
        if confirm(self, "Delete member", f"Permanently delete {name}?"):
            member_id = self.member_id
            self.db.delete_member(member_id)
            self.member_id = None
            self.deleted.emit(member_id)


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
class Page(QWidget):
    """Base page: header with a back button and a title, plus a body layout."""

    back = Signal()

    def __init__(self, title: str, back_text: str = "← Home"):
        super().__init__()
        outer = QVBoxLayout(self)

        header = QHBoxLayout()
        back_btn = QPushButton(back_text)
        back_btn.clicked.connect(lambda: self.back.emit())
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        header.addWidget(back_btn)
        header.addWidget(title_label, 1)
        outer.addLayout(header)

        self.body = QVBoxLayout()
        outer.addLayout(self.body, 1)

    def on_show(self):
        """Called every time the page becomes visible."""


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        title = QLabel("Gym Management")
        title.setObjectName("homeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.add_btn = QPushButton("Add a member")
        self.list_btn = QPushButton("Show all members")
        self.search_btn = QPushButton("Search for a member by ID")
        for btn in (self.add_btn, self.list_btn, self.search_btn):
            btn.setObjectName("homeButton")

        column = QVBoxLayout()
        column.addWidget(title)
        column.addSpacing(20)
        column.addWidget(self.add_btn)
        column.addWidget(self.list_btn)
        column.addWidget(self.search_btn)

        container = QWidget()
        container.setLayout(column)
        container.setMaximumWidth(380)

        outer = QHBoxLayout(self)
        outer.addStretch(1)
        outer.addWidget(container)
        outer.addStretch(1)


class AddMemberPage(Page):
    def __init__(self, db: Database):
        super().__init__("Add a member")
        self.db = db

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. John Smith")
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("optional")

        form = QFormLayout()
        form.addRow("Full name:", self.name_edit)
        form.addRow("Phone:", self.phone_edit)

        save_btn = QPushButton("Save member")
        save_btn.clicked.connect(self.save)
        self.name_edit.returnPressed.connect(self.save)
        self.phone_edit.returnPressed.connect(self.save)

        hint = QLabel("The ID is generated automatically. "
                      "You can add a membership afterwards from the member's info.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)

        self.body.addLayout(form)
        self.body.addWidget(save_btn)
        self.body.addWidget(hint)
        self.body.addStretch(1)

    def on_show(self):
        self.name_edit.clear()
        self.phone_edit.clear()
        self.name_edit.setFocus()

    def save(self):
        name = " ".join(self.name_edit.text().split())
        if not name:
            QMessageBox.warning(self, "Missing name", "Please enter the member's full name.")
            return
        member_id = self.db.add_member(name, self.phone_edit.text().strip())
        QMessageBox.information(
            self, "Member added", f"{name} was added with ID {member_id}."
        )
        self.back.emit()


class MembersListPage(Page):
    open_member = Signal(int)

    def __init__(self, db: Database):
        super().__init__("All members")
        self.db = db

        self.count_label = QLabel("From Editor")
        self.count_label.setObjectName("hint")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Full name", ""])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.body.addWidget(self.count_label)
        self.body.addWidget(self.table, 1)

    def on_show(self):
        rows = self.db.all_members()
        self.count_label.setText(f"{len(rows)} member(s)")
        self.table.setRowCount(len(rows))
        for r, member in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(member["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(member["full_name"]))
            btn = QPushButton("Member info")
            btn.clicked.connect(
                lambda _checked=False, mid=member["id"]: self.open_member.emit(mid)
            )
            self.table.setCellWidget(r, 2, btn)


class MemberInfoPage(Page):
    """Full-page member info, opened from the members list."""

    member_deleted = Signal()

    def __init__(self, db: Database):
        super().__init__("Member info", back_text="← Members")
        self.info = MemberInfoWidget(db)
        self.info.deleted.connect(lambda _id: self.member_deleted.emit())
        self.body.addWidget(self.info)
        self.body.addStretch(1)

    def open(self, member_id: int):
        self.info.load(member_id)


class SearchPage(Page):
    def __init__(self, db: Database):
        super().__init__("Search member by ID")
        self.db = db

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Member ID")
        self.id_edit.setValidator(QIntValidator(1, 2_000_000_000, self))
        self.id_edit.returnPressed.connect(self.search)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)

        row = QHBoxLayout()
        row.addWidget(self.id_edit, 1)
        row.addWidget(search_btn)

        self.message = QLabel()
        self.message.setObjectName("hint")

        self.info = MemberInfoWidget(db)
        self.info.deleted.connect(self._on_deleted)
        self.info.hide()

        self.body.addLayout(row)
        self.body.addWidget(self.message)
        self.body.addWidget(self.info)
        self.body.addStretch(1)

    def on_show(self):
        self.id_edit.clear()
        self.message.clear()
        self.info.hide()
        self.id_edit.setFocus()

    def search(self):
        text = self.id_edit.text().strip()
        if not text:
            self.message.setText("Enter a member ID.")
            self.info.hide()
            return
        member_id = int(text)
        if self.info.load(member_id):
            self.message.clear()
            self.info.show()
        else:
            self.info.hide()
            self.message.setText(f"No member found with ID {member_id}.")

    def _on_deleted(self, member_id: int):
        self.info.hide()
        self.message.setText(f"Member {member_id} was deleted.")


# --------------------------------------------------------------------------
# Main window
# --------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Management")
        self.resize(760, 540)

        self.db = Database(DB_PATH)

        self.home = HomePage()
        self.add_page = AddMemberPage(self.db)
        self.list_page = MembersListPage(self.db)
        self.search_page = SearchPage(self.db)
        self.info_page = MemberInfoPage(self.db)

        self.stack = QStackedWidget()
        for page in (self.home, self.add_page, self.list_page,
                     self.search_page, self.info_page):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        # home buttons
        self.home.add_btn.clicked.connect(lambda: self.show_page(self.add_page))
        self.home.list_btn.clicked.connect(lambda: self.show_page(self.list_page))
        self.home.search_btn.clicked.connect(lambda: self.show_page(self.search_page))

        # back buttons
        for page in (self.add_page, self.list_page, self.search_page):
            page.back.connect(lambda: self.show_page(self.home))
        self.info_page.back.connect(lambda: self.show_page(self.list_page))

        # list -> info
        self.list_page.open_member.connect(self.open_member_info)
        self.info_page.member_deleted.connect(lambda: self.show_page(self.list_page))

    def show_page(self, page):
        self.stack.setCurrentWidget(page)
        page.on_show()

    def open_member_info(self, member_id: int):
        self.info_page.open(member_id)
        self.stack.setCurrentWidget(self.info_page)


def main():
    app = QApplication(sys.argv)
    apply_dark_palette(app)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
