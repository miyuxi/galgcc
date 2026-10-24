# galgcc
为gcc添加好感度系统

## 依赖
pip install openai tomli_w python-dotenv

## 安装
拉取代码<br>
在.zshrc中添加一下函数
```sh
gcc() {
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
export API_KEY="your-key"
```
将~/galgcc/gcc_wrapper.py改成实际地址<br>
将your-key改为你的apikey

## 添加人设
1.在./prompts目录下新增文件夹,命名为A,可自行替换名称<br>
2.在A中建success和fail两个文件夹,其中各放9个.toml文件,分别命名为<br>
success0.toml到success8.toml和fail0.toml到fail.toml<br>
3.每个文件内容如下
```toml
like_prompt = """"你的内容"""
```
4.在./.config.toml中添加一下内容
```toml
[character]
current = "mesugaki"
list = ["mesugaki","A"]
```
5.可以直接修改current为A,也可运行config.py选择

## 实现方法
通过同名函数转接,处理gcc报错信息

## 待添加功能

## 灵感来源
[kawaii-gcc](https://github.com/Bill-Haku/kawaii-gcc)<br>
[编程语言娘化galgame](https://www.bilibili.com/video/BV1rgBFBFE1V/?spm_id_from=333.40138.top_right_bar_window_history.content.click&vd_source=48faf476e3f368ce7cf7b6aef346e6c9)
