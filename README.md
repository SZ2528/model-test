# 模型可用性测试工具

我改了一部分AI生成的代码

![面向AI编程](https://img.shields.io/badge/面向AI编程-AI生成-blue)

本工具用于批量测试不同AI模型的可用性。

## 食用方法

1. 复制 `.env.example` 文件为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 修改 `.env` 文件中的配置信息:
   - `BASE_URL`: API的基础URL
   - `API_KEY`: 你的API密钥
   - `CONCURRENCY`: 并发测试数（如果遇到429错误请调低）
   - `TEST_PROMPT`: 测试提示词

3. 创建 `models.txt` 文件，每行一个模型名称:
   ```
   gpt-3.5-turbo
   gpt-4
   claude-2
   ```

4. 运行测试:
   ```bash
   python model_test.py
   ```

5. 查看结果:
   - 测试完成后，可用模型将保存在 `alive_models.txt` 文件中