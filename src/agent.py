from pathlib import Path
import time

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


# ==============================
# 1. 项目路径
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"


# ==============================
# 2. 加载 Embedding 模型
# ==============================

print("正在加载 Embedding 模型...")

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh-v1.5"
)

Settings.embed_model = embed_model

print("Embedding 模型加载完成")


# ==============================
# 3. 加载已经保存的向量索引
# ==============================

print("正在加载已保存的向量索引...")

storage_context = StorageContext.from_defaults(
    persist_dir=str(STORAGE_DIR)
)

index = load_index_from_storage(
    storage_context
)

print("向量索引加载完成")


# ==============================
# 4. 加载 Qwen3
# ==============================

llm = Ollama(
    model="qwen3:4b",
    request_timeout=120.0,
    context_window=2048
)

Settings.llm = llm

print("Qwen3 模型加载完成")


# ==============================
# 5. 创建 RAG 检索器
# ==============================

retriever = index.as_retriever(
    similarity_top_k=3
)


# ==============================
# 6. 医疗知识库检索函数
# ==============================

def medical_rag_search(question):

    nodes = retriever.retrieve(question)

    knowledge = []

    for node in nodes:
        knowledge.append(node.text)

    return "\n\n".join(knowledge)


# ==============================
# 7. AI Agent
# ==============================

def medical_agent(question):

    # --------------------------------
    # 第一步：Agent 判断是否需要 RAG
    # --------------------------------

    decision_prompt = f"""
你是智慧医疗系统中的任务判断模块。

你的任务是判断用户的问题是否属于医疗健康知识问题。

判断规则：

1. 只要用户的问题涉及疾病、症状、病因、危险因素、
预防、治疗、用药、健康管理、医学概念、检查、
医疗风险等医疗健康知识，就必须回答 SEARCH。

2. 医疗健康问题即使你自己知道答案，也必须回答 SEARCH，
不能因为你已有相关知识而选择 NO_SEARCH。

3. 只有明显不属于医疗健康知识的问题，例如普通闲聊、
打招呼、询问系统名称等，才回答 NO_SEARCH。

4. 只能回答 SEARCH 或 NO_SEARCH，不要输出其他内容。

用户问题：
{question}

你的判断：
"""

    decision = llm.complete(
        decision_prompt
    ).text.strip()

    print(f"[Agent] 任务判断：{decision}")


    # --------------------------------
    # 第二步：根据 Agent 判断决定是否检索
    # --------------------------------

    if decision == "SEARCH":

        print("[Agent] 调用医疗知识库检索工具...")

        knowledge = medical_rag_search(question)

        print("[Agent] 医疗知识检索完成")

    else:

        knowledge = "当前问题不需要查询医疗知识库。"

        print("[Agent] 本次不调用医疗知识库")


    # --------------------------------
    # 第三步：生成最终回答
    # --------------------------------

    final_prompt = f"""
你是智慧医疗问答系统。

请根据用户问题和医疗知识库检索结果生成回答。

用户问题：
{question}

医疗知识库检索结果：
{knowledge}

回答要求：

1. 优先依据医疗知识库内容回答。
2. 不要编造知识库中没有的信息。
3. 如果信息不足，应明确说明。
4. 对涉及疾病诊断、严重症状或用药的问题，
   不要代替医生进行诊断。
5. 回答简洁、清晰、准确。

请给出最终回答。
"""

    print("[Agent] 正在生成最终回答...")

    print("\nAI：", end="", flush=True)

    full_answer = ""

    try:

        response = llm.stream_complete(
            final_prompt
        )

        for chunk in response:

            print(
                chunk.delta,
                end="",
                flush=True
            )

            full_answer += chunk.delta

        print()

        return full_answer, False


    except KeyboardInterrupt:

        print("\n")

        print("================================")
        print("回答已中断")
        print("================================")

        return full_answer, True


# ==============================
# 8. 启动 AI Agent
# ==============================

print("\n================================")
print("智慧医疗 AI Agent 已启动")
print("你可以输入医疗问题进行咨询")
print("回答生成过程中按 Ctrl+C 可以中断")
print("输入 exit 可以退出程序")
print("================================")


# ==============================
# 9. 主循环
# ==============================

while True:

    try:

        question = input(
            "\n请输入医疗问题："
        ).strip()

    except KeyboardInterrupt:

        print("\n\n程序已退出。")
        break


    # --------------------------------
    # 输入 exit 退出
    # --------------------------------

    if question.lower() == "exit":

        print("\nAI Agent 已退出。")
        break


    # --------------------------------
    # 空问题
    # --------------------------------

    if not question:

        print("请输入问题后再提交。")
        continue


    # --------------------------------
    # 显示用户问题
    # --------------------------------

    print("\n================================")
    print("用户问题：")
    print(question)
    print("================================")


    # --------------------------------
    # 开始计时
    # --------------------------------

    start_time = time.perf_counter()


    # --------------------------------
    # 执行 Agent
    # --------------------------------

    try:

        answer, interrupted = medical_agent(
            question
        )

    except KeyboardInterrupt:

        print("\n")

        print("================================")
        print("本次回答已中断")
        print("================================")

        continue


    # --------------------------------
    # 结束计时
    # --------------------------------

    end_time = time.perf_counter()

    response_time = end_time - start_time


    # --------------------------------
    # 根据状态显示不同结果
    # --------------------------------

    if interrupted:

        print("\n================================")
        print("AI Agent 回答状态：已中断")
        print("================================")

    else:

        print("\n================================")
        print("AI Agent + RAG + Qwen3 回答生成完成")
        print("================================")


    # --------------------------------
    # 显示响应时间
    # --------------------------------

    print("\n--------------------------------")
    print(f"响应时间：{response_time:.2f} 秒")
    print("--------------------------------")