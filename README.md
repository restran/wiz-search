# 为知搜

Mac 版的为知笔记在没有网络的时候，无法使用全文搜索。使用 whoosh 和 jieba 分词建立了离线搜索功能。

## 使用方法

1. 复制 config.py.example 为 config.py
2. 修改 WIZ_NOTE_PATH 为正确的路径
3. 运行 index.py 创建或更新索引
4. 启动 app.py 
5. search anything

