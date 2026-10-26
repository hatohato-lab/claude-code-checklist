# -*- coding: utf-8 -*-
r"""チェックリストを点検する（スキル「チェックリストの作成」の7節の6つの点検）。

    python -X utf8 "<このスキルのフォルダー>/チェックリストを点検する.py" "<トピックのフォルダー>"

点検すること
1. 切れているリンク（チェックリストの中の、相対パスのリンクの先が無い）
2. 親から指されていない子のチェックリスト
3. 親へ戻るリンクが無い子のチェックリスト
4. 詳しい中身の HTML が無い子のフォルダー（チェックリストのほかに .html が1つも無い）
5. 子の表と合わない親の行の状態（全部が完了なら完了、全部が未着手なら未着手、それ以外は作業中）
6. 名前か状態の言葉が決まりと違うチェックリスト（名前は階層とフォルダー名、状態は完了・作業中・未着手、1フォルダーに1枚）
1つでもあれば、終わりのコードを1にする。読むだけで、何も書き換えない。
"""
import html
import os
import re
import sys
from urllib.parse import unquote

PREFIX = "チェックリスト_"
NUMBER = re.compile(r"^\d+_")
STATES = ("完了", "作業中", "未着手")
SKIP_PREFIX = (".", "旧_")
SKIP_DIRS = ("plantuml", "__pycache__")
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
HREF = re.compile(r'<a\s[^>]*href="([^"]+)"')
TAG = re.compile(r"<[^>]+>")
EXTERNAL = re.compile(r"^(https?:|mailto:|#)")
KINDS = (
    ("link", "切れているリンク"),
    ("orphan", "親から指されていない子のチェックリスト"),
    ("back", "親へ戻るリンクが無い子のチェックリスト"),
    ("detail", "詳しい中身の HTML が無い子のフォルダー"),
    ("state", "子の表と合わない親の行の状態"),
    ("name", "名前か状態の言葉が決まりと違うチェックリスト"),
)


def key(path):
    return os.path.normcase(os.path.normpath(path))


def expected_name(d, root):
    base = os.path.basename(d)
    label = NUMBER.sub("", base) or base
    rel = os.path.relpath(d, root)
    if rel == ".":
        return PREFIX + "全体_" + label + ".html"
    return PREFIX + "第{}階層_".format(len(rel.split(os.sep))) + label + ".html"


def plain(cell):
    return html.unescape(TAG.sub("", cell)).strip()


def read(path):
    """表の行（作業内容、リンク先、状態）と、ページの中の全部のリンク先を返す。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    rows = []
    for m in ROW.finditer(text):
        cells = CELL.findall(m.group(1))
        if len(cells) != 2:
            continue
        hrefs = HREF.findall(cells[0])
        rows.append({"text": plain(cells[0]), "href": unquote(hrefs[0]) if hrefs else None, "state": plain(cells[1])})
    return rows, [unquote(h) for h in HREF.findall(text)]


def combine(states):
    if not states or all(s == "未着手" for s in states):
        return "未着手"
    if all(s == "完了" for s in states):
        return "完了"
    return "作業中"


def main(argv):
    if len(argv) < 2:
        print("使い方: python -X utf8 チェックリストを点検する.py <トピックのフォルダー>")
        return 2
    root = os.path.normpath(os.path.abspath(argv[1]))
    found, problems = {}, {k: [] for k, _ in KINDS}
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if not x.startswith(SKIP_PREFIX) and x not in SKIP_DIRS)
        lists = sorted(f for f in files if f.startswith(PREFIX) and f.endswith(".html"))
        if not lists:
            continue
        rel = os.path.relpath(d, root)
        if len(lists) > 1:
            problems["name"].append("{}: チェックリストが{}枚ある".format(rel, len(lists)))
        if lists[0] != expected_name(d, root):
            problems["name"].append("{}: 名前は {} にする（いまは {}）".format(rel, expected_name(d, root), lists[0]))
        found[key(d)] = (d, os.path.join(d, lists[0]))
    if key(root) not in found:
        print("トピックのフォルダーにチェックリストが無い: " + root)
        return 2

    pages = {k: read(p) for k, (d, p) in found.items()}
    by_page = {key(p): k for k, (d, p) in found.items()}

    for k, (d, p) in found.items():
        rows, links = pages[k]
        rel = os.path.relpath(d, root)
        for target in links:
            if EXTERNAL.match(target):
                continue
            if not os.path.exists(os.path.join(d, target.split("#")[0])):
                problems["link"].append("{} から {}".format(rel, target))
        for r in rows:
            if r["state"] not in STATES:
                problems["name"].append("{}: 「{}」の状態が「{}」".format(rel, r["text"], r["state"]))
            child = by_page.get(key(os.path.join(d, r["href"]))) if r["href"] else None
            if child is not None and child != k:
                want = combine([c["state"] for c in pages[child][0]])
                if r["state"] != want:
                    problems["state"].append("{}: 「{}」は「{}」にする（いまは「{}」）".format(rel, r["text"], want, r["state"]))

    for k, (d, p) in found.items():
        if k == key(root):
            continue
        rel = os.path.relpath(d, root)
        up = os.path.dirname(d)
        while key(up) not in found:
            up = os.path.dirname(up)
        parent = key(up)
        pointed = any(r["href"] and key(os.path.join(up, r["href"])) == key(p) for r in pages[parent][0])
        if not pointed:
            problems["orphan"].append(rel)
        back = any(key(os.path.join(d, h)) == key(found[parent][1]) for h in pages[k][1])
        if not back:
            problems["back"].append(rel)
        others = [f for f in os.listdir(d) if f.endswith(".html") and not f.startswith(PREFIX)]
        if not others:
            problems["detail"].append(rel)

    print("点検: " + "、".join("{} {}件".format(label, len(problems[k])) for k, label in KINDS))
    for k, label in KINDS:
        for line in problems[k]:
            print("  {}: {}".format(label, line))
    return 1 if any(problems[k] for k, _ in KINDS) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
