#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tomllib

from dotenv import load_dotenv
from openai import OpenAI
import tomli_w


class Wrapper:
    def __init__(self):
        with open("config.toml", "rb") as f:
            self.config = tomllib.load(f)
        self.prompt = self.config["prompt"]
        self.likeability = self.config["numerical_value"]["likeability"]

    def like_change(self, num):
        self.likeability += num
        if self.likeability < 0:
            self.likeability = 0
        elif self.likeability > 100:
            self.likeability = 100
        self.config["numerical_value"]["likeability"] = self.likeability
        with open("config.toml", "wb") as f:
            tomli_w.dump(self.config, f)

    def success_quit(self):
        print("编译成功了呢喵~", file=sys.stderr)
        self.like_change(5)

    def failed_quit(self):
        raw_stderr = sys.stdin.read()
        try:
            sarif = json.loads(raw_stderr)
            """
            with open("output.json", "w") as file:
                json.dump(sarif, file)
            """
            like_change_num = 0
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
                    self.connect_llm(
                        f"ruleId:{ruleId}level:{level}message:{text}likeability:{self.likeability}"
                    )
                    like_change_num -= 1
            self.like_change(like_change_num)
        except json.JSONDecodeError:
            print(raw_stderr)

    def connect_llm(self, content):
        load_dotenv()
        api_key = os.getenv("API_KEY")

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": self.prompt["system_prompt"],
                },
                {"role": "user", "content": content},
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=False,
        )
        print(response.choices[0].message.content, file=sys.stderr)


def main():
    # 读取编译状态
    parser = argparse.ArgumentParser()
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()

    if args.exit_code == 0:
        wrap.success_quit()
    else:
        wrap.failed_quit()


if __name__ == "__main__":
    wrap = Wrapper()
    main()
    print(f"{wrap.likeability}", file=sys.stderr)
