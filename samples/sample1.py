class ParentClass:
    def __init__(self):
        self.field1 = 100
        self.field2 = "foo bar"

    def parent1_method1(self):
        return self.field1 + self.field2

    def parent1_method2(self):
        return self.field1

    def parent1_method3(self):
        return self.field2


class ChildClass1(ParentClass):
    def __init__(self):
        super().__init__()
        self.child_field_1 = True

    def child1_method1(self):
        return self.field1 if self.child_field_1 else None

    def child1_method2(self):
        return self.field2
