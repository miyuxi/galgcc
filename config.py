import tomllib
from pathlib import Path

import tomli_w

# 与 gcc_wrapper.py 保持一致: 配置文件始终指向本仓库, 不受调用时的工作目录影响
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / ".config.toml"


class Preferences:
    def __init__(self):
        self.config_path = CONFIG_PATH
        with open(self.config_path, "rb") as f:
            self.config = tomllib.load(f)
        self.likeability = self.config["affinity_system"]["likeability"]
        self.character_current = self.config["character"]["current"]
        self.character_list = self.config["character"]["list"]
        self.character_num = len(self.character_list)

    def show_character_list(self):
        i = 1
        for c in self.character_list:
            print(f"{i}:{c}\n")
            i += 1

    def choose_character(self, num):
        if isinstance(num, int) and 0 < num and num <= self.character_num:
            self.config["character"]["current"] = self.character_list[num - 1]
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self.config, f)


def str_is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def main():
    pref.show_character_list()
    num = input(":")
    while not str_is_int(num):
        num = input(":")
    pref.choose_character(int(num))


if __name__ == "__main__":
    pref = Preferences()
    main()
