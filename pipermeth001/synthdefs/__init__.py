# -*- coding: utf-8 -*-


def autoimport(file_path, namespace):
    import importlib
    import pathlib
    import pipermeth001
    root_package = pipermeth001
    root_name = root_package.__name__
    root_path = pathlib.Path(root_package.__path__[0])
    for path in pathlib.Path(file_path).parent.iterdir():
        if path.suffix != '.py':
            continue
        path = path.with_suffix('')
        path_parts = (root_name,) + path.relative_to(root_path).parts
        module_path = '.'.join(path_parts)
        module = importlib.import_module(module_path)
        member_names = getattr(module, '__all__', [])
        for member_name in member_names:
            member = getattr(module, member_name)
            namespace[member_name] = member


autoimport(__file__, globals())

del(autoimport)
