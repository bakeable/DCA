from importlib import import_module
from pathlib import Path

# Get all modules
mutations = {}
directory = str(Path().resolve())
pathlist = Path(directory + "/mutations").glob("*.py")

# Import all mutations
for path in pathlist:
    # Convert to string
    path_in_str = str(path)

    # Get instance
    module = path_in_str.split(".py").pop(0).split("/").pop()
    function_name = module.split("_").pop()

    # Import function
    if len(function_name) == 3:
        mutations[function_name] = getattr(import_module("." + module, package='mutations'), "mutate_" + function_name)

