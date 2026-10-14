#!/usr/bin/env python3
"""
GCC 报错处理器：读取 GCC 的 stderr，替换为自定义输出。
当前版本：把所有报错替换为 hello world。
后续可扩展：解析 JSON、调用 LLM、生成修复建议。
"""

import sys


def main():
    # 从 stdin 读取 GCC 的原始 stderr
    raw_stderr = sys.stdin.read()

    if not raw_stderr.strip():
        # 没有任何报错，不输出
        print("成功编译了呢喵~")
        return

    # === 简单版本：直接替换为 hello world ===
    # 后续可在此处加入 JSON 解析 / LLM 推理
    print("hello world", file=sys.stderr)


if __name__ == "__main__":
    main()
