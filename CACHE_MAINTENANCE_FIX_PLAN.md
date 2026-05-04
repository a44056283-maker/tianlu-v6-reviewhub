# 缓存维护修复实施计划（草案）

> 状态：仅草案，不直接执行
> 根因：macOS APFS 外接卷 Python 权限限制

---

## 核心结论

Python `pathlib.Path.mkdir()` 和 `shutil.copy2()` 在 macOS APFS 外接卷上被系统拦截，shell 命令（`rsync`/`mkdir`）可以绕过。

## 修复方案

### 修改 1：`tianlu_cache_maintenance.py` 第 101 行附近

将：
```python
shutil.copy2(src, tmp)
```

替换为：
```python
import subprocess
subprocess.run(['rsync', '-a', src, dst], check=True)
```

### 修改 2：`tianlu_system_backup.py` 第 194 行附近

将：
```python
target.mkdir(parents=True, exist_ok=True)
```

替换为：
```python
import subprocess
subprocess.run(['mkdir', '-p', str(target)], check=True)
```

### 修改 3：SQLite 文件（m1_cache.db 等）

```python
import sqlite3
def backup_sqlite_db(src_db, dst_path):
    """使用 SQLite .backup() API，零锁、快照一致"""
    conn = sqlite3.connect(src_db, timeout=5)
    bak_conn = sqlite3.connect(dst_path)
    conn.backup(bak_conn)
    bak_conn.close()
    conn.close()
```

---

## 待用户/GPT 确认后再执行
