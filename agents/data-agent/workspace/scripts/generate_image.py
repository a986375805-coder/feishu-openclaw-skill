import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse

DASHSCOPE_BASE = "https://dashscope.aliyuncs.com/api/v1"


def get_api_key():
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not key:
        print("ERROR: 环境变量 DASHSCOPE_API_KEY 未设置", file=sys.stderr)
        sys.exit(2)
    return key


def submit_task(key, prompt, size, n):
    url = f"{DASHSCOPE_BASE}/services/aigc/text2image/image-synthesis"
    body = {
        "model": "wanx-v1",
        "input": {"prompt": prompt, "negative_prompt": ""},
        "parameters": {"size": size, "n": n},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def poll_task(key, task_id, timeout=180, interval=5):
    url = f"{DASHSCOPE_BASE}/tasks/{task_id}"
    elapsed = 0
    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {key}"}, method="GET"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        status = data.get("output", {}).get("task_status", "")
        print(f"[{elapsed}s] status={status}")
        if status == "SUCCEEDED":
            return data
        if status == "FAILED":
            raise RuntimeError(f"生图失败: {json.dumps(data, ensure_ascii=False)}")
    raise TimeoutError(f"生图超时 ({timeout}s)")


def download(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(out_path, "wb") as f:
            f.write(resp.read())


def main():
    parser = argparse.ArgumentParser(description="通义万相 AI 生图")
    parser.add_argument("--prompt", required=True, help="图片描述（中文即可）")
    parser.add_argument("--size", default="1024*1024",
                        help="尺寸: 1024*1024 / 720*1280 / 1280*720 等")
    parser.add_argument("--n", type=int, default=1, help="生成张数 1-4")
    parser.add_argument("--out", default="output.png", help="输出文件路径")
    args = parser.parse_args()

    key = get_api_key()
    print(f"提交生图任务: prompt={args.prompt} size={args.size} n={args.n}")
    submit = submit_task(key, args.prompt, args.size, args.n)
    task_id = submit.get("output", {}).get("task_id", "")
    if not task_id:
        print(f"提交失败: {json.dumps(submit, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    print(f"task_id={task_id}")

    result = poll_task(key, task_id)
    results = result.get("output", {}).get("results", [])
    if not results:
        print("无结果", file=sys.stderr)
        sys.exit(1)

    saved = []
    for i, item in enumerate(results):
        url = item.get("url", "")
        if not url:
            continue
        path = args.out if i == 0 else f"{os.path.splitext(args.out)[0]}_{i+1}.png"
        download(url, path)
        saved.append(path)
        print(f"已保存: {path}")

    if not saved:
        print("下载失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
