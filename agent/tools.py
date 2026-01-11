"""
LLM tools for XHS Text Agent.
Handles Qwen (通义千问) API calls and JSON parsing with retries.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple

from openai import OpenAI

from .prompts import (
    WEEKLY_GENERATION_PROMPT,
    REWRITE_DAY_PROMPT,
    WEEKLY_REVIEW_PROMPT,
    JSON_FIX_PROMPT
)
from .state import DayContent, WeeklyReview

# 通义千问 DashScope OpenAI 兼容接口
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-turbo"  # 可选: qwen-turbo, qwen-plus, qwen-max


def get_qwen_client() -> Tuple[Optional[OpenAI], Optional[str]]:
    """Get Qwen client via DashScope. Returns (client, error_message)."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return None, "未设置 DASHSCOPE_API_KEY 环境变量。请在 .env 文件中设置或导出环境变量。\n获取方式: https://dashscope.console.aliyun.com/apiKey"
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=DASHSCOPE_BASE_URL
        )
        return client, None
    except Exception as e:
        return None, f"千问客户端初始化失败: {str(e)}"


def call_llm(client: OpenAI, prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Make a simple LLM call and return the response text."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000
    )
    return response.choices[0].message.content.strip()


def parse_json_with_retry(client: OpenAI, text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Parse JSON with retry logic.
    1. First attempt: direct parse
    2. If fails: ask LLM to fix
    3. If still fails: return error
    
    Returns (parsed_dict, error_message)
    """
    # Clean up common issues
    cleaned = text.strip()
    
    # Remove markdown code blocks if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # First attempt
    try:
        result = json.loads(cleaned)
        return result, None
    except json.JSONDecodeError:
        pass
    
    # Second attempt: ask LLM to fix
    try:
        fix_prompt = JSON_FIX_PROMPT.format(text=text)
        fixed_text = call_llm(client, fix_prompt)
        
        # Clean again
        fixed_cleaned = fixed_text.strip()
        if fixed_cleaned.startswith("```json"):
            fixed_cleaned = fixed_cleaned[7:]
        elif fixed_cleaned.startswith("```"):
            fixed_cleaned = fixed_cleaned[3:]
        if fixed_cleaned.endswith("```"):
            fixed_cleaned = fixed_cleaned[:-3]
        fixed_cleaned = fixed_cleaned.strip()
        
        result = json.loads(fixed_cleaned)
        return result, None
    except Exception as e:
        return None, f"JSON 解析失败，请重试。错误: {str(e)}"


def generate_weekly_content(
    niche: str,
    goal: str,
    style: str,
    effort: str,
    constraints: List[str],
    custom_note: str
) -> Tuple[Optional[List[DayContent]], Optional[str]]:
    """
    Generate a 7-day content plan.
    Returns (list of DayContent, error_message)
    """
    client, error = get_qwen_client()
    if error:
        return None, error
    
    # Format constraints
    constraints_str = "、".join(constraints) if constraints else "无特别限制"
    custom_str = custom_note if custom_note else "无"
    
    prompt = WEEKLY_GENERATION_PROMPT.format(
        niche=niche,
        goal=goal,
        style=style,
        effort=effort,
        constraints=constraints_str,
        custom_note=custom_str
    )
    
    try:
        response_text = call_llm(client, prompt)
        parsed, parse_error = parse_json_with_retry(client, response_text)
        
        if parse_error:
            return None, parse_error
        
        # Convert to DayContent objects
        days = []
        for day_data in parsed.get("days", []):
            day_content = DayContent.from_dict(day_data)
            days.append(day_content)
        
        if len(days) != 7:
            return None, f"生成的内容天数不正确（期望7天，实际{len(days)}天），请重试。"
        
        return days, None
        
    except Exception as e:
        return None, f"生成内容时出错: {str(e)}"


def rewrite_day_content(
    day_content: DayContent,
    instruction: str
) -> Tuple[Optional[DayContent], Optional[str]]:
    """
    Rewrite a single day's content based on user instruction.
    Returns (new DayContent, error_message)
    """
    client, error = get_qwen_client()
    if error:
        return None, error
    
    prompt = REWRITE_DAY_PROMPT.format(
        title=day_content.title,
        hook=day_content.hook,
        bullets="、".join(day_content.bullets),
        cta=day_content.cta,
        tags="、".join(day_content.tags),
        instruction=instruction
    )
    
    try:
        response_text = call_llm(client, prompt)
        parsed, parse_error = parse_json_with_retry(client, response_text)
        
        if parse_error:
            return None, parse_error
        
        # Create new DayContent preserving day number
        new_content = DayContent(
            day=day_content.day,
            title=parsed.get("title", day_content.title),
            hook=parsed.get("hook", day_content.hook),
            bullets=parsed.get("bullets", day_content.bullets),
            cta=parsed.get("cta", day_content.cta),
            tags=parsed.get("tags", day_content.tags)
        )
        
        return new_content, None
        
    except Exception as e:
        return None, f"改写内容时出错: {str(e)}"


def generate_weekly_review(
    weekly_plan: List[DayContent],
    best_days: List[int],
    hardest_days: List[int],
    pace: str,
    notes: str
) -> Tuple[Optional[WeeklyReview], Optional[str]]:
    """
    Generate weekly review based on user feedback.
    Returns (WeeklyReview, error_message)
    """
    client, error = get_qwen_client()
    if error:
        return None, error
    
    # Build weekly summary
    summary_parts = []
    for day in weekly_plan:
        summary_parts.append(f"第{day.day}天: {day.title}")
    weekly_summary = "\n".join(summary_parts)
    
    # Format selections
    best_str = "、".join([f"第{d}天" for d in best_days]) if best_days else "未选择"
    hardest_str = "、".join([f"第{d}天" for d in hardest_days]) if hardest_days else "未选择"
    pace_str = pace if pace else "未选择"
    notes_str = notes if notes else "无"
    
    prompt = WEEKLY_REVIEW_PROMPT.format(
        weekly_summary=weekly_summary,
        best_days=best_str,
        hardest_days=hardest_str,
        pace=pace_str,
        notes=notes_str
    )
    
    try:
        response_text = call_llm(client, prompt)
        parsed, parse_error = parse_json_with_retry(client, response_text)
        
        if parse_error:
            return None, parse_error
        
        review = WeeklyReview.from_dict(parsed)
        return review, None
        
    except Exception as e:
        return None, f"生成复盘时出错: {str(e)}"

