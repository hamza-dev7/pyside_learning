import os
from re import M
import time

import system
from data import GYM_MEM_FILE, MEMBERSHIP_DICT_FILE, load_json, save_json


class UI:
    def __init__(self):
        self.gym = system.Gym()
        self.membership = system.Gym.Membership()
        self.member = system.Member


    @staticmethod
    def decoration1():
        print("=" * 32)
    @staticmethod
    def decoration2():
        print("-" * 32)

    @staticmethod
    def input_decoration():
        print("-" * 4, end="")

    @staticmethod
    def clear():
        os.system("clear")



    def ui_add_member(self):
        try:
            self.decoration1()
            self.input_decoration()
            first_name = input("Enter first name: ")
            self.input_decoration()
            last_name = input("Enter last name: ")
            self.decoration1()

            existing_member = self.gym.name_search(first_name, last_name)
            if existing_member:
                member = existing_member
            else:
                member = self.member(first_name, last_name)
            self.gym.add_member(member)
        except system.GymError as e:
            print(e)
            return

    def ui_remove_member(self, member:system.Member):
        try:
            self.gym.remove_member(member)
        except system.GymError as e:
            print(e)
            return

    def show_memberships(self):
        self.decoration1()
        self.decoration2()
        print("1- 1 month \n2- 3 months \n3- 6 months \n4- 12 months")
        self.decoration2()
        self.decoration1()

    def ui_add_membership(self, member:system.Member):
        try:
            self.show_memberships()

            self.decoration1()
            self.input_decoration()
            membership_type = input("Enter membership type: ")
            self.decoration1()

            self.membership.add_membership(member, membership_type)
            print("membership added successfuly")
        except system.GymError as e:
            print(e)
            return

    def ui_change_membership(self, member:system.Member):
        try:
            self.show_memberships()

            self.decoration1()
            self.input_decoration()
            membership_type = input("Enter membership type: ")
            self.decoration1()

            self.membership.remove_membership(member, member.membership)
            self.membership.add_membership(member, membership_type)
            print("membership changed successfuly")
        except system.GymError as e:
            print(e)
            return

    def ui_membership_expiry(self):
        try:
            for members in self.membership.membership_dict.values():
                for member_id in members:
                    member = self.gym.id_search(member_id)
                    self.membership.check_membership_expiry(member)

        except system.GymError as e:
            print(e)
            return

    def show_mem_info(self, member:system.Member):
        while True:
            self.clear()

            self.decoration1()
            print(f"Name: {member.first_name} {member.last_name}")
            print(f"ID: {member.id}")
            print(f"Membership: {system.SUBSCRIPTION_TYPES[member.membership] if not member.membership is None else 'None'}")
            self.decoration1()

            self.decoration2()
            print("1-Add membership \n2-Change membership \n3-Remove member \n4-Back")
            self.decoration2()

            self.decoration1()
            choice = input("Enter your choice: ")
            if choice == "1":
                self.ui_add_membership(member)
                time.sleep(1)
                continue
            elif choice == "2":
                self.ui_change_membership(member)
                time.sleep(1)
                continue
            elif choice == "3":
                self.ui_remove_member(member)
                time.sleep(1)
                break
            elif choice == "4":
                break

    def show_all_members(self):
        while True:
            self.clear()
            if not self.gym.members:
                self.decoration2()
                print("No registered members")
                self.decoration2()
                choice = input("Enter any key to return: ")
                if choice:
                    break
            else:
                for member in self.gym.members.values():
                    self.decoration1()
                    print(f"Name: {member.first_name} {member.last_name}")
                    print(f"ID: {member.id}")
                self.decoration1()
                self.decoration2()
                print("1-id search \n2-Back")
                self.decoration2()
                self.decoration1()
                choice = input("Enter your choice: ")
                if choice == "1":
                    self.ui_id_search()
                    continue
                elif choice == "2":
                    break

    def ui_id_search(self):
        try:
            self.decoration1()
            member_id = input("Enter member id: ")
            member = self.gym.id_search(member_id)
            self.show_mem_info(member)
        except system.GymError as e:
            print(e)
            return





ui = UI()
def load_membership_dict():
    raw_data = load_json(MEMBERSHIP_DICT_FILE)
    for key, value in raw_data.items():
        ui.membership.membership_dict[key] = value

def load_gym_members():
    raw_data = load_json(GYM_MEM_FILE)
    for key, value in raw_data.items():
        ui.gym.members[key] = ui.member.from_dict(value)
while True:
    load_gym_members()
    load_membership_dict()

    ui.clear()
    ui.ui_membership_expiry()

    UI.decoration1()
    UI.decoration2()
    print("1-Add member \n2-show all members \n3-Search member \n4-Exit")
    UI.decoration2()
    UI.decoration1()

    choice = input("Enter your choice: ")
    if choice == "1":
        ui.ui_add_member()
        time.sleep(1)
        continue
    elif choice == "2":
        ui.show_all_members()
        continue
    elif choice == "3":
        ui.ui_id_search()
        continue
    elif choice == "4":
        optimized_data = {member.id: member.to_dict() for member in ui.gym.members.values()}
        save_json(GYM_MEM_FILE, optimized_data)
        save_json(MEMBERSHIP_DICT_FILE, ui.membership.membership_dict)
        break
    else:
        print("Invalid choice")
        continue
