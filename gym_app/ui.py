import sys
from calendar import firstweekday
from mimetypes import init

import system
from data import GYM_MEM_FILE, MEMBERSHIP_DICT_FILE, load_json, save_json
from PySide6 import QtCore, QtGui, QtWidgets


class MyGym:
    def __init__(self):
        self.gym = system.Gym()
        # self.member = system.Member

    def load_gym_members(self):
        raw_data = load_json(GYM_MEM_FILE)
        for key, value in raw_data.items():
            self.gym.members[key] = system.Member.from_dict(value)

    @QtCore.Slot()
    def add_member(self, first_name, last_name):
        member = system.Member(first_name, last_name)
        self.gym.add_member(member)

class MemberListWidget(QtWidgets.QWidget):
    def __init__(self, member: system.Member):
        super().__init__()
        self.member = member

        self.id_label = QtWidgets.QLabel(self.member.id)
        self.name_label = QtWidgets.QLabel(f"{self.member.first_name} {self.member.last_name}")
        self.membership_label = QtWidgets.QLabel(self.member.membership if self.member.membership else "No membership")

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Full Name:", self.name_label)
        self.form_layout.addRow("Membership:", self.membership_label)

        self.add_membership_btn = QtWidgets.QPushButton("Add Membership")
        self.change_membership_btn = QtWidgets.QPushButton("Change Membership")
        self.remove_membership_btn = QtWidgets.QPushButton("Remove Membership")
        self.btns_layout = QtWidgets.QHBoxLayout()
        self.btns_layout.addWidget(self.add_membership_btn)
        self.btns_layout.addWidget(self.change_membership_btn)
        self.btns_layout.addWidget(self.remove_membership_btn)

        self.remove_member_btn = QtWidgets.QPushButton("Remove Member")

        self.box_layout = QtWidgets.QVBoxLayout(self)
        self.box_layout.addLayout(self.form_layout)
        self.box_layout.addLayout(self.btns_layout)
        self.box_layout.addWidget(self.remove_member_btn)

        self.box = QtWidgets.QGroupBox("Member Info")
        self.box.setLayout(self.box_layout)
        self.outer_layout = QtWidgets.QVBoxLayout(self)
        self.outer_layout.addWidget(self.box)
        self.outer_layout.addStretch()
        self.setLayout(self.outer_layout)



class Page(QtWidgets.QWidget):
    """Base page: header with a back button and a title, plus a body layout."""

    back = QtCore.Signal()

    def __init__(self, title: str, back_text: str = "← Home"):
        super().__init__()
        outer = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton(back_text)
        back_btn.clicked.connect(lambda: self.back.emit())
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("pageTitle")
        header.addWidget(back_btn)
        header.addWidget(title_label, 1)
        outer.addLayout(header)

        self.body = QtWidgets.QVBoxLayout()
        outer.addLayout(self.body, 1)


class AddMemberWindow(Page):
    def __init__(self, my_gym: MyGym):
        super().__init__("Add Member")
        self.my_gym = my_gym

        self.setWindowTitle("Add Member")

        self.fname_input = QtWidgets.QLineEdit()
        self.lname_input = QtWidgets.QLineEdit()

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow("First Name:", self.fname_input)
        self.form_layout.addRow("Last Name:", self.lname_input)

        self.save_btn = QtWidgets.QPushButton("Add Member")
        self.save_btn.clicked.connect(self.save)

        self.save_msg = QtWidgets.QLabel()

        self.body.addLayout(self.form_layout)
        self.body.addWidget(self.save_btn)
        self.body.addWidget(self.save_msg)
        self.body.addStretch()

    def save(self):
        first_name = self.fname_input.text()
        last_name = self.lname_input.text()
        self.my_gym.add_member(first_name, last_name)
        member_id = list(self.my_gym.gym.members.keys())[-1]
        self.save_msg.setText(f"Member {first_name} {last_name} with ID:{member_id} added successfully!")
        self.fname_input.clear()
        self.lname_input.clear()

class MembersListWindow(Page):
    def __init__(self, my_gym: MyGym):
        super().__init__("Members List")
        self.my_gym = my_gym
        self.members = self.my_gym.gym.members

        self.setWindowTitle("Members Show")
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Info"])
        self.table.setRowCount(len(self.members))
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)


        for i, (member_id, member) in enumerate(self.members.items()):
            full_name = f"{member.first_name} {member.last_name}"
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(member_id))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(full_name))
            info_btn = QtWidgets.QPushButton("Show Info")
            self.table.setCellWidget(i, 2, info_btn)

        self.body.addWidget(self.table)

class MemberInfoWindow(Page):
    def __init__(self, member: system.Member):
        super().__init__(f"Member Info - {member.first_name} {member.last_name}")
        self.member = member

        self.member_info_widget = MemberListWidget(self.member)
        self.body.addWidget(self.member_info_widget)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Gym Management")


        self.title = QtWidgets.QLabel("      Gym Fitness      ")
        self.add = QtWidgets.QPushButton("Add Member")
        self.members = QtWidgets.QPushButton("Show Members")
        self.id_search = QtWidgets.QPushButton("Id Search Member")

        column = QtWidgets.QVBoxLayout()
        column.addWidget(self.title)
        column.addSpacing(20)
        column.addWidget(self.add)
        column.addWidget(self.members)
        column.addWidget(self.id_search)

        container = QtWidgets.QWidget()
        container.setLayout(column)
        container.setMaximumWidth(380)

        outer = QtWidgets.QHBoxLayout(self)
        outer.addStretch(1)
        outer.addWidget(container)
        outer.addStretch(1)

        self.setStyleSheet("""
            QLabel {
                font-size: 30px;
            }
            QPushButton{
                font-size: 16px;
                padding: 16px;
            }
        """)


app = QtWidgets.QApplication(sys.argv)
my_gym = MyGym()
my_gym.load_gym_members()
mems = tuple(enumerate(my_gym.gym.members.items()))
print(mems)
window = MemberInfoWindow(mems[0][1][1])
window.show()
app.exec()
optimized_data = {member.id: member.to_dict() for member in my_gym.gym.members.values()}
save_json(GYM_MEM_FILE, optimized_data)
