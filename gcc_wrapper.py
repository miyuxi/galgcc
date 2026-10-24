#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path

import tomli_w
from dotenv import load_dotenv
from openai import OpenAI

# 所有资源都以本文件所在目录为基准, 这样在任意工作目录下调用都能正常工作
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / ".config.toml"
PROMPTS_DIR = BASE_DIR / "prompts"


class Wrapper:
    def __init__(self):
        with open(CONFIG_PATH, "rb") as f:
            self.config = tomllib.load(f)
        self.system_prompt = self.config["prompt"]["system_prompt"]
        self.likeability = self.config["affinity_system"]["likeability"]
        self.affinity_levels = self.config["affinity_system"]["affinity_levels"]
        self.character = self.config["character"]["current"]
        with open(PROMPTS_DIR / self.character / "core_prompt.toml", "rb") as f:
            self.character_prompt = tomllib.load(f)
        self.character_prompt = self.character_prompt["core"]
        self.like_level = self.get_like_level()
        self.fail_path = (
            PROMPTS_DIR / self.character / "fail" / f"fail{self.like_level}.toml"
        )
        self.success_path = (
            PROMPTS_DIR / self.character / "success" / f"success{self.like_level}.toml"
        )

    def like_change(self, num):
        self.likeability += num
        if self.likeability < 0:
            self.likeability = 0
        elif self.likeability > 100:
            self.likeability = 100
        self.config["affinity_system"]["likeability"] = self.likeability
        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(self.config, f)

    def get_like_level(self):
        rules = [(item["threshold"], item["level"]) for item in self.affinity_levels]
        for threshold, level in reversed(rules):
            if self.likeability >= threshold:
                return level

    def success_quit(self):
        with open(self.success_path, "rb") as f:
            like_prompt = tomllib.load(f)
        like_prompt = like_prompt["like_prompt"]
        print(
            f"{
                self.connect_llm(
                    '用户编译成功了',
                    f'{self.system_prompt}{self.character_prompt}{like_prompt}',
                )
            }"
        )
        self.like_change(5)

    def failed_quit(self):
        raw_stderr = sys.stdin.read()
        try:
            with open(self.fail_path, "rb") as f:
                like_prompt = tomllib.load(f)
            like_prompt = like_prompt["like_prompt"]

            sarif = json.loads(raw_stderr)
            like_change_num = 0
            for run in sarif.get("runs", []):
                for r in run.get("results", []):
                    uri, startLine, startColumn, level, text, ruleId = (
                        self.error_message_extraction(r)
                    )

                    print(
                        f"{uri}:{startLine}:{startColumn}: {self.connect_llm(f'level:{level}message:{text}', f'{self.system_prompt}{self.character_prompt}{like_prompt}')} [{ruleId}]",
                        file=sys.stderr,
                    )
                    like_change_num -= 1
            self.like_change(like_change_num)
        except json.JSONDecodeError:
            print(raw_stderr)

    def error_message_extraction(self, r):
        ruleId = r.get("ruleId", [])

        level = r.get("level", [])

        message = r.get("message", [])
        text = message.get("text", [])

        locations = r.get("locations", [])[0]
        physicalLocation = locations.get("physicalLocation", [])
        artifactLocation = physicalLocation.get("artifactLocation", [])
        uri = artifactLocation.get("uri", [])
        region = physicalLocation.get("region", [])
        startLine = region.get("startLine", [])
        startColumn = region.get("startColumn", [])
        return uri, startLine, startColumn, level, text, ruleId

    def connect_llm(self, user_content, system_prompt):
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("API_KEY")

        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": user_content},
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=False,
        )
        return response.choices[0].message.content


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
