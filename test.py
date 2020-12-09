import ast
import typing
import pprint

import astpretty
import astroid.nodes
import astroid.node_classes
from pylint.pyreverse.inspector import Linker, project_from_files

import astroid.helpers

# filename = "samples/sample1.py"
# with open(filename, encoding="utf8") as sample_py:
#     root = ast.parse(sample_py.read(), filename=filename)

# astpretty.pprint(root)

PROJECT_DIR = "samples"


project = project_from_files(["samples/sample1.py"], project_name="sample-project")
linker = Linker(project, tag=True)
# We need this to make the linker actually work on the project
linker.visit_project(project)

sample_module = project.modules[0]
parent_class, child_class = sample_module.body


def compute_tcc(cls) -> int:
    for base_class in cls.bases:
        print(f"{cls.name} has parent class {base_class.name}")
    for attr_name in cls.instance_attrs:
        print(f"{cls.name} has instance attribute {attr_name}")

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

    tcc_sum = 0
    for method1 in method_to_attrs_accessed:
        for method2 in method_to_attrs_accessed:
            if method1 == method2:
                continue
            if method_to_attrs_accessed[method1] & method_to_attrs_accessed[method2]:
                tcc_sum += 1
    return tcc_sum / (k * (k - 1))



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


def find_uses_of_self(fn_node) -> typing.List[str]:
    """Given an AST node representing an instance method, attempts to find names
    of all instance attributes used by this function.
    """
    attr_names = []
    # for node in ast.walk(fn_node):
    #     # Detect self.attr_name
    #     if isinstance(node, astroid.nodes.Attribute):
    #         if isinstance(node.value, astroid.nodes.Name) and node.id == "self":
    #             print(f"    Attribute access detected: self.{node.attr}")
    return attr_names


print(compute_tcc(parent_class))
print(compute_tcc(child_class))
