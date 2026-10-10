import datetime
import random

TIMEZONE = datetime.timezone.utc
SUBSCRIPTION_TYPES = {
    "1": "1 month",
    "2": "3 months",
    "3": "6 months",
    "4": "12 months"
}

class GymError(Exception):
    pass

class MemberNotFoundError(GymError):
    def __init__(self, member_id):
        super().__init__(f"Member '{member_id}' does not exist")

class DuplicateMemberError(GymError):
    def __init__(self, member_id):
        super().__init__(f"Member '{member_id}' does already exist")

class WrongDataError(GymError):
    def __init__(self):
        super().__init__("Wrong input data")


class Member:
    def __init__(self, first_name, last_name, id=None, membership=None, membership_end_time:str | None = None):
        self.first_name = first_name
        self.last_name = last_name
        self.id = id if id is not None else f"{random.randint(0, 999):03d}"
        self.membership = membership
        self.membership_end_time = membership_end_time

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)




class Gym:
    def __init__(self):
        self.members:dict[str, Member] = {}

    def add_member(self, member:Member):
        if member.id in self.members:
            raise DuplicateMemberError(member.id)
        elif (not isinstance(member.first_name, str) or not member.first_name.strip()
                or not member.first_name.replace(" ", "").isalpha()
                or not isinstance(member.last_name, str) or not member.last_name.strip()
                or not member.last_name.replace(" ", "").isalpha()):
            raise WrongDataError()
        else:
            self.members[member.id] = member
            print(f"{member.id} added successfuly")

    def remove_member(self, member:Member):
            self.members.pop(member.id)
            print(f"{member.id} removed successfuly")

    def id_search(self, member_id):
        if member_id not in self.members:
            raise MemberNotFoundError(member_id)
        else:
            return self.members[member_id]

    def name_search(self, first_name, last_name):
        for member in self.members.values():
            if member.first_name.strip() == first_name.strip() and member.last_name.strip() == last_name.strip():
                return member


    class Membership:
        def __init__(self):
            self.membership_dict:dict[str, list[str]] = {
                                    "1": [], # 1 month
                                    "2": [], # 3 months
                                    "3": [], # 6 months
                                    "4": []  # 12 months
                                        }

        def add_membership(self,member:Member, membership_type):
            self.membership_dict[membership_type].append(member.id)
            member.membership = membership_type
            if membership_type == "1":
                member.membership_end_time = (datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            elif membership_type == "2":
                member.membership_end_time = (datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=90)).strftime('%Y-%m-%d')
            elif membership_type == "3":
                member.membership_end_time = (datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=180)).strftime('%Y-%m-%d')
            elif membership_type == "4":
                member.membership_end_time = (datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=365)).strftime('%Y-%m-%d')

        def remove_membership(self,member:Member, membership_type):
            self.membership_dict[membership_type].remove(member.id)
            member.membership = None
            member.membership_end_time = None

        def check_membership_expiry(self, member:Member):
            if member.membership_end_time is None:
                return
            expiry_time: datetime.date = datetime.datetime.strptime(member.membership_end_time, '%Y-%m-%d').date()  # noqa: DTZ007
            if datetime.datetime.now(tz=TIMEZONE).date() > expiry_time:
                self.remove_membership(member, member.membership)
                print(f"membership expired for {member.first_name} {member.last_name}")
