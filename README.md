# 为知搜

Mac 版的为知笔记在没有网络的时候，无法使用全文搜索。如果去参加 CTF 线下赛，被屏蔽网络，就没法搜索笔记了，只能脑补。

分析了一下为知笔记的存储，格式很简单，用了 sqlite 来存储元数据，然后每篇笔记其实是用 ZIP 压缩，将 html 和 网页的图片打成一个压缩包。既然这么简单，那不如自己开发一个全文搜索功能。一开始有考虑要在为知笔记的客户端开源代码上修改，但是用C++写的，看不懂，也懒得去改，最终选择用Python写个站，使用 whoosh 和 jieba 分词建立了离线搜索功能。

## 使用方法

1. pip3 install -r requirements.txt
2. 复制 config.py.example 为 config.py
3. 修改 config.py 中的 WIZ_NOTE_PATH 为正确的路径
4. 运行 index.py 创建或更新索引
5. 运行 app.py
6. search anything

注意：如果要运行 index.py 重新创建索引，请先停止 app.py

![demo.gif](docs/demo.gif "")