# 教师普查 AI 

这是一个为安徽省某财经大学的同学们开发的公益性 AI 选课情报平台。利用大语言模型（LLM）对碎片化的选课评价进行结构化分析，帮助大家在选课周快速避坑。

## 💡 为什么做这个项目？
老师好不好，适不适合选之类的各种讨论，全部分散在各个群聊和表白墙，有些还得不到解答，查询效率低。本项目通过在网页内集成收集问卷，快速获取教师上课情况，便于同学查询和选课。
## 🛠️ 技术实现
- **核心逻辑：** Streamlit 做的网页，SQLite的数据库，Deepseek给的AI。
- **AI模型：** Qwen2.5-3B-Int4 被我放弃了，6G 显存跑不动，启动一下显卡就嗷嗷叫，我怕给我二手游戏本跑炸了。然后换成 Deepseek 的 API 直接用。
- **数据存储：** SQLite 结构化存储课程与教师评价。
- **前端交互：** Streamlit 快速构建的 Web 界面。Cpolar免费内网穿透，开机挂上8080端口就是一个直接能用的网站。
## 🖼️ 示例截图
![主页](example/主页.jpg)
<img src="example/主页.jpg" alt="主页" width="33%" />
![查询](example/查询.jpg)
<img src="example/查询.jpg" alt="查询" width="33%" />
![问卷](example/问卷.jpg)
<img src="example/问卷.jpg" alt="问卷" width="33%" />
## 🤔 功能展望
- **新生知识库** 正在研究RAG，如果能在下一届学生入学前做完，就能提供一条龙服务（真

## 📂 项目结构
- `main.py`: 网页本体
- `RAG_assisstant3.py`: 大模型处理输入，提取关键词，送到数据库查询，再组织语言返回结果
- `data_utils2.py`: 网页显示和使用的数据库读写
- `database_query3.py`: 供AI查询和返回结果

## 🚀 运行
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
