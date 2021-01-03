import os

import utils_listener
import utils

def pushdown_field(source_filenames: list,
                   package_name: str,
                   superclass_name: str,
                   field_name: str,
                   class_names: list = [],
                   filename_mapping = lambda x: (x[:-5] if x.endswith(".java") else x) + ".re.java") -> bool:

    program = utils.get_program(source_filenames)

    if package_name not in program.packages \
            or superclass_name not in program.packages[package_name].classes \
            or field_name not in program.packages[package_name].classes[superclass_name].fields:
        return False

    #all_derived_classes = [] # Not needed
    other_derived_classes = []
    classes_to_add_to = []
    for pn in program.packages:
        p: utils_listener.Package = program.packages[pn]
        for cn in p.classes:
            c: utils_listener.Class = p.classes[cn]
            if ((c.superclass_name == superclass_name and c.file_info.has_imported_class(package_name, superclass_name)) \
                    or (package_name is not None and c.superclass_name == package_name + '.' + superclass_name)):
                #all_derived_classes.append(c)
                if len(class_names) == 0 or cn in class_names:
                    if field_name in c.fields:
                        return False
                    else:
                        classes_to_add_to.append(c)
                else:
                    other_derived_classes.append(c)
    # Check if the field is used from the superclass or other derived classes
    for pn in program.packages:
        p: utils_listener.Package = program.packages[pn]
        for cn in p.classes:
            c: utils_listener.Class = p.classes[cn]
            has_imported_superclass = c.file_info.has_imported_class(package_name, superclass_name)
            fields_of_superclass_type_or_others = []
            for fn in c.fields:
                f: utils_listener.Field = c.fields[fn]
                if (f.datatype == superclass_name and has_imported_superclass) \
                        or (package_name is not None and f.datatype == (package_name + '.' + superclass_name)):
                    fields_of_superclass_type_or_others.append(f.name)
                if any((c.file_info.has_imported_class(o.package_name, o.name) and f.datatype == o.name)
                        or f.datatype == (o.package_name + '.' + o.name) for o in other_derived_classes):
                    fields_of_superclass_type_or_others.append(f.name)
            for mn in c.methods:
                m: utils_listener.Method = c.methods[mn]
                local_vars_of_superclass_type_or_others = []
                for item in m.body_local_vars_and_expr_names:
                    if isinstance(item, utils_listener.LocalVariable):
                        if (item.datatype == superclass_name and has_imported_superclass) \
                                or item.datatype == (package_name + '.' + superclass_name):
                            local_vars_of_superclass_type_or_others.append(item.identifier)
                        if any((c.file_info.has_imported_class(o.package_name, o.name) and item.datatype == o.name)
                                or item.datatype == (o.package_name + '.' + o.name) for o in other_derived_classes):
                            local_vars_of_superclass_type_or_others.append(item.identifier)
                    elif isinstance(item, utils_listener.ExpressionName):
                        if item.dot_separated_identifiers[-1] == field_name \
                                and (
                                    (len(item.dot_separated_identifiers) == 2)
                                    or (len(item.dot_separated_identifiers) == 3 and item.dot_separated_identifiers[0] == "this")
                                ) and (
                                    (item.dot_separated_identifiers[-2] in local_vars_of_superclass_type_or_others and len(item.dot_separated_identifiers) == 2)
                                    or item.dot_separated_identifiers[-2] in fields_of_superclass_type_or_others
                                ):
                            return False

    rewriter = utils.Rewriter(program, filename_mapping)

    superclass = program.packages[package_name].classes[superclass_name]
    field = superclass.fields[field_name]
    if len(field.neighbor_names) == 0:
        rewriter.replace(field.get_tokens_info(), "")
    else:
        i = field.index_in_variable_declarators
        var_ctxs = field.all_variable_declarator_contexts
        if i == 0:
            to_remove = utils_listener.TokensInfo(var_ctxs[i])
            to_remove.stop = utils_listener.TokensInfo(var_ctxs[i + 1]).start - 1  # Include the ',' after it
            rewriter.replace(to_remove, "")
        else:
            to_remove = utils_listener.TokensInfo(var_ctxs[i])
            to_remove.start = utils_listener.TokensInfo(var_ctxs[i - 1]).stop + 1  # Include the ',' before it
            rewriter.replace(to_remove, "")

    is_public = "public" in field.modifiers
    is_protected = "protected" in field.modifiers
    modifier = ("public " if is_public else ("protected " if is_protected else ""))
    for c in classes_to_add_to:
        c_body_start = utils_listener.TokensInfo(c.parser_context.classBody())
        c_body_start.stop = c_body_start.start  # Start and stop both point to the '{'
        rewriter.insert_after(c_body_start, "\n    " + modifier + field.datatype + " " + field_name \
                              + ((" = " + field.initializer) if field.initializer is not None else "")
                              + ";")

    rewriter.apply()
    return True

if __name__ == "__main__":
    print("Testing pushdown_field...")
    filenames = [
        "tests/pushdown_field/test1.java",
        "tests/pushdown_field/test2.java",
        "tests/pushdown_field/test3.java",
        "tests/pushdown_field/test4.java",
        "tests/pushdown_field/test5.java",
        "tests/pushdown_field/test6.java",
        "tests/pushdown_field/test7.java",
    ]

    if pushdown_field(filenames[:2], "pushdown_field_test1", "A", "a"):
        print("1, 2: Success!")
    else:
        print("1, 2: Cannot refactor.")

    for i in range(2, 7):
        if pushdown_field(filenames[:2] + [filenames[i]], "pushdown_field_test1", "A", "a"):
            print("1, 2, " + str(i + 1) + ": Success!")
        else:
            print("1, 2, " + str(i + 1) + ": Cannot refactor.")
