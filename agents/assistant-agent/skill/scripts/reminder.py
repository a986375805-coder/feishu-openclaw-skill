#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析自然语言提醒 → openclaw cron add 参数。

用法:
  python reminder.py parse "每天9点提醒我晨会"
  python reminder.py parse "下午3点提醒我喝水"
  python reminder.py parse "30分钟后提醒我休息"
  python reminder.py parse "明天10点提醒我开会"

输出 JSON: {"name": ..., "cron": ..., "at": ..., "message": ..., "friendly": ...}
"""
import json
import re
import sys
from datetime import datetime, timedelta

WEEKDAY_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 7, "天": 7,
}

def parse_time_in_text(text):
    """匹配 'X点' / 'X点半'，返回 hour, minute"""
    m = re.search(r"(\d{1,2})\s*点(?:\s*(\d{1,2}))?\s*分?", text)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    return hour, minute

def _adjust_period_text(text, hour, period=None):
    """根据时段词修正小时数。优先用已匹配的 period；否则从 text 里探测。"""
    p = period or ""
    if not p:
        if "下午" in text or "晚上" in text:
            p = "下午" if "下午" in text else "晚上"
        elif "中午" in text:
            p = "中午"
        elif "凌晨" in text:
            p = "凌晨"
    if p in ("下午", "晚上"):
        if hour < 12:
            hour += 12
    elif p == "中午" and hour < 12 and hour != 0:
        hour = hour  # 中午12点=12
    elif p == "中午" and hour == 12:
        hour = 12
    return hour

def parse(text):
    text_clean = text.strip()
    msg = None

    # 提取"提醒我/叫我/别忘了"之后的内容作为提醒事项
    m = re.search(r"(?:提醒我|提醒|叫我|别忘了|到点叫我)\s*(?:去|做|写|开|喝|吃|给|要)?\s*(.+)", text_clean)
    if m:
        msg = m.group(1).strip()
    if not msg:
        msg = text_clean

    # 1. 每天X点
    m = re.search(r"每天\s*(早上|上午|中午|下午|晚上|凌晨)?\s*(\d{1,2})\s*点", text_clean)
    if m:
        hour = int(m.group(2))
        hour = _adjust_period_text(text_clean, hour, m.group(1))
        cron = f"0 {hour} * * *"
        return {"name": f"每日{hour}点提醒", "cron": cron, "message": msg,
                "friendly": f"每天 {hour:02d}:00 提醒你：{msg}"}

    # 2. 每周X X点
    m = re.search(r"每?周([一二三四五六日天]{1,2})\s*(早上|上午|中午|下午|晚上|凌晨)?\s*(\d{1,2})\s*点", text_clean)
    if m:
        w = WEEKDAY_MAP.get(m.group(1))
        hour = int(m.group(3))
        hour = _adjust_period_text(text_clean, hour, m.group(2))
        if w:
            cron = f"0 {hour} * * {w}"
            return {"name": f"每周{m.group(1)}{hour}点提醒", "cron": cron, "message": msg,
                    "friendly": f"每周{m.group(1)} {hour:02d}:00 提醒你：{msg}"}

    # 3. X分钟后 / X小时后（一次性）
    m = re.search(r"(\d+)\s*分钟\s*后", text_clean)
    if m:
        return {"name": "一次性提醒", "at": f"+{m.group(1)}m", "message": msg,
                "friendly": f"{m.group(1)}分钟后提醒你：{msg}"}
    m = re.search(r"(\d+)\s*小时\s*后", text_clean)
    if m:
        return {"name": "一次性提醒", "at": f"+{int(m.group(1))*60}m", "message": msg,
                "friendly": f"{m.group(1)}小时后提醒你：{msg}"}

    # 4. 明天X点 / 今天X点（一次性）
    for day_delta, label in [(1, "明天"), (0, "今天")]:
        if f"{label}" in text_clean:
            tp = parse_time_in_text(text_clean)
            if tp:
                hour, minute = tp
                # 时段修正：下午/晚上/午夜
                hour = _adjust_period_text(text_clean, hour)
                when = datetime.now() + timedelta(days=day_delta)
                when = when.replace(hour=hour, minute=minute, second=0, microsecond=0)
                iso = when.strftime("%Y-%m-%dT%H:%M:%S+08:00")
                return {"name": f"{label}提醒", "at": iso, "message": msg,
                        "friendly": f"{label} {hour:02d}:{minute:02d} 提醒你：{msg}"}

    # 5. 直接"X点"（默认今天，若已过则明天）
    tp = parse_time_in_text(text_clean)
    if tp:
        hour, minute = tp
        hour = _adjust_period_text(text_clean, hour)
        now = datetime.now()
        when = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if when <= now:
            when += timedelta(days=1)
        iso = when.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        return {"name": f"{hour}点提醒", "at": iso, "message": msg,
                "friendly": f"{when.strftime('%Y-%m-%d %H:%M')} 提醒你：{msg}"}

    # 兜底
    return {"error": "未识别时间。请说清楚，如：每天9点 / 下午3点 / 30分钟后 / 明天10点"}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python reminder.py parse \"<提醒语句>\""}, ensure_ascii=False))
        sys.exit(1)
    result = parse(sys.argv[2])
    print(json.dumps(result, ensure_ascii=False))
