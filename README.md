# 小红书创作小白 · 文字内容生成

一个帮助小红书新手创作者规划一周文字内容的 AI 助手。

## 🎯 产品功能

这是一个**纯文字内容生成工具**，帮助你：

- 📝 根据你的赛道、目标、风格偏好生成 7 天内容计划
- 👀 查看每天的完整内容（标题、开头、要点、CTA、标签）
- ✏️ 根据你的要求改写任意一天的内容
- 📊 周复盘：选择感觉最好/最难的内容，获取下周建议

**注意**：本工具仅生成文字内容，不包含图片/视频生成、发布排期或平台对接功能。

## 🚀 快速开始

### 1. 克隆或下载项目

```bash
cd xhs-text-agent
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 设置通义千问 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey) 获取 API Key

2. 复制示例环境变量文件：

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，填入你的 DashScope API Key：

```
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
```

或者直接导出环境变量：

```bash
export DASHSCOPE_API_KEY=sk-your-dashscope-api-key
```

### 5. 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

## 📸 截图

> [待补充截图]

### Onboarding 流程
![Onboarding](screenshots/onboarding.png)

### 周计划视图
![Weekly Plan](screenshots/weekly-plan.png)

### 内容详情
![Day Content](screenshots/day-content.png)

## 🏗️ 项目结构

```
xhs-text-agent/
├── app.py              # Streamlit 主应用
├── agent/
│   ├── __init__.py
│   ├── state.py        # 状态管理
│   ├── router.py       # 视图路由
│   ├── tools.py        # LLM 调用工具
│   └── prompts.py      # 提示词模板
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
└── README.md
```

## ✅ 手动测试清单

运行应用后，请按以下步骤测试：

### Onboarding 流程
- [ ] 选择赛道（如"生活方式"）
- [ ] 选择目标（如"记录生活"）
- [ ] 选择风格（如"轻松日常"）
- [ ] 选择精力投入（如"一般(3-4条/周)"）
- [ ] 选择避免话题（可多选或不选）
- [ ] 输入自定义补充（可选）
- [ ] 点击"完成设置"

### 内容生成
- [ ] 确认设置摘要正确显示
- [ ] 点击"生成我的一周内容"
- [ ] 等待生成完成，确认显示 7 天计划

### 查看内容
- [ ] 点击任意一天的"查看内容"
- [ ] 确认显示标题、开头、要点、CTA、标签
- [ ] 点击"返回计划"

### 改写内容
- [ ] 点击任意一天的"改写这条"
- [ ] 输入改写要求（如"语气更轻松"）
- [ ] 点击"开始改写"
- [ ] 确认内容已更新

### 周复盘
- [ ] 展开"周复盘与下周建议"
- [ ] 选择感觉最好的天数
- [ ] 选择感觉最难的天数
- [ ] 选择下周节奏偏好
- [ ] 点击"生成下周建议"
- [ ] 确认显示复盘总结和建议

### 重新开始
- [ ] 点击"重新开始"
- [ ] 确认回到 Onboarding 第一步

## ⚠️ 常见问题

### API Key 未设置
如果看到"未设置 DASHSCOPE_API_KEY 环境变量"错误：
1. 确认 `.env` 文件存在且包含有效的 API Key
2. 或者在终端中 `export DASHSCOPE_API_KEY=your-key`
3. 重启 Streamlit 应用

### 获取通义千问 API Key
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 在"API-KEY管理"页面创建 Key

### JSON 解析错误
如果多次重试后仍显示 JSON 解析错误：
1. 检查网络连接
2. 尝试重新生成
3. 如问题持续，可能是 API 服务暂时不稳定

## 📄 许可

MIT License

