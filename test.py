import ast
import typing
import pprint
import itertools
import statistics

import astpretty
import astroid.nodes
import astroid.node_classes
from pylint.pyreverse import inspector

import astroid.helpers


def compute_tcc(cls: astroid.nodes.ClassDef) -> int:
    """Computes the TCC of a class."""
    # Mapping of (method name) -> (instance attributes accessed)
    method_to_attrs_accessed: typing.Dict[str, typing.Set[str]] = {}
    for method in cls.mymethods():
        finder = AstSelfFinder()
        finder.visit(method)
        method_to_attrs_accessed[method.name] = set(finder.attr_names_accessed)

    k = len(method_to_attrs_accessed)
    if k <= 1:
        print(f"TCC: Ignoring class {cls.name} because it has only {k} method")
        return None

    # Contains methods that access a common attribute, i.e CAU
    cau_methods: typing.Set[typing.Tuple[str, str]] = set()
    for method1, method2 in itertools.combinations(method_to_attrs_accessed, 2):
        assert method1 < method2, "Not sorted!"
        if method_to_attrs_accessed[method1] & method_to_attrs_accessed[method2]:
            cau_methods.add((method1, method2))
    return len(cau_methods) / (k * (k - 1) / 2)


def compute_lscc(cls) -> typing.Optional[None]:
    methodlist = []
    for method_name in cls.mymethods():
        methodlist.append(method_name)
    l = len(cls.instance_attrs)
    k = len(methodlist) - 1
    if l == 0 and k == 0:
        print("input error : there is no attribue and method")
        return None
    elif (l == 0) and (k > 1):
        return 0
    elif (l > 0 and k == 0) or k == 1:
        return 1
    else:
        sum = 0
        for attr_name in cls.instance_attrs:
            count = 0
            for method_name in cls.mymethods():
                if method_name.name == "__init__":
                    pass
                else:
                    finder = AstSelfFinder()
                    finder.visit(method_name)
                    if attr_name in finder.attr_names_accessed:
                        count = count + 1
            sum = sum + (count * (count - 1))
        sum = sum / (l * k * (k - 1))
        return sum


class ProjectScore(typing.NamedTuple):
    """Scores of a project"""

    lscc: float
    tcc: float


def compute_project_score(project_path: str) -> ProjectScore:
    """Computes the score for a project.

    Returns:
        An object with the fields:
            obj.lscc: LSCC score
            obj.tcc:  TCC score
    """
    project = inspector.project_from_files([project_path], project_name="the-project")
    linker = inspector.Linker(project, tag=True)
    # We need this to make the linker actually work on the project
    linker.visit_project(project)

    tcc_values = []
    lscc_values = []

    for module in project.modules:
        for statement in module.body:
            if isinstance(statement, astroid.nodes.ClassDef):
                tcc_values.append(compute_tcc(statement))
                lscc_values.append(compute_lscc(statement))

    return ProjectScore(
        lscc=statistics.mean(filter(lambda x: x is not None, lscc_values)),
        tcc=statistics.mean(filter(lambda x: x is not None, tcc_values)),
    )


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


def main() -> None:
    print("=================TCC=================")
    """Script entrypoint"""
    PROJECT_DIR = "samples"

    print(compute_project_score(PROJECT_DIR))


if __name__ == "__main__":
    main()
