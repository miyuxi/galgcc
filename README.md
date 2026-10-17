# galgcc
希望让c语言学习不再枯燥

## 依赖
pip install openai

## 安装
拉取代码
```sh
mygcc() {
    local tmp_err
    tmp_err=$(mktemp)

    /usr/bin/gcc -fdiagnostics-format=sarif-stderr "$@" 2>"$tmp_err"
    local exit_code=$?

    python3 \
      ~/galgcc/gcc_wrapper.py \
      --exit-code "$exit_code" < "$tmp_err"

    rm -f "$tmp_err"
    return $exit_code
}
```
将~/galgcc/gcc_wrapper.py改成实际地址
