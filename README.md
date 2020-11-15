# mdict-py

## 参考
本项目基于[MDX Server](https://github.com/ninja33/mdx-server)优化而来。
> 目前流行的 MDX 词典文件只能在 Mdict, GoldenDict, 欧路，深蓝等词典软件中使用，而不能将内容对外输出。MDX Server 通过读取 MDX、MDD 格式的词典文件，对外部提供一个标准的 HTTP 服务接口。使得一些需要词典服务的软件，比如 Kindlemate，Anki 划词助手以及其他工具可以利用这个本地服务，灵活选取所需的 MDX 词典，批量或者单独获取单词的解释。

MDX Server 核心功能由 [mdict-query](https://github.com/mmjang/mdict-query) 和 [PythonDictionaryOnline](https://github.com/amazon200code/PythonDictionaryOnline) 整合而成。

主要的优化点有：
1. 增加了一个查询页面，而不是通过url path传递参数，样式更加美观
2. 可以选择切换词典，可以自动识别中英文（如果有中文词典的话）
3. 增加拼写纠错


## 使用说明
```bash
1. git clone 本项目，将mdx放在根目录下面，如果mdx有独立css文件，放在static目录下面
2. 根据放入的mdx，修改mdx_server.py下面的DICTS_MAP里面的词典和static/index.html相对应。
3. >pip install -r requirements.txt
4. 启动mdx_server，打开http://localhost:8080
```

## TODO
- [ ] 动词的时态处理
- [ ] mdx返回结果包含mdd资源，无法获取
- [x] 增加中文词典

## 效果图
![mdict](./images/mdict.png)