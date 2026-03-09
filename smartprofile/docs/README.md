# SmartProfile - 智能化学诊断与知识追踪引擎

## 项目简介

SmartProfile是一个基于DINA模型的智能化学诊断与知识追踪引擎，能够评估学生的知识点掌握情况并生成个性化学习建议。系统采用前后端分离架构，通过优化API设计和数据加载策略，实现了选完学生瞬间出图的用户体验。

## 核心功能

- **知识点掌握评估**：基于DINA模型计算学生在各知识点上的掌握概率
- **可视化展示**：使用雷达图直观展示学生的知识点掌握情况
- **个性化建议**：集成火山引擎大模型，为每个学生生成独特的学习建议
- **知识图谱**：构建知识点之间的前序/后继关系，形成知识网络
- **快速响应**：分离雷达图数据和学习建议加载，实现瞬间出图

## 技术栈

| 层级  | 技术 | 说明 |
|------|------|------|
| 后端 | Python + FastAPI | 高性能异步Web框架 |
| 数据库 | SQLite | 轻量级关系型数据库 |
| 前端 | Vue3 + ECharts + Vite | 现代化前端技术栈 |
| AI | OpenAI SDK + 火山引擎 | 大模型API调用 |

## 项目结构

```
smartprofile/
├── backend/              # 后端服务
│   ├── api/              # 接口层（FastAPI路由）
│   │   └── student.py    # 学生相关API
│   ├── model/            # 算法层
│   │   ├── dina.py       # DINA模型实现
│   │   └── llm_service.py # 大模型服务
│   ├── data/             # 数据层
│   │   └── db.py         # 数据库操作
│   ├── main.py           # 服务入口
│   └── smartprofile.db   # SQLite数据库文件
├── frontend/             # Vue3前端
│   ├── src/
│   │   ├── App.vue       # 主页面组件
│   │   └── main.js       # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── sql/                  # 数据库脚本
│   ├── init.sql          # 数据库初始化脚本
│   ├── generate_data.py  # 数据生成脚本
│   └── smartprofile.db   # 数据库文件
├── docs/                 # 文档
│   ├── README.md         # 项目说明
│   ├── dev_idea.md       # 开发思路
│   └── prompt.md         # Prompt文档
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- 火山引擎API密钥

### 1. 安装后端依赖

```bash
cd backend
pip install fastapi uvicorn numpy openai
```

### 2. 安装前端依赖

```bash
cd ../frontend
npm install
```


### 3. 启动服务

**启动后端服务：**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**启动前端服务：**
```bash
cd frontend
npm run dev
```

### 4. 访问系统

- 前端页面：http://localhost:3000
- API文档：http://127.0.0.1:8000/docs

## API接口说明

### 获取学生知识点掌握情况

- **URL**：`/student/{student_id}/knowledge`
- **方法**：GET
- **响应**：
```json
{
  "student_id": "student1",
  "mastery_probs": {
    "kp1": 0.85,
    "kp2": 0.72,
    "kp3": 0.91,
    "kp4": 0.68,
    "kp5": 0.79
  },
  "knowledge_graph": [...],
  "learning_suggestions": []
}
```

### 获取学生个性化学习建议

- **URL**：`/student/{student_id}/suggestions`
- **方法**：GET
- **响应**：
```json
{
  "student_id": "student1",
  "learning_suggestions": [
    "建议1：...",
    "建议2：...",
    "建议3：..."
  ]
}
```

## 核心模块说明

### 数据层（data/db.py）

封装了数据库操作函数：
- `get_q_matrix()`：获取Q矩阵（题目-知识点关联）
- `get_x_matrix(student_id)`：获取指定学生的X矩阵（作答记录）
- `get_knowledge_graph()`：获取知识图谱

### 算法层（model/dina.py）

实现了DINA模型：
- `__init__(s=0.1, g=0.2)`：初始化模型参数
- `predict(student_id, q_matrix, x_matrix)`：计算学生知识点掌握概率

### 大模型服务（model/llm_service.py）

集成火山引擎大模型：
- 使用OpenAI SDK调用API
- 从环境变量获取API密钥
- 生成个性化学习建议

### 接口层（api/student.py）

提供RESTful API：
- `/student/{student_id}/knowledge`：快速返回知识点掌握情况
- `/student/{student_id}/suggestions`：单独返回大模型生成的学习建议

### 前端（frontend/src/App.vue）

实现交互式界面：
- 学生选择下拉框
- 认知雷达图（ECharts）
- 个性化学习建议展示
- 异步加载和加载状态


## 开发文档

- [算法逻辑说明](算法逻辑说明.md) - 详细的技术方案和实现细节
- [Prompt文档](prompt.md) - AI协同开发的Prompt示例

## 技术亮点

1. **DINA模型实现**：准确评估学生知识点掌握情况
2. **大模型集成**：使用OpenAI SDK调用火山引擎API
3. **性能优化**：分离数据加载，实现瞬间出图
4. **前后端分离**：清晰的架构设计，易于维护和扩展
5. **完整的错误处理**：确保系统稳定性和可靠性

