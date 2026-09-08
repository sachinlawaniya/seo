import json

with open("audit_raw_data.json", "r", encoding="utf-8") as f:
    d = json.load(f)

with open("app.js", "r", encoding="utf-8") as f:
    app_code = f.read()

fallback_header = "// Standalone Embedded Audit Dataset\nif (typeof window !== 'undefined' && !window.AUDIT_RAW_DATA) {\n  window.AUDIT_RAW_DATA = " + json.dumps(d, ensure_ascii=False) + ";\n}\n\n"

if "Standalone Embedded Audit Dataset" not in app_code:
    with open("app.js", "w", encoding="utf-8") as f:
        f.write(fallback_header + app_code)

print("Updated app.js size:", len(open("app.js", "r", encoding="utf-8").read()))
