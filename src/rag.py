from pathlib import Path
import time

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


# ============================================================
# 1. 项目路径
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"


# ============================================================
# 2. 加载中文 Embedding 模型
# ============================================================

print("正在加载 Embedding 模型...")

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh-v1.5"
)

Settings.embed_model = embed_model

print("Embedding 模型加载完成")


# ============================================================
# 3. 加载已经保存的向量索引
# ============================================================

print("正在加载已经保存的向量索引...")

storage_context = StorageContext.from_defaults(
    persist_dir=str(STORAGE_DIR)
)

index = load_index_from_storage(
    storage_context
)

print("向量索引加载完成")


# ============================================================
# 4. 加载本地 Qwen3 大语言模型
# ============================================================

llm = Ollama(
    model="qwen3:4b",
    request_timeout=120.0,
    context_window=2048
)

Settings.llm = llm

print("Qwen3 模型加载完成")


# ============================================================
# 5. 创建 RAG 检索器
# ============================================================

retriever = index.as_retriever(
    similarity_top_k=3
)


# ============================================================
# 6. 医疗知识库检索
# ============================================================

def medical_rag_search(question):

    nodes = retriever.retrieve(question)

    knowledge = []

    for node in nodes:
        knowledge.append(node.text)

    return "\n\n".join(knowledge), nodes


# ============================================================
# 7. RAG + Qwen3
# ============================================================

def rag_answer(question):

    # --------------------------------
    # 第一步：检索医疗知识
    # --------------------------------

    print("\n[RAG] 正在检索医疗知识库...")

    knowledge, nodes = medical_rag_search(question)

    print("[RAG] 医疗知识检索完成")


    # --------------------------------
    # 第二步：构造 Prompt
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


    # --------------------------------
    # 第三步：流式生成回答
    # --------------------------------

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

        return full_answer, nodes, False


    except KeyboardInterrupt:

        print("\n")

        print("================================")
        print("回答已中断")
        print("================================")

        return full_answer, nodes, True


# ============================================================
# 8. 启动 RAG 系统
# ============================================================

print("\n================================")
print("智慧医疗 RAG 系统已启动")
print("当前系统：B组（Qwen3 + RAG）")
print("回答生成过程中按 Ctrl+C 可以中断")
print("输入 exit 可以退出程序")
print("================================")


# ============================================================
# 9. 主循环
# ============================================================

while True:

    try:

        question = input(
            "\n请输入医疗问题："
        ).strip()

    except KeyboardInterrupt:

        print("\n\n程序已退出。")
        break


    # --------------------------------
    # 输入 exit
    # --------------------------------

    if question.lower() == "exit":

        print("\nRAG 系统已退出。")
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
    # 执行 RAG
    # --------------------------------

    try:

        answer, nodes, interrupted = rag_answer(
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


    # ========================================================
    # 10. 判断回答状态
    # ========================================================

    if interrupted:

        print("\n================================")
        print("B组回答状态：已中断")
        print("================================")

    else:

        print("\n================================")
        print("Qwen3 + RAG 回答生成完成")
        print("================================")


    # ========================================================
    # 11. 输出检索来源
    # ========================================================

    print("\n================================")
    print("RAG 检索到的知识片段")
    print("================================")


    for i, node in enumerate(
        nodes,
        start=1
    ):

        print(f"\n--- 知识片段 {i} ---")

        print(node.text)

        if node.score is not None:

            print(
                f"相似度：{node.score:.4f}"
            )


    # ========================================================
    # 12. 输出响应时间
    # ========================================================

    print("\n--------------------------------")
    print(
        f"响应时间：{response_time:.2f} 秒"
    )
    print("--------------------------------")