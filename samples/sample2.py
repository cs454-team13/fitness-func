from .sample1 import ParentClass


class AnotherChildClass(ParentClass):
    def child_method1(self):
        """child_method1 of AnotherChildClass"""
        print(self.field1)
        print(self.field2)

    def child_method_another(self):
        """Method that accesses nothing"""
        print("Hello, world!")
