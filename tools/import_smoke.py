import pkgutil, importlib, traceback

ROOT = "app"
failures = []
for m in pkgutil.walk_packages([ROOT], prefix="app."):
    name = m.name
    try:
        importlib.import_module(name)
    except Exception as e:
        failures.append((name, f"{type(e).__name__}: {e}"))
        print(f"FAIL {name}: {e}")

print("\nSUMMARY")
print("-------")
if not failures:
    print("All imports succeeded.")
else:
    for n, err in failures:
        print(f"{n} -> {err}")
    raise SystemExit(1)
