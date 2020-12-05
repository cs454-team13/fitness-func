class ParentClass:
    def __init__(self):
        self.field1 = 100
        self.field2 = "foo bar"


class ChildClass1(ParentClass):
    def __init__(self):
        super()

    def child1_method1():
        return self.field1

    def child1_method2():
        return self.field2
