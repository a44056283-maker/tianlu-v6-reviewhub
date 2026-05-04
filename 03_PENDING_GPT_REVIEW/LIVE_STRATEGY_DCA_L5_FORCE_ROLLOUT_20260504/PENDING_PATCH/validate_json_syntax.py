#!/usr/bin/env python3
"""
JSON语法验证脚本
对PENDING_PATCH目录下的所有补丁文件进行JSON语法验证
"""
import json
import os
import sys
from pathlib import Path

PENDING_DIR = Path(__file__).parent
BACKUP_DIR = Path(__file__).parent.parent.parent / "04_BACKUPS" / "live_rollout_20260504_150000"

def validate_json_file(filepath: Path) -> tuple[bool, str]:
    """验证单个JSON文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, f"OK - {len(data)} top-level keys"
    except json.JSONDecodeError as e:
        return False, f"JSON ERROR: {e}"
    except Exception as e:
        return False, f"ERROR: {e}"

def main():
    print("=" * 60)
    print("JSON语法验证报告")
    print(f"目录: {PENDING_DIR}")
    print("=" * 60)

    all_ok = True
    results = []

    for f in sorted(PENDING_DIR.glob("*_PATCHED*.json")):
        ok, msg = validate_json_file(f)
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        results.append((status, f.name, msg))
        print(f"  [{status}] {f.name}: {msg}")

    print()
    print("=" * 60)
    if all_ok:
        print("结果: 所有补丁文件JSON语法验证通过")
    else:
        print("结果: 存在无效JSON文件，请修复后重试")
    print("=" * 60)

    # 同时验证备份目录
    print()
    print("备份文件验证:")
    backup_ok = True
    for f in sorted(BACKUP_DIR.glob("*.bak_*")):
        ok, msg = validate_json_file(f)
        status = "PASS" if ok else "FAIL"
        if not ok:
            backup_ok = False
        print(f"  [{status}] {f.name}: {msg}")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
