#!/usr/bin/env python3
"""
GCC 报错处理器：读取 GCC 的 stderr，替换为自定义输出。
当前版本：把所有报错替换为 hello world。
后续可扩展：解析 JSON、调用 LLM、生成修复建议。
"""

import argparse
import json
import sys


def success_quit():
    print("编译成功了呢喵~", file=sys.stderr)


def failed_quit():
    # 从 stdin 读取 GCC 的原始 stderr
    raw_stderr = sys.stdin.read()
    try:
        sarif = json.loads(raw_stderr)
        # print(f"\n----------\n{data}\n----------\n", file=sys.stderr)
        with open("output.json", "w") as file:
            json.dump(sarif, file)
        for run in sarif.get("runs", []):
            for r in run.get("results", []):
                ruleId = r.get("ruleId", [])

                level = r.get("level", [])

                message = r.get("message", [])
                text = message.get("text", [])

                print(
                    f"\n\ruleId:{ruleId}\nlevel:{level}\nmessage:{text}\nlocations:\nfixes:\n\n",
                    file=sys.stderr,
                )
    except json.JSONDecodeError:
        print(raw_stderr)


def main():
    # 读取编译状态
    parser = argparse.ArgumentParser()
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()

    if args.exit_code == 0:
        success_quit()
    else:
        failed_quit()


if __name__ == "__main__":
    main()
