#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tomllib

from dotenv import load_dotenv
from openai import OpenAI


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

                """
                print(
                    f"\n\nruleId:{ruleId}\nlevel:{level}\nmessage:{text}\nlocations:\nfixes:\n\n",
                    file=sys.stderr,
                )
                """
                connect_llm(f"ruleId:{ruleId}level:{level}message:{text}n")

    except json.JSONDecodeError:
        print(raw_stderr)


def connect_llm(content):
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "system",
                "content": cfg["system_prompt"],
            },
            {"role": "user", "content": content},
        ],
        max_tokens=1024,
        temperature=0.7,
        stream=False,
    )
    print(response.choices[0].message.content, file=sys.stderr)


def init():
    with open("config.toml", "rb") as f:
        cfg = tomllib.load(f)
    return cfg


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
    cfg = init()
    main()
