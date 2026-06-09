import os
import json
import re

files = [
    r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\extracted_logs.txt",
    r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\rownd_id_logs.txt"
]

for fpath in files:
    if os.path.exists(fpath):
        print(f"Searching in: {fpath}")
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Look for stardust logs JSON
            # Typically has keys like 'date', 'period', 'bleeding'
            matches = re.findall(r'(\[\s*\{\s*"date":\s*"\d{4}-\d{2}-\d{2}".*?\}\s*\])', content, re.DOTALL)
            print(f"  Found {len(matches)} potential JSON array matches.")
            for i, m in enumerate(matches[:3]):
                print(f"  Match {i}: length {len(m)}")
                try:
                    data = json.loads(m)
                    print(f"  Successfully parsed Match {i}! Total logs: {len(data)}")
                    # Save it
                    out_path = f"C:\\Users\\PC\\Desktop\\nhacuongthuoc\\stardust_logs_found_{i}.json"
                    with open(out_path, "w", encoding="utf-8") as f_out:
                        json.dump(data, f_out, indent=2, ensure_ascii=False)
                    print(f"  Saved to {out_path}")
                except Exception as e:
                    print(f"  Failed parsing Match {i}: {e}")
                    
            # Let's search for "my-logs" and show surrounding text
            for match in re.finditer(r"my-logs", content):
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 200)
                print(f"  my-logs match: {content[start:end]}")
    else:
        print(f"File not found: {fpath}")
