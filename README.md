\# Medical RAG + Agent：智慧医疗智能问答原型



A local medical question-answering prototype based on RAG, Qwen3 and a workflow-based AI Agent.



\## 1. 项目简介



本项目是一个面向课程实验的智慧医疗智能问答原型，主要探索大语言模型、检索增强生成（Retrieval-Augmented Generation，RAG）与 AI Agent 在一般医疗健康信息问答中的结合方式。



项目通过构建中文医疗知识库，为大语言模型提供外部知识检索能力，并使用流程式 Agent 判断是否需要调用检索模块。同时，通过对比实验观察不同系统配置在回答质量和响应时间方面的表现。



本项目用于学习、课程实践与技术验证，不用于真实医疗诊断、处方或治疗决策。



\## 2. 主要功能



\- 构建中文医疗健康知识库。

\- 使用文本嵌入模型将知识转换为向量表示。

\- 使用 LlamaIndex 构建和加载向量索引。

\- 使用本地大语言模型生成问答内容。

\- 通过流程式 Agent 判断是否调用医疗知识检索模块。

\- 比较普通 LLM、LLM + RAG、LLM + RAG + Agent 三种配置。

\- 记录回答评价指标和响应时间。



\## 3. 技术栈



\- Python 3.12

\- Ollama

\- Qwen3:4B

\- BAAI/bge-small-zh-v1.5

\- LlamaIndex

\- Openpyxl



\## 4. 项目目录



```text

medical\_rag/

├── src/                  # RAG、索引构建与实验程序

├── knowledge/            # 医疗知识库文本

├── storage/              # 持久化向量索引

├── experiment\_results/   # 实验记录与结果

├── requirements.txt      # Python 依赖清单

├── .gitignore            # Git 忽略规则

└── README.md             # 项目说明文档

```



\## 5. 环境准备



建议使用 Python 3.12，并提前安装 Git 和 Ollama。



创建虚拟环境并安装 Python 依赖：



```bat

python -m venv venv2

venv2\\Scripts\\activate

python -m pip install -r requirements.txt

```



在 Ollama 中准备 Qwen3 模型：



```bat

ollama pull qwen3:4b

ollama list

```



\## 6. 运行方法



以下命令均在项目根目录下执行。



如果已有可用的 `storage` 索引，可以直接进行 RAG 实验。若索引不存在，或者医疗知识库内容发生变化，则先执行：



```bat

python src\\build\_index.py

```



分别运行三组实验：



```bat

python src\\experiment\_runner\_final.py --system A --repeats 3 --limit 30

```



```bat

python src\\experiment\_runner\_final.py --system B --repeats 3 --limit 30

```



```bat

python src\\experiment\_runner\_final.py --system C --repeats 3 --limit 30

```



A 组为普通 LLM，B 组为 LLM + RAG，C 组为 LLM + RAG + Agent。



实验结果默认保存在 `experiment\_results` 目录中。程序的具体运行参数以实际代码为准。



\## 7. 实验说明



## 7. 实验说明

本项目使用固定测试题，对普通 LLM、LLM + RAG、LLM + RAG + Agent 等配置进行对比，并记录回答质量与响应时间。实验脚本支持重复测试和将结果保存到 Excel 文件。

实验结果以 `experiment_results` 目录中实际保存的数据为准。自动评分结果可能存在偏差，部分结果需要人工复核。本项目实验结论仅适用于当前测试题、模型配置、运行环境和评价方法，不代表模型具备真实临床诊断能力。



\## 8. 安全与使用限制



\- 本项目仅用于学习、课程实验和一般健康信息服务探索。

\- 系统不能替代医生的诊断、处方或治疗决策。

\- 对疑似急症、个体化用药及高风险医疗问题，应寻求专业医疗人员帮助。

\- 医疗知识库中的资料应保留来源信息，并遵守原始资料的引用、使用和再分发要求。

\- 请勿提交真实患者隐私、密码、访问令牌或其他敏感信息。



\## 9. 后续改进方向



\- 扩充医疗知识库并改进来源管理。

\- 评估检索相关性，探索重排序等检索优化方法。

\- 改进 Agent 的检索路由策略和异常处理。

\- 引入人工或专业人员盲评，进一步验证自动评分结果。





