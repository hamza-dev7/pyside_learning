import sys

import system
from data import GYM_MEM_FILE, load_json, save_json
from PySide6 import QtCore, QtWidgets


class MyGym:
    def __init__(self):
        self.gym = system.Gym()
        self.membership = system.Gym.Membership()
        # self.member = system.Member

    def load_gym_members(self):
        raw_data = load_json(GYM_MEM_FILE)
        for key, value in raw_data.items():
            self.gym.members[key] = system.Member.from_dict(value)

    @QtCore.Slot()
    def add_member(self, parent: QtWidgets.QWidget, first_name, last_name):
        member = system.Member(first_name, last_name)
        try:
            self.gym.add_member(member)
            optimized_data = {member.id: member.to_dict() for member in self.gym.members.values()}
            save_json(GYM_MEM_FILE, optimized_data)
        except system.DuplicateMemberError as e:
            QtWidgets.QMessageBox.warning(parent, "Duplicate Member Error", str(e))

    @QtCore.Slot()
    def add_membership(self, parent: QtWidgets.QWidget, member: system.Member, membership_type):
        try:
            self.membership.add_membership(member, membership_type)
            optimized_data = {member.id: member.to_dict() for member in self.gym.members.values()}
            save_json(GYM_MEM_FILE, optimized_data)
        except system.MembershipAlreadyExistsError as e:
            QtWidgets.QMessageBox.warning(parent, "Membership Error", str(e))


    @QtCore.Slot()
    def change_membership(self, parent: QtWidgets.QWidget, member: system.Member, new_membership_type):
        try:
            self.membership.remove_membership(member, member.membership)
            self.membership.add_membership(member, new_membership_type)
            optimized_data = {member.id: member.to_dict() for member in self.gym.members.values()}
            save_json(GYM_MEM_FILE, optimized_data)
        except system.NoMembershipExistsError as e:
            QtWidgets.QMessageBox.warning(parent, "Membership Error", str(e))

    @QtCore.Slot()
    def cancel_membership(self, parent: QtWidgets.QWidget, member: system.Member):
        try:
            self.membership.remove_membership(member, member.membership)
            optimized_data = {member.id: member.to_dict() for member in self.gym.members.values()}
            save_json(GYM_MEM_FILE, optimized_data)
        except system.NoMembershipExistsError as e:
            QtWidgets.QMessageBox.warning(parent, "Membership Error", str(e))

    @QtCore.Slot()
    def remove_member(self, member: system.Member):
        self.gym.remove_member(member)
        optimized_data = {member.id: member.to_dict() for member in self.gym.members.values()}
        save_json(GYM_MEM_FILE, optimized_data)

class MemberInfoWidget(QtWidgets.QWidget):

    back = QtCore.Signal()

    def __init__(self, my_gym: MyGym, member: system.Member):
        super().__init__()
        self.my_gym = my_gym
        self.member = member

        self.id_label = QtWidgets.QLabel(self.member.id)
        self.name_label = QtWidgets.QLabel(f"{self.member.first_name} {self.member.last_name}")
        self.membership_label = QtWidgets.QLabel(system.SUBSCRIPTION_TYPES[self.member.membership] if self.member.membership else "No membership")
        self.membership_end_label = QtWidgets.QLabel(self.member.membership_end_time if self.member.membership_end_time else "N/A")

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Full Name:", self.name_label)
        self.form_layout.addRow("Membership:", self.membership_label)
        self.form_layout.addRow("Membership End:", self.membership_end_label)

        self.add_membership_btn = QtWidgets.QPushButton("Add Membership")
        self.add_membership_btn.clicked.connect(self.add_ship)

        self.change_membership_btn = QtWidgets.QPushButton("Change Membership")
        self.change_membership_btn.clicked.connect(self.change_ship)

        self.remove_membership_btn = QtWidgets.QPushButton("Remove Membership")
        self.remove_membership_btn.clicked.connect(self.cancel_ship)
        self.btns_layout = QtWidgets.QHBoxLayout()
        self.btns_layout.addWidget(self.add_membership_btn)
        self.btns_layout.addWidget(self.change_membership_btn)
        self.btns_layout.addWidget(self.remove_membership_btn)

        self.remove_member_btn = QtWidgets.QPushButton("Remove Member")
        self.remove_member_btn.setStyleSheet("color: red;")
        self.remove_member_btn.clicked.connect(self.remove_mem)

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

    def get_choice(self):
        choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Select Membership Type", "Membership Type:",
            list(system.SUBSCRIPTION_TYPES.values()), 0, False
        )
        if ok and choice:
            for key, value in system.SUBSCRIPTION_TYPES.items():
                if value == choice:
                    return key
        return None

    def confirm_removal(self, title, text ):
        reply = QtWidgets.QMessageBox.question(self, title, text)
        return reply == QtWidgets.QMessageBox.StandardButton.Yes

    def add_ship(self):
        choice = self.get_choice()
        if choice:
            self.my_gym.add_membership(self, self.member, choice)
            self.refresh()
            # print(self.member.membership)
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "No membership type selected.")

    def change_ship(self):
        choice = self.get_choice()
        if choice:
            self.my_gym.change_membership(self, self.member, choice)
            self.refresh()
            # print(self.member.membership)
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "No membership type selected.")

    def cancel_ship(self):
        approval = self.confirm_removal("Confirm Cancellation", f"Are you sure you want to cancel {self.member.first_name} {self.member.last_name}'s membership?")
        if approval:
            self.my_gym.cancel_membership(self, self.member)
            self.refresh()

    def remove_mem(self):
        approval = self.confirm_removal("Confirm Removal", f"Are you sure you want to remove {self.member.first_name} {self.member.last_name}?")
        if approval:
            self.my_gym.remove_member(self.member)
            self.back.emit()

    def refresh(self):
        self.membership_label.setText(system.SUBSCRIPTION_TYPES[self.member.membership] if self.member.membership else "No membership")
        self.membership_end_label.setText(self.member.membership_end_time if self.member.membership_end_time else "N/A")


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


