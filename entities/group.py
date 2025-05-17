class Group:
    def __init__(self, group_number):
        self.members = []
        self.group_number = group_number
        self.aggression = 0

    def add_member(self, animal):
        if animal not in self.members:
            self.members.append(animal)
            self.update_aggression_level()

    def remove_member(self, animal):
        if animal in self.members:
            self.members.remove(animal)
            self.update_aggression_level()

    def update_aggression_level(self):
        group_size = len(self.members)
        if group_size > 5:
            self.aggression = 1 
        else:
            self.aggression = 0

    def get_group_size(self):
        return len(self.members)
    
    def split(self):
        mid = len(self.members) // 2
        members1 = self.members[:mid]
        members2 = self.members[mid:]

        new_group = Group(self.group_type)

        for member in members2:
            new_group.add_member(member)
            member.group = new_group

        self.members = members1
        for member in self.members:
            member.group = self

        self.update_aggression_level()
        new_group.update_aggression_level()
