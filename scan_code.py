from pathlib import Path

CODE_FOLDER = Path("company_code")

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".cs",
    ".java",
    ".sql",
    ".html",
    ".css"
}

for file_path in CODE_FOLDER.rglob("*"):
    if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:

        print("\n" + "=" * 60)
        print(f"DOSYA: {file_path}")
        print("=" * 60)

        try:
            content = file_path.read_text(encoding="utf-8")

            if content.strip():
                print(content)
            else:
                print("[DOSYA BOŞ]")

        except Exception as e:
            print(f"Dosya okunamadı: {e}")