class AddMemberPage(Page):
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
        self.my_gym.add_member(self, first_name, last_name)
        member_id = list(self.my_gym.gym.members.keys())[-1]
        self.save_msg.setText(f"Member {first_name} {last_name} with ID:{member_id} added successfully!")
        self.fname_input.clear()
        self.lname_input.clear()

class MembersListPage(Page):

    show_info = QtCore.Signal(system.Member)

    def __init__(self, my_gym: MyGym):
        super().__init__("Members List")
        self.my_gym = my_gym
        self.members = self.my_gym.gym.members

        self.setWindowTitle("Members Show")
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Info"])
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.body.addWidget(self.table)
        self.refresh()

    def refresh(self):
        self.members = self.my_gym.gym.members
        self.table.setRowCount(len(self.members))
        for i, (member_id, member) in enumerate(self.members.items()):
            full_name = f"{member.first_name} {member.last_name}"
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(member_id))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(full_name))
            info_btn = QtWidgets.QPushButton("Show Info")
            info_btn.clicked.connect(lambda _, m=member: self.show_info.emit(m))
            self.table.setCellWidget(i, 2, info_btn)

class MemberInfoPage(Page):
    def __init__(self, my_gym: MyGym, member: system.Member):
        super().__init__(f"Member Info - {member.first_name} {member.last_name}", "← members list")
        self.my_gym = my_gym
        self.member = member

        self.member_info_widget = MemberInfoWidget(self.my_gym, self.member)
        self.body.addWidget(self.member_info_widget)
        self.member_info_widget.back.connect(lambda: self.back.emit())

class HomePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gym Management")
        self.setStyleSheet("""
            QLabel {
                font-size: 30px;
            }
            QPushButton{
                font-size: 16px;
                padding: 16px;
            }
        """)

        self.title = QtWidgets.QLabel("      Gym Fitness      ")
        self.add_btn = QtWidgets.QPushButton("Add Member")
        self.list_btn = QtWidgets.QPushButton("Show Members")
        self.search_btn = QtWidgets.QPushButton("Id Search Member")

        column = QtWidgets.QVBoxLayout()
        column.addWidget(self.title)
        column.addSpacing(20)
        column.addWidget(self.add_btn)
        column.addWidget(self.list_btn)
        column.addWidget(self.search_btn)

        container = QtWidgets.QWidget()
        container.setLayout(column)
        container.setMaximumWidth(380)

        outer = QtWidgets.QHBoxLayout(self)
        outer.addStretch(1)
        outer.addWidget(container)
        outer.addStretch(1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, my_gym: MyGym) -> None:
        super().__init__()
        self.my_gym = my_gym

        self.setWindowTitle("Gym Management - Home")

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomePage()
        self.add_page = AddMemberPage(self.my_gym)
        self.list_page = MembersListPage(self.my_gym)
        self.info_page = None

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.list_page)

        self.home.add_btn.clicked.connect(self.open_add_page)
        self.home.list_btn.clicked.connect(self.open_members_list)
        self.home.search_btn.clicked.connect(self.open_id_search)

        # in MainWindow.__init__, after creating the pages
        self.add_page.back.connect(lambda: self.stack.setCurrentWidget(self.home))
        self.list_page.back.connect(lambda: self.stack.setCurrentWidget(self.home))
        self.list_page.show_info.connect(self.open_info_page)

    def open_add_page(self):
        self.stack.setCurrentWidget(self.add_page)

    def open_members_list(self):
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)

    def open_info_page(self, member: system.Member):
        if self.info_page is not None:
            self.stack.removeWidget(self.info_page)
            self.info_page.deleteLater()
        self.info_page = MemberInfoPage(self.my_gym, member)
        self.stack.addWidget(self.info_page)
        self.info_page.back.connect(self.open_members_list)
        self.stack.setCurrentWidget(self.info_page)

    def open_id_search(self):
        print("Coming soon")


def main():
    app = QtWidgets.QApplication(sys.argv)
    my_gym = MyGym()
    my_gym.load_gym_members()
    window = MainWindow(my_gym)  # Show the first member's info
    window.show()
    app.exec()
    optimized_data = {member.id: member.to_dict() for member in my_gym.gym.members.values()}
    save_json(GYM_MEM_FILE, optimized_data)

if __name__ == "__main__":
    main()
