import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

# ================== 这里改成你的配置 ==================
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

MODEL_LIST = os.getenv("MODEL_LIST")                 # 你的模型列表文件，一行一个模型名
CONCURRENCY = os.getenv("CONCURRENCY")                        # 并发数报429就调低

TEST_PROMPT = os.getenv("TEST_PROMPT")
# ====================================================

async def test_model(client: AsyncOpenAI, model: str, semaphore: asyncio.Semaphore):
    """测试单个模型是否可用"""
    async with semaphore:
        try:
            start_time = time.time()
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": TEST_PROMPT}],
                max_tokens=20,
                timeout=60,  # 单个请求超时60秒，群友发消息，不是秒回才更像真人（？）
            )
            # 只要能返回响应就算成功
            latency = round((time.time() - start_time) * 1000, 2)
            print(f"✅ {model.ljust(40)} 可用 | 延迟: {latency}ms")
            # 顺便看看猫娘回应（？）
            print(response.choices[0].message.content)
            return model, True
        except Exception as e:
            error_msg = str(e).replace("\n", " ").strip()
            if "rate limit" in error_msg.lower():
                print(f"⚠️ {model.ljust(40)} 限流")
            elif "invalid" in error_msg.lower() or "not found" in error_msg.lower():
                print(f"❌ {model.ljust(40)} 不存在或不可用")
            else:
                print(f"❌ {model.ljust(40)} 失败: {error_msg}")
            return model, False


async def main():
    # 读取模型列表
    try:
        with open(MODEL_LIST, "r", encoding="utf-8") as f:
            models = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"📋 读取到 {len(models)} 个模型，开始测试...\n")
    except FileNotFoundError:
        print(f"❌ 未找到 {MODEL_LIST} 文件！")
        return

    if not models:
        print("⚠️ 模型列表为空，退出。")
        return

    # 创建客户端
    client = AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        timeout=20,
    )

    # 控制并发
    semaphore = asyncio.Semaphore(CONCURRENCY)

    # 并发测试所有模型
    tasks = [test_model(client, model, semaphore) for model in models]
    results = await asyncio.gather(*tasks)

    # 收集可用的模型
    alive_models = [model for model, success in results if success]

    # 写入可用模型文件
    with open("alive_models.txt", "w", encoding="utf-8") as f:
        for m in alive_models:
            f.write(m + "\n")

    print("\n" + "="*60)
    print(f"🎉 测试完成！共测试 {len(models)} 个模型，可用 {len(alive_models)} 个")
    print(f"💾 可用模型已保存至 alive_models.txt")
    if alive_models:
        print("\n可用模型列表：")
        for m in alive_models:
            print(f"    • {m}")

if __name__ == "__main__":
    print("🚀 开始批量测试API模型可用性...\n")
    asyncio.run(main())