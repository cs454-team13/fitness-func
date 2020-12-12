import ast
import typing
import pprint
import itertools

import astpretty
import astroid.nodes
import astroid.node_classes
from pylint.pyreverse import inspector

import astroid.helpers


def compute_tcc(cls: astroid.nodes.ClassDef) -> int:
    """Computes the TCC of a class."""
    # for base_class in cls.bases:
    #     print(f"{cls.name} has parent class {base_class.name}")
    # for attr_name in cls.instance_attrs:
    #     print(f"{cls.name} has instance attribute {attr_name}")

    # Mapping of (method name) -> (instance attributes accessed)
    method_to_attrs_accessed: typing.Dict[str, typing.Set[str]] = {}
    for method in cls.mymethods():
        # print(f"{cls.name} has method {method.name}()")
        # pprint.pprint(list(method.get_children()))
        finder = AstSelfFinder()
        finder.visit(method)
        # print(f"  Method {method.name}() accesses instance attributes: {', '.join(finder.attr_names_accessed)}")
        method_to_attrs_accessed[method.name] = set(finder.attr_names_accessed)

    k = len(method_to_attrs_accessed)
    assert k > 1, f"The class must have at least 2 methods ({cls.name} only has {k})"

    # Contains methods that access a common attribute, i.e CAU
    cau_methods: typing.Set[typing.Tuple[str, str]] = set()
    for method1, method2 in itertools.combinations(method_to_attrs_accessed, 2):
        assert method1 < method2, "Not sorted!"
        if method_to_attrs_accessed[method1] & method_to_attrs_accessed[method2]:
            cau_methods.add((method1, method2))
    return len(cau_methods) / (k * (k - 1) / 2)

def compute_lscc(cls) -> int :
    methodlist=[]
    for method_name in cls.mymethods():
        methodlist.append(method_name)
    l = len(cls.instance_attrs)
    k = len(methodlist)-1
    if (l==0 and k==0):
        print("input error : there is no attribue and method")
    elif (l==0) and (k>1):
        return 0
    elif (l>0 and k==0) or k==1:
        return 1
    else:
        sum=0
        for attr_name in cls.instance_attrs:
            count = 0
            for method_name in cls.mymethods():
                if method_name.name == "__init__" :
                    pass
                else :
                    finder = AstSelfFinder()
                    finder.visit(method_name)
                    if attr_name in finder.attr_names_accessed:
                        count = count + 1
            sum = sum + (count*(count-1))
        sum = sum / (l*k*(k-1))
        return sum



class AstSelfFinder:
    """Custom AST walker for astroid
    Needed because we don't have an equivalent of ast.walk() or ast.NodeVisitor
    in astroid.
    """

    def __init__(self):
        self.attr_names_accessed = set()

    def visit(self, node: astroid.node_classes.NodeNG):
        if isinstance(node, (astroid.nodes.Attribute, astroid.nodes.AssignAttr)):
            # Detect self.attr_name (read) or self.attr_name = something (write)
            if isinstance(node.expr, astroid.nodes.Name) and node.expr.name == "self":
                # print(f"    Attribute access detected: self.{node.attrname}")
                self.attr_names_accessed.add(node.attrname)

        for child in node.get_children():
            self.visit(child)


# def find_uses_of_self(fn_node) -> typing.List[str]:
#     """Given an AST node representing an instance method, attempts to find names
#     of all instance attributes used by this function.
#     """
#     attr_names = []
# for node in ast.walk(fn_node):
#     # Detect self.attr_name
#     if isinstance(node, astroid.nodes.Attribute):
#         if isinstance(node.value, astroid.nodes.Name) and node.id == "self":
#             print(f"    Attribute access detected: self.{node.attr}")
# return attr_names


def main() -> inspector.Project:
    print("=================TCC=================")
    """Script entrypoint"""
    PROJECT_DIR = "samples"

    # filename = "samples/sample1.py"
    # with open(filename, encoding="utf8") as sample_py:
    #     root = ast.parse(sample_py.read(), filename=filename)

    # astpretty.pprint(root)

    project = inspector.project_from_files(["samples"], project_name="sample-project")
    linker = inspector.Linker(project, tag=True)
    # We need this to make the linker actually work on the project
    linker.visit_project(project)

    for module in project.modules:
        for statement in module.body:
            if isinstance(statement, astroid.nodes.ClassDef):
                print(
                    f"Module {module.name}: {statement.name} has TCC = {compute_tcc(statement)}, LSCC = {compute_lscc(statement)}",
                )

    # Return the project object so we can debug it in the console
    return project

if __name__ == "__main__":
    main()
