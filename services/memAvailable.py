import psutil

def print_available_memory():
    mem = psutil.virtual_memory()
    print(f"Total Memory: {mem.total}")
    print(f"Available Memory: {mem.available}")

print_available_memory()