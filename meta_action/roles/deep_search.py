from meta_action.extensions import google_custom_search, alibaba_deepseekV3_llm_api
import re

# User input
user_input = "芙宁娜在原神剧情里都做过哪些滑稽的事?"

# Initialize history for tracking rounds
history = ""
round_num = 1

# Loop until sufficient information is gathered
while True:
    # Step 1: Generate search query
    query_step1 = f"""
    用户问题：[{user_input}]

    检索query生成规则：
    1. 提取关键词：从用户问题中提取核心关键词或短语，确保这些关键词能够准确反映用户的需求。
    2. 去除冗余信息：去掉不必要的修饰词、语气词或重复信息，保留核心内容。
    3. 优化格式：将关键词组合成简洁的英文查询语句，适合搜索引擎直接使用。
    4. 保持简洁：去掉不必要的修饰词，确保query简洁明了。

    请生成一个英文检索query。
    """
    step1 = alibaba_deepseekV3_llm_api.pipe(query_step1)[1]
    
    # Extract the query from step1 output (assuming it’s a plain string or prefixed text)
    match = re.search(r'The query is: (.*)|query: (.*)', step1)
    if match:
        search_query = match.group(1) or match.group(2)
    else:
        search_query = step1.split('\n')[-1]  # Fallback to raw output
    print(f"Round {round_num} - Generated Query: {search_query}")
    if not search_query:raise Exception(step1)
    # Step 2: Perform Google Custom Search
    step2 = google_custom_search.pipe(search_query)[1]
    print(f"Round {round_num} - Search Results:\n{step2}")

    # Step 3: Summarize search results
    query_step3 = f"""
    用户问题: [{user_input}]
    搜索内容: {search_query}
    检索结果:
    {step2}

    请执行以下任务：
    1. **提取有用信息**：
       - 从检索结果中提取与用户问题相关的信息。
       - 对于每个有用的页面，简要说明从中可以了解到什么。
    2. **决定是否进一步检索**：
       - 如果当前信息足够回答用户问题，请说明“信息充足”。
       - 如果需要更多信息，请生成一个新的英文检索query，并说明原因。

    输出格式：
    **有用信息**：
    - Page[1]: ...
    - Page[2]: ...
    ...

    **进一步检索**：
    - 需要/不需要
    - 如果需要，新的query是: <new_query>
    - 原因: ...
    """
    step3 = alibaba_deepseekV3_llm_api.pipe(query_step3)[1]
    print(f"Round {round_num} - Summary:\n{step3}")

    # Update history
    history += f"**Round {round_num}**\n检索query: {search_query}\n总结:\n{step3}\n\n"
    round_num += 1

    # Step 4: Decide to stop or continue
    query_step4 = f"""
    用户问题：[{user_input}]
    历史检索:
    {history}

    请执行以下任务：
    1. **综合历史信息**：
       - 综合所有历史检索中的有用信息。
    2. **判断信息充足性**：
       - 如果信息足够回答用户问题，请生成一个专业的分析报告。
       - 如果信息不足，请生成一个新的英文检索query，并说明需要哪些额外信息。

    输出格式：
    **信息充足性**：
    - 充足/不足

    **如果充足**：
    **分析报告**：
    [在此处提供详细的分析和答案]

    **如果不足**：
    **新的检索query**： <new_query>
    **原因**： [说明需要哪些额外信息]
    """
    step4 = alibaba_deepseekV3_llm_api.pipe(query_step4)[1]
    print(f"Round {round_num-1} - Decision:\n{step4}")

    # Check if information is sufficient
    if "- 充足" in step4 or "- sufficient" in step4.lower():
        # Extract and display the final report
        report_start = step4.find("**分析报告**：") + len("**分析报告**：")
        final_report = step4[report_start:].strip() if report_start > len("**分析报告**：") else "No detailed report provided."
        print(f"Final Report:\n{final_report}")
        break
    else:
        # Extract new query for the next iteration
        match = re.search(r'新的检索query.*?：\s*(.+?)(?:\n|$)|new query.*?：\s*(.+?)(?:\n|$)', step4, re.IGNORECASE)
        if match:
            search_query = match.group(1) or match.group(2)
        else:
            print("Failed to extract new query. Stopping.")
            break