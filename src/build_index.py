from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Settings
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# ============================================================
# 1. 获取项目根目录
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
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
# 3. 加载医疗知识库
# ============================================================

print("正在加载医疗知识库...")

documents = SimpleDirectoryReader(
    input_dir=str(KNOWLEDGE_DIR)
).load_data()

print(f"知识库加载完成，共 {len(documents)} 个文档")


# ============================================================
# 4. 建立向量索引
# ============================================================

print("正在建立向量索引...")

index = VectorStoreIndex.from_documents(documents)

print("向量索引建立完成")


# ============================================================
# 5. 保存向量索引
# ============================================================

print("正在保存向量索引...")

index.storage_context.persist(
    persist_dir=str(STORAGE_DIR)
)

print("向量索引保存完成！")
print(f"索引保存位置：{STORAGE_DIR}")