# team_leader的功能是将用户的设计任务分类，设计任务流程。这里我们选择用Deepseek-v3作为llm。对于较小的项目，我们会直接让coder试图用单代码解决问题。
import os
from simplemetagpt.core.llm import AlibabaDeepseekV3LLM
from simplemetagpt.core.pipe import BasePipe
from dotenv import load_dotenv
load_dotenv()
#
