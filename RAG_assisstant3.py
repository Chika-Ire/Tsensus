import json
import re
import os
from openai import OpenAI

os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

class API_Assistant:
    def __init__(self):

        self.api_key = "用你自己的API Key，我剩的十块钱全给Deepseek了，别用我的TAT"
        
        # OpenRouter 的固定接口地址
        self.client = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=self.api_key,
        )
        
        # 2. 指定模型 ID
        self.model_name = "deepseek-chat" 

    def extract_params(self, user_input):
        """一阶段：意图识别与参数提取 (交由大模型处理)"""
        prompt = """你是一个严谨的数据提取器和意图分析器。分析用户输入：
        1.如果用户在打招呼、问候、询问你是谁，或者提出与选课无关的测试问题，请识别为闲聊 (intent: "chat")。
        2.如果用户在询问课程信息、老师信息、或者与选课相关的问题，请识别为查询 (intent: "query")。
        如果是query,请提取教师姓名。如果没有提到某个信息，请填 null。

        请在query时严格返回JSON格式:{ "teacher_name": "xxx" or null, "intent": "query"}
        例如:
        {"course_name": "新媒体导论" or null, "teacher_name": "海猫" or null, "intent": "query"}
        {"course_name": "微积分" or null, "teacher_name": "李天翼" or null, "intent": "query"}

        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1, 
                max_tokens=150,
                response_format={"type": "json_object"} 
            )
            
            result_text = response.choices[0].message.content
            
            # 清洗并解析 JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"intent": "chat", "course_name": None, "teacher_name": None, "weekday": None}
            
        except Exception as e:
            print(f"[错误] API 提取失败: {e}")
            return {"intent": "chat", "course_name": None, "teacher_name": None, "weekday": None}

    def generate_final_answer(self, user_input, db_results):
        """二阶段：润色回答 (交由大模型处理)"""
        if not db_results:
            return "在这个数据库分身里，我还没学到这门课的信息。你可以尝试检查老师姓名或课程名是否准确。"
        
        # 构造 Context
        context_parts = []
        for i, r in enumerate(db_results, 1):
            info = (
                f"--- 评价 {i} ---\n"
                f"- 教师：{r.get('teacher_name', '未知')}\n"
                f"- 签到：{r.get('attendance_freq', '未记录')} (方式：{r.get('attendance_method', '未记录')})\n"
                f"- 点名政策：{r.get('roll_call', '未记录')} (逻辑：{r.get('roll_call_logic', '无')})\n"
                f"- 交互风格：{r.get('interaction_style', '未记录')}\n"
                f"- 考试重点：{r.get('exam_tips', '未记录')}\n"
                f"- 给分风格：{r.get('grading_style', '未记录')}\n"
                f"- 作业量：{r.get('workload', '未记录')}\n"
                f"- 其他备注：{r.get('special_notes', '无')}\n"
            )
            context_parts.append(info)

        context_str = "\n".join(context_parts)

            #提示词微调
        
        final_prompt = f"""你是一个严谨的选课分析助手。以下是关于该教师的【{len(db_results)}份学生真实评价】：
{context_str}
请根据以上评价回答用户的问题："{user_input}"。
如果存在多份评价，请你进行综合分析（例如：如果评价中对点名频率说法不一，请如实指出）。
【回答结构】
1. 总体印象（风格与给分）
2. 考勤细节（点名与签到）
3. 学习压力（作业与考试重点）
4. 其他备注
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": final_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.5, 
                max_tokens=512 
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[错误] API 生成回答失败: {e}")
            return "网络波动了一下，学姐和DeepSeek摸鱼去了，请稍后再试哦。"