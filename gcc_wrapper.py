#!/usr/bin/env python3
"""
GCC 报错处理器：读取 GCC 的 stderr，替换为自定义输出。
当前版本：把所有报错替换为 hello world。
后续可扩展：解析 JSON、调用 LLM、生成修复建议。
"""

import argparse
import sys


def main():
    # 读取编译状态
    parser = argparse.ArgumentParser()
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()

    if args.exit_code == 0:
        print("编译成功了呢喵~", file=sys.stderr)
        return

    if args.exit_code == 1:
        # 从 stdin 读取 GCC 的原始 stderr
        raw_stderr = sys.stdin.read()
        print(f"{raw_stderr}\n真是杂鱼呢喵~", file=sys.stderr)


if __name__ == "__main__":
    main()
