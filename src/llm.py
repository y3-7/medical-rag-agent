import time

from llama_index.llms.ollama import Ollama


# ==============================
# 加载 Qwen3
# ==============================

print("正在加载 Qwen3 模型...")

llm = Ollama(
    model="qwen3:4b",
    request_timeout=120.0,
    context_window=2048
)

print("Qwen3 模型加载完成")


# ==============================
# 普通 LLM 回答
# ==============================

def llm_answer(question):

    prompt = f"""
你是一个智慧医疗问答系统。

请根据你的已有知识回答用户的问题。

用户问题：
{question}

回答要求：

1. 回答清晰、准确。
2. 不要故意编造信息。
3. 对医疗问题给出适当的健康知识说明。
4. 涉及疾病诊断、严重症状或用药时，
   不要代替医生进行诊断或治疗。
5. 如果无法确定，应明确说明。

请给出最终回答。
"""

    print("\nAI：", end="", flush=True)

    full_answer = ""

    try:

        response = llm.stream_complete(prompt)

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
# 主程序
# ==============================

print("\n================================")
print("智慧医疗普通 LLM 系统已启动")
print("当前系统：A组（Qwen3）")
print("回答生成过程中按 Ctrl+C 可以中断")
print("输入 exit 可以退出程序")
print("================================")


while True:

    try:

        question = input(
            "\n请输入医疗问题："
        ).strip()

    except KeyboardInterrupt:

        print("\n\n程序已退出。")
        break

    if question.lower() == "exit":

        print("\n普通 LLM 系统已退出。")
        break

    if not question:

        print("请输入问题后再提交。")
        continue

    print("\n================================")
    print("用户问题：")
    print(question)
    print("================================")

    start_time = time.perf_counter()

    try:

        answer, interrupted = llm_answer(
            question
        )

    except KeyboardInterrupt:

        print("\n")
        print("================================")
        print("本次回答已中断")
        print("================================")

        continue

    end_time = time.perf_counter()

    response_time = end_time - start_time

    if interrupted:

        print("\n================================")
        print("A组回答状态：已中断")
        print("================================")

    else:

        print("\n================================")
        print("Qwen3 普通 LLM 回答生成完成")
        print("================================")

    print("\n--------------------------------")
    print(
        f"响应时间：{response_time:.2f} 秒"
    )
    print("--------------------------------")