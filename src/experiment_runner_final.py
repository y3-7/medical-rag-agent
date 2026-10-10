# -*- coding: utf-8 -*-
from pathlib import Path
import argparse, json, re, time
from statistics import mean
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

BASE=Path(__file__).resolve().parent.parent
STORAGE=BASE/'storage'; OUT=BASE/'experiment_results'; OUT.mkdir(exist_ok=True)
RESULT=OUT/'智慧医疗RAG_A_B_C自动实验最终结果_v2.xlsx'

Q=[
(1,'什么是高血压？'),(2,'什么是2型糖尿病？它与胰岛素抵抗有什么关系？'),(3,'什么是冠心病？它与动脉粥样硬化有什么关系？'),(4,'什么是脑卒中？主要有哪些类型？'),(5,'什么是慢性阻塞性肺疾病（COPD）？'),(6,'流感和普通感冒有什么主要区别？'),(7,'高血压有哪些常见危险因素？'),(8,'2型糖尿病有哪些常见危险因素？'),(9,'吸烟为什么会增加心血管疾病风险？'),(10,'肥胖为什么会增加2型糖尿病风险？'),(11,'长期缺乏身体活动可能对健康产生哪些影响？'),(12,'为什么高盐饮食可能增加高血压风险？'),(13,'高血压通常应该如何进行健康管理？'),(14,'2型糖尿病患者在饮食管理方面通常需要注意什么？'),(15,'规律身体活动对慢性病和整体健康有什么作用？'),(16,'睡眠与身体健康有什么关系？'),(17,'成年人应该如何进行体重管理？'),(18,'慢性病为什么需要定期随访和长期管理？'),(19,'什么是收缩压和舒张压？'),(20,'什么是血糖？'),(21,'什么是糖化血红蛋白（HbA1c）？'),(22,'BMI是什么？如何计算？'),(23,'什么是动脉粥样硬化？'),(24,'什么是医疗人工智能中的“幻觉”？为什么需要关注？'),(25,'请综合说明高血压的基本概念、主要危险因素和健康管理方法。'),(26,'请比较高血压和2型糖尿病在危险因素和长期管理方面的异同。'),(27,'吸烟、肥胖和身体活动不足分别会怎样影响慢性病风险？'),(28,'请说明流感的主要特点、常见预防措施以及哪些情况需要及时就医。'),(29,'如果一个人出现胸痛，仅凭智能问答能否判断就是冠心病？应该如何安全处理？'),(30,'为什么医疗问答系统应优先参考权威、可更新的医学来源？来源和更新时间为什么重要？')]

R={
1:['高血压是血压持续升高的慢性疾病或状态','血压包括收缩压和舒张压','不能仅依据一次偶然测量诊断'],
2:['2型糖尿病是常见糖尿病类型','与胰岛素抵抗及不能有效利用胰岛素有关','长期血糖控制不佳可增加健康风险'],
3:['冠心病是冠状动脉相关心血管疾病','动脉粥样硬化是重要病理基础之一','冠脉供血受影响可导致心肌缺血'],
4:['脑卒中是脑部血液供应异常导致的急性神经系统疾病','主要包括缺血性和出血性卒中','突发神经异常应及时就医'],
5:['COPD是慢性呼吸系统疾病','通常有持续呼吸症状和气流受限','吸烟是重要危险因素'],
6:['流感由流感病毒引起且全身症状通常较明显','普通感冒可由多种呼吸道病毒引起','预防包括卫生习惯并可结合当地建议接种疫苗'],
7:['常见因素包括年龄、遗传、超重或肥胖','高盐饮食、活动不足、吸烟、过量饮酒等也可增加风险'],
8:['年龄、超重肥胖、活动不足、遗传家族史等相关','不健康饮食和代谢因素也可能增加风险'],
9:['吸烟损害心血管系统','增加心血管疾病及相关事件风险','戒烟有助于降低风险'],
10:['超重肥胖与2型糖尿病风险增加有关','体重管理、健康饮食和活动是重要措施'],
11:['活动不足与多种慢性非传染性疾病风险增加有关','规律活动有助于心血管、代谢和整体健康'],
12:['过多钠盐可能增加血压升高风险','减少高盐和高钠加工食品有助于血压管理'],
13:['包括生活方式干预、血压监测和必要时药物治疗','可包括控制体重、减盐、活动、戒烟、限制饮酒','药物调整或停药应由专业人员判断'],
14:['关注总体膳食质量、合理能量摄入和体重管理','保持均衡膳食并减少不健康饮食因素','具体方案应结合个人情况'],
15:['有助于心血管和代谢健康','有助于体重管理并降低多种慢性病风险','方式和强度应结合个人情况'],
16:['充足规律睡眠与身心健康有关','长期不足或质量差可能与多种健康问题相关','持续睡眠问题可寻求专业评估'],
17:['综合饮食、活动和生活方式','目标应长期可持续而非极端减重','必要时寻求专业指导'],
18:['慢性病通常需要长期管理','随访有助于监测控制情况和治疗效果','治疗调整应结合个体情况由专业人员判断'],
19:['收缩压是心脏收缩时的血压指标','舒张压是心脏舒张时的血压指标','二者共同描述血压水平'],
20:['血糖是血液中的葡萄糖水平','葡萄糖是重要能量来源之一','受饮食、激素和代谢状态影响'],
21:['HbA1c即糖化血红蛋白','可反映较长时期平均血糖控制情况','常用于糖尿病管理评估'],
22:['BMI是身体质量指数','通常为体重kg除以身高m的平方','不能单独代表全部健康状况'],
23:['动脉壁发生脂质等物质积聚及相关病理改变的慢性过程','可导致狭窄或斑块相关问题','与冠心病、脑卒中等风险有关'],
24:['医疗AI幻觉是看似合理但缺乏依据或与医学事实不符的生成内容','可能造成健康风险','可用权威知识、RAG、来源追踪和专业审核降低风险'],
25:['说明高血压是血压持续升高的慢性疾病或状态','提到多个主要危险因素','提到生活方式管理、监测及必要时专业治疗'],
26:['两者都是常见慢性病且需长期管理','都与遗传、体重、生活方式等有关但机制不完全相同','管理都可涉及饮食、活动、体重和监测'],
27:['吸烟增加心血管等风险','肥胖与多种代谢性慢病风险增加有关','活动不足与多种慢病风险增加有关'],
28:['流感由流感病毒引起且可有发热、咳嗽、乏力','预防包括疫苗、手卫生和减少传播','严重呼吸困难、意识异常、持续恶化等应及时就医'],
29:['不能仅凭聊天判断就是冠心病','胸痛原因多样且部分可危及生命','严重或突发胸痛、呼吸困难、意识异常等应及时急诊就医'],
30:['医学知识会更新，来源应可靠且有时效性','权威来源可减少错误和幻觉','来源与更新时间便于核查依据并判断是否过时']}

print('正在加载 Embedding 模型...'); Settings.embed_model=HuggingFaceEmbedding(model_name='BAAI/bge-small-zh-v1.5'); print('Embedding 模型加载完成')
print('正在加载 Qwen3...'); llm=Ollama(model='qwen3:4b',request_timeout=120.0,context_window=2048); Settings.llm=llm; print('Qwen3 模型加载完成')
print('正在加载独立评分器...'); evaluator_llm=Ollama(model='qwen3:4b',request_timeout=120.0,context_window=2048); print('评分器加载完成')
print('正在加载 RAG 向量索引...'); sc=StorageContext.from_defaults(persist_dir=str(STORAGE)); index=load_index_from_storage(sc); retriever=index.as_retriever(similarity_top_k=3); print('RAG 向量索引加载完成')

def gen(p): return str(llm.complete(p))
def eval_gen(p): return str(evaluator_llm.complete(p))
def retrieve(q):
    ns=retriever.retrieve(q); return '\n\n'.join(getattr(n,'text','') for n in ns)

def A(q):
    return gen(f'''你是智慧医疗问答系统。请根据已有知识回答：{q}\n要求：清晰准确；不要故意编造；涉及诊断、严重症状或用药时不要代替医生；无法确定要说明；如果引用医学指南或机构，请尽量明确来源名称。'''),''
def B(q):
    k=retrieve(q); return gen(f'''你是智慧医疗RAG问答系统。用户问题：{q}\n医疗知识库：{k}\n要求：优先依据知识库；知识库不足要说明；不要把未被支持的内容说成知识库结论；医疗问题注意安全边界；如有来源可说明。'''),k
def C(q):
    d=gen(f'''你是智慧医疗AI Agent任务规划模块。判断是否需要医疗知识库检索。问题：{q}\n医学事实、疾病知识、健康管理、医疗安全或需要可靠来源时输出SEARCH；简单闲聊输出NO_SEARCH。只输出SEARCH或NO_SEARCH。''').strip().upper()
    k=retrieve(q) if ('SEARCH' in d and 'NO_SEARCH' not in d) else ''
    p=f'''你是智慧医疗AI Agent。用户问题：{q}\n'''+('已调用医疗知识库，检索内容：'+k if k else '本次Agent判断不需要知识库检索。')+'''\n请完成最终回答。要求：优先依据检索内容；不要编造；信息不足说明；医疗问题注意安全边界；如有来源可说明。'''
    return gen(p),k

EVAL='''你是医学问答实验的独立评分器。只进行评分，不聊天。

请严格输出一行，格式必须是：A,C,T,H|简短理由
其中：A=准确性1-5，C=完整性1-5，T=可追溯性0-5，H=明确医学事实错误或幻觉数量（整数）。
不要输出JSON，不要输出百分制，不要寒暄，不要复述题目。

准确性：5=核心事实基本全对；4=总体正确但有少量遗漏；3=部分正确；2=核心有明显错误；1=核心错误/严重误导/基本未回答。
完整性：5=基本覆盖全部参考要点；4=覆盖大部分；3=覆盖部分；2=覆盖较少；1=基本未回答。
可追溯性：5=核心结论有明确、可靠、可核查来源；4=大部分有来源；3=部分；2=少量；1=几乎没有；0=没有。A组没有RAG不等于0，若明确提供可核查权威来源可得相应分数。B/C使用RAG也不能机械加分。
幻觉数：只统计明确错误、虚构或明显无医学依据的医学断言；同一错误只算1次；知识库未覆盖但医学上正确的补充，不直接算幻觉。
'''


def _level_to_score(value, low=1, high=5):
    """把中文等级/英文等级转换成1-5分。"""
    s = str(value).strip().lower()
    mapping = {
        "极高": 5, "很高": 5, "高": 5, "优秀": 5, "优": 5, "excellent": 5,
        "较高": 4, "良好": 4, "好": 4, "good": 4,
        "中": 3, "中等": 3, "一般": 3, "moderate": 3,
        "较低": 2, "偏低": 2, "低": 1, "差": 1, "poor": 1,
    }
    if s in mapping:
        return mapping[s]
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if m:
        n = float(m.group())
        if n > 5:
            return max(low, min(high, round(n / 20)))
        return max(low, min(high, int(round(n))))
    return None


def _find_value(raw, patterns):
    for pat in patterns:
        m = re.search(pat, raw, re.I | re.S)
        if m:
            return m.group(1).strip()
    return None


def extract_score(raw):
    """
    宽松解析评分器输出。

    支持：
    1) 标准JSON
    2) “准确性：5 / 完整性：4 / 可追溯性：5 / 幻觉数：0”
    3) “准确性评分：90分 / 完整性评分：75分 / 信息源评分：95分”
    4) “准确性：高 / 完整性：高 / 可追溯性：高 / 幻觉数：0”
    """
    raw = str(raw).strip()
    cleaned = raw.replace("```json", "").replace("```", "").strip()

    # ---------- 0. 一行数字格式：A,C,T,H|理由 ----------
    m = re.search(r"(?<!\d)([1-5])\s*[,，|/]\s*([1-5])\s*[,，|/]\s*([0-5])\s*[,，|/]\s*(\d+)(?:\s*\|\s*(.*))?$", cleaned, re.M)
    if m:
        return {
            "accuracy": int(m.group(1)),
            "completeness": int(m.group(2)),
            "traceability": int(m.group(3)),
            "hallucination_count": int(m.group(4)),
            "reason": (m.group(5) or "").strip()[:500],
        }

    # ---------- 1. 优先解析JSON ----------
    for obj in re.findall(r"\{.*?\}", cleaned, re.S):
        try:
            d = json.loads(obj)
            if all(k in d for k in
                   ["accuracy", "completeness", "traceability", "hallucination_count"]):
                return {
                    "accuracy": max(1, min(5, int(float(d["accuracy"])))),
                    "completeness": max(1, min(5, int(float(d["completeness"])))),
                    "traceability": max(0, min(5, int(float(d["traceability"])))),
                    "hallucination_count": max(0, int(float(d["hallucination_count"]))),
                    "reason": str(d.get("reason", d.get("evaluation", "")))[:500],
                }
        except Exception:
            pass

    # ---------- 2. 普通中文/英文结构化评分 ----------
    acc_raw = _find_value(cleaned, [
        r"准确性(?:评分)?\s*[:：]\s*([^\n]+)",
        r"准确\s*[:：]\s*([^\n]+)",
        r"accuracy\s*[:：]\s*([^\n]+)",
    ])
    comp_raw = _find_value(cleaned, [
        r"完整性(?:评分)?\s*[:：]\s*([^\n]+)",
        r"完整\s*[:：]\s*([^\n]+)",
        r"completeness\s*[:：]\s*([^\n]+)",
    ])
    trace_raw = _find_value(cleaned, [
        r"(?:可追溯性|信息源|来源)(?:评分)?\s*[:：]\s*([^\n]+)",
        r"traceability\s*[:：]\s*([^\n]+)",
    ])
    hall_raw = _find_value(cleaned, [
        r"幻觉(?:数|数量|/事实错误|错误数)?\s*[:：]\s*(\d+)",
        r"事实错误(?:数|数量)?\s*[:：]\s*(\d+)",
        r"hallucination_count\s*[:：]\s*(\d+)",
    ])

    # 处理“90分”“75分”“95分”等百分制
    def parse_percent_or_level(v, low=1, high=5):
        if v is None:
            return None
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:分|%)?", v)
        if m:
            n = float(m.group(1))
            if n > 5:
                return max(low, min(high, round(n / 20)))
            return max(low, min(high, int(round(n))))
        return _level_to_score(v, low, high)

    accuracy = parse_percent_or_level(acc_raw, 1, 5)
    completeness = parse_percent_or_level(comp_raw, 1, 5)
    traceability = parse_percent_or_level(trace_raw, 0, 5)

    hallucination = None
    if hall_raw is not None:
        m = re.search(r"\d+", hall_raw)
        if m:
            hallucination = max(0, int(m.group()))

    # ---------- 3. 从“优秀/无缺失/无错误”补足信息 ----------
    if accuracy is None and re.search(r"准确无误|完全正确|优秀|excellent", cleaned, re.I):
        accuracy = 5
    if completeness is None and re.search(r"完整覆盖|全部覆盖|无缺失信息|完整", cleaned):
        completeness = 5
    if traceability is None and re.search(r"信息源评分|来源评分|可追溯性[：:]\s*(?:高|优秀)", cleaned):
        traceability = 5
    if hallucination is None and re.search(r"无幻觉|没有幻觉|无事实错误|没有事实错误", cleaned):
        hallucination = 0

    # 至少需要四个核心字段才能作为有效评分。
    if accuracy is not None and completeness is not None and traceability is not None and hallucination is not None:
        return {
            "accuracy": accuracy,
            "completeness": completeness,
            "traceability": traceability,
            "hallucination_count": hallucination,
            "reason": cleaned[:500],
        }

    return None


def score(qid, q, system, ans, k):
    reference = "\n".join("- " + x for x in R[qid])
    # 控制输入长度，避免2048上下文窗口下评分提示被挤压。
    answer_for_eval = str(ans)[-2400:]
    evidence_for_eval = (k or "本次无RAG证据。")[:2600]
    prompt = f"""{EVAL}
测试题：{q}
参考要点：
{reference}
被评估系统：{system}
系统回答：
{answer_for_eval}
RAG证据：
{evidence_for_eval}

现在只输出一行 A,C,T,H|理由。"""

    last = ""
    prompts = [
        prompt,
        prompt + "\n再次提醒：只允许一行，例如 5,5,4,0|回答基本完整且无明显事实错误。",
        f"只输出一行四个数字和一句理由：5,5,4,0|理由。不要JSON。\n题目：{q}\n回答：{answer_for_eval}\n参考要点：{reference}",
    ]
    for attempt, pp in enumerate(prompts, 1):
        raw = eval_gen(pp)
        last = str(raw).strip()
        parsed = extract_score(last)
        if parsed is not None:
            return parsed
        print(f"[评分器重试 {attempt}/3] 未得到有效评分格式，原始输出：{last[:300]!r}")

    return {
        "accuracy": None,
        "completeness": None,
        "traceability": None,
        "hallucination_count": None,
        "reason": "评分器输出无法自动解析，已保留原始评分输出，待人工复核。",
        "_score_failed": True,
        "_raw_score": last[:1000],
    }

HEAD=['题号','测试问题','系统','第几次','回答','准确性(1-5)','完整性(1-5)','可追溯性(0-5)','幻觉/事实错误数','响应时间(秒)','自动评分说明','备注']
def wbload():
    if RESULT.exists(): return load_workbook(RESULT)
    w=Workbook(); s=w.active; s.title='实验记录'; s.append(HEAD)
    a=w.create_sheet('评分说明'); a.append(['指标','规则']); a.append(['准确性','1-5分']); a.append(['完整性','1-5分']); a.append(['可追溯性','0-5分，按可靠且可核查来源判断，不按是否RAG机械赋分']); a.append(['幻觉/事实错误数','医学事实错误或明显无依据医学断言数量']); a.append(['综合质量分','准确性40% + 完整性25% + 可追溯性20% + 无幻觉率15%']); a.append(['说明','自动评分需人工抽查，不作为绝对金标准；评分器无法解析的记录保留回答并标记待人工复核，不阻塞后续实验'])
    w.create_sheet('每题平均结果'); w.create_sheet('最终总成绩'); return w

def summary(w):
    s=w['实验记录']; rows=list(s.iter_rows(min_row=2,values_only=True))
    for name in ['每题平均结果','最终总成绩']:
        ws=w[name]
        if ws.max_row: ws.delete_rows(1,ws.max_row)
    a=w['每题平均结果']; a.append(['题号','测试问题','系统','平均准确性','平均完整性','平均可追溯性','平均幻觉/事实错误数','平均响应时间(秒)','幻觉出现率'])
    for qid,q in Q:
        for sys in 'ABC':
            z=[r for r in rows if r[0]==qid and r[2]==sys and r[5] is not None]
            if not z: continue
            a.append([qid,q,sys,round(mean(r[5] for r in z),3),round(mean(r[6] for r in z),3),round(mean(r[7] for r in z),3),round(mean(r[8] for r in z),3),round(mean(r[9] for r in z),3),round(sum(r[8]>0 for r in z)/len(z),4)])
    t=w['最终总成绩']; t.append(['系统','平均准确性','平均完整性','平均可追溯性','平均幻觉/事实错误数','幻觉出现率','平均响应时间(秒)','无幻觉率','综合质量分(100)','排名'])
    ss=[]
    for sys in 'ABC':
        z=[r for r in rows if r[2]==sys and r[5] is not None]
        if not z: continue
        acc=mean(r[5] for r in z); comp=mean(r[6] for r in z); tr=mean(r[7] for r in z); hall=mean(r[8] for r in z); hr=sum(r[8]>0 for r in z)/len(z); rt=mean(r[9] for r in z); no=1-hr
        quality=acc/5*100*.4+comp/5*100*.25+tr/5*100*.2+no*100*.15
        ss.append((quality,sys,acc,comp,tr,hall,hr,rt,no))
    ss.sort(reverse=True)
    for rank,x in enumerate(ss,1):
        quality,sys,acc,comp,tr,hall,hr,rt,no=x; t.append([sys,round(acc,3),round(comp,3),round(tr,3),round(hall,3),round(hr,4),round(rt,3),round(no,4),round(quality,2),rank])
    for ws in w.worksheets:
        for c in ws[1]: c.font=Font(bold=True); c.alignment=Alignment(horizontal='center')
        ws.freeze_panes='A2'
        for col in range(1,ws.max_column+1):
            mx=max((len(str(c.value)) for c in ws[get_column_letter(col)] if c.value is not None),default=8)
            ws.column_dimensions[get_column_letter(col)].width=min(max(mx+2,10),45)
        for row in ws.iter_rows():
            for c in row: c.alignment=Alignment(vertical='top',wrap_text=True)

def run(sys, repeats, limit):
    w = wbload()
    s = w['实验记录']
    # key -> Excel row number；已有失败记录可以在本次运行中被覆盖重试。
    row_by_key = {}
    done_valid = set()
    for excel_row, r in enumerate(s.iter_rows(min_row=2, values_only=True), start=2):
        if r[0] is None or r[2] is None or r[3] is None:
            continue
        key = (int(r[0]), str(r[2]), int(r[3]))
        row_by_key[key] = excel_row
        if r[5] is not None and r[6] is not None and r[7] is not None and r[8] is not None:
            done_valid.add(key)

    qs = Q[:limit] if limit else Q
    fn = {'A': A, 'B': B, 'C': C}
    total_plan = len(qs) * repeats
    print(f"\n本组计划：{total_plan} 次；已有有效记录：{sum(1 for k in done_valid if k[1] == sys)}")

    for qid, q in qs:
        for rep in range(1, repeats + 1):
            key = (qid, sys, rep)
            if key in done_valid:
                print(f'[跳过] {sys} | Q{qid} | 第{rep}次（已有有效评分）')
                continue

            print('\n' + '-' * 70 + f'\n{sys}组 | Q{qid} | 第{rep}次\n{q}\n' + '-' * 70)
            st = time.perf_counter()
            try:
                ans, k = fn[sys](q)
                elapsed = time.perf_counter() - st
                print('\nAI回答：\n' + ans + f'\n\n系统响应时间：{elapsed:.2f}秒')
                print('正在自动评分...')
                sc = score(qid, q, sys, ans, k)

                note_base = {'A': 'A组无RAG；可追溯性按统一来源可核查标准评分。',
                             'B': 'B组使用RAG检索结果。',
                             'C': 'C组使用Agent并按需调用RAG。'}[sys]

                if sc.get('_score_failed'):
                    print('[警告] 自动评分无法解析，本条保存为“待人工复核”，后续运行会优先重试。')
                    print('评分器原始输出：\n' + sc.get('_raw_score', ''))
                    row_values = [qid, q, sys, rep, ans, None, None, None, None,
                                  round(elapsed, 2), sc.get('reason', '') + '\n原始评分输出：' + sc.get('_raw_score', ''),
                                  note_base + ' 自动评分失败，待人工复核。']
                else:
                    print(f"评分：准确={sc['accuracy']} 完整={sc['completeness']} 可追溯={sc['traceability']} 幻觉={sc['hallucination_count']}\n说明：{sc.get('reason', '')}")
                    row_values = [qid, q, sys, rep, ans, sc['accuracy'], sc['completeness'],
                                  sc['traceability'], sc['hallucination_count'], round(elapsed, 2),
                                  sc.get('reason', ''), note_base]

                if key in row_by_key:
                    for col, value in enumerate(row_values, start=1):
                        s.cell(row=row_by_key[key], column=col, value=value)
                    excel_row = row_by_key[key]
                else:
                    s.append(row_values)
                    excel_row = s.max_row
                    row_by_key[key] = excel_row

                summary(w)
                w.save(RESULT)

                if not sc.get('_score_failed'):
                    done_valid.add(key)
                print('√ 本次结果已保存并继续')
                print(f'本组当前有效评分记录：{sum(1 for x in done_valid if x[1] == sys)} 条')

            except KeyboardInterrupt:
                summary(w)
                w.save(RESULT)
                print('\n已中断，已保存当前结果。')
                return
            except Exception as e:
                print('[本题错误]', repr(e))
                print('本题未完成，将继续下一题。')
                continue

    summary(w)
    w.save(RESULT)
    print('\n本轮完成：', RESULT)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--system',choices=['A','B','C','ALL'],default='ALL'); p.add_argument('--repeats',type=int,default=3); p.add_argument('--limit',type=int,default=None); a=p.parse_args()
    if a.system=='ALL':
        for x in 'ABC': run(x,a.repeats,a.limit)
    else: run(a.system,a.repeats,a.limit)
if __name__=='__main__': main()
