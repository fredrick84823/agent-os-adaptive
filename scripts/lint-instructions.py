#!/usr/bin/env python3
"""Lint Agent OS Adaptive 的 instructions / subagents / standards / README。

檢查項目：
  1. frontmatter：instructions/*.md 與 subagents/*.md 第一行必須是 `---`，且有成對的結尾 `---`；
     instructions 需含 `description`，subagents 需含 `name` 與 `description`。
  2. 不得出現個人機器的絕對路徑（/Users/...、/home/...）。
  3. `@~/agent-os-adaptive/<path>` 引用的檔案必須存在於本 repo；
     `@agent-os-adaptive/product/<file>` 必須是 plan-product 會產生的檔案。
  4. README 中的 slash / @ 指令必須對應到 instructions/<name>.md；
     README 不得 curl 上游 buildermethods 的 setup 腳本（已 404）。

用法：python3 scripts/lint-instructions.py   （exit 0 = 通過）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["instructions", "subagents", "standards"]
# plan-product.md 會在使用者專案中產生的 product 文件
GENERATED_PRODUCT_FILES = {"mission.md", "tech-stack.md", "roadmap.md", "decisions.md"}
ABS_PATH_RE = re.compile(r"(?<![\w~])/(?:Users|home)/[\w.-]+")
HOME_REF_RE = re.compile(r"@~/agent-os-adaptive/([\w./-]+\.(?:md|mermaid))")
PRODUCT_REF_RE = re.compile(r"@agent-os-adaptive/product/([\w.-]+\.md)")
README_CMD_RE = re.compile(r"^\s*[/@]([a-z][a-z-]+)\s*$")

errors = []


def err(path, line, msg):
    errors.append(f"{path.relative_to(ROOT)}:{line}: {msg}")


def check_frontmatter(path, required_keys):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        err(path, 1, f"frontmatter 必須以 '---' 開頭（實際為 {lines[0][:20]!r}）" if lines else "空檔案")
        return
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        err(path, 1, "frontmatter 缺少結尾 '---'")
        return
    keys = {l.split(":", 1)[0].strip() for l in lines[1:end] if ":" in l}
    for k in required_keys:
        if k not in keys:
            err(path, 1, f"frontmatter 缺少 '{k}'")


def iter_md():
    for d in SCAN_DIRS:
        yield from sorted((ROOT / d).glob("*.md"))
    yield ROOT / "README.md"


for p in sorted((ROOT / "instructions").glob("*.md")):
    check_frontmatter(p, ["description"])
for p in sorted((ROOT / "subagents").glob("*.md")):
    check_frontmatter(p, ["name", "description"])

for p in iter_md():
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for m in ABS_PATH_RE.finditer(line):
            err(p, n, f"出現絕對路徑 {m.group(0)}…，請改用 ~/agent-os-adaptive/ 相對路徑")
        for m in HOME_REF_RE.finditer(line):
            if not (ROOT / m.group(1)).exists():
                err(p, n, f"引用的檔案不存在：{m.group(1)}")
        for m in PRODUCT_REF_RE.finditer(line):
            if m.group(1) not in GENERATED_PRODUCT_FILES:
                err(p, n, f"product/{m.group(1)} 不會由 plan-product 產生")

readme = ROOT / "README.md"
for n, line in enumerate(readme.read_text(encoding="utf-8").splitlines(), 1):
    m = README_CMD_RE.match(line)
    if m and not (ROOT / "instructions" / f"{m.group(1)}.md").exists():
        err(readme, n, f"指令 {m.group(1)} 沒有對應的 instructions/{m.group(1)}.md")
    if "raw.githubusercontent.com/buildermethods" in line:
        err(readme, n, "README 引用上游 buildermethods setup 腳本（已 404），請改用本 repo 的安裝步驟")

if errors:
    print("\n".join(errors))
    print(f"\nFAIL: {len(errors)} 個問題")
    sys.exit(1)
print("OK: instructions / subagents / standards / README 檢查通過")
