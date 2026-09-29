# 第一版使用说明

项目叫 **Agent Handoff Lab**。重点是团队交接的评估和行为证据：在真实 AgentWorld 引擎里跑五个角色，记录每次动作前后的库存，再对比资源交付和消息延迟的影响。

当前第一版使用固定脚本决策，真实游戏执行。LLM 接口已接入代码，但尚未配置密钥，也没有运行真实模型实验。视频、图表、发布草稿都明确保留这个区别。

## 启动

安装 Node.js 22、Python 3.10+ 和 Git 后，在项目根目录运行：

```powershell
npm run setup
npm run dev
```

打开 http://127.0.0.1:7331 。等右上角显示 Engine connected 后，选择三种条件之一，点击 Run experiment。事件时间轴可以逐步回放，右侧显示真实状态差异。第一轮启动要生成地图缓存，可能需要约一分钟。

另外开一个终端可以运行 `npm run experiment`，完成每种条件五次重复。`npm test` 检查评估器能否拒绝“预先放好成品”“只报成功但库存没变”等错误证据。

真正游戏窗口在 http://127.0.0.1:7032 。用 `lab_viewer` / `local-lab-only` 登录后，运行：

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:7031/lab/observer
python -m lab.run --mode scripted --condition delayed-request --pace 0.45
```

五个角色会在观察者周围出现并执行任务，完成后退出。

## 接入模型

把 API 地址、模型名和密钥填到项目本地 `.env` 的 `LLM_BASE_URL`、`LLM_MODEL`、`LLM_API_KEY`。文件已被 Git 忽略，无需发送给聊天。当前支持 OpenAI 兼容的工具调用接口。重启服务后选择 LLM 模式即可；这会产生提供商的 API 费用。

## 发布材料

- `docs/LINKEDIN.md`：英文草稿，强调自己的 eval / explainability 观点。
- `videos/handoff-eval/`：HyperFrames 视频源文件，可修改文字和画面后重新渲染。
- `artifacts/agent-handoff-lab-v1.mp4`：本地首版视频。
- `docs/METHODS.md`：实验设置、真实结果、限制和下一步。

仓库目前 private，LinkedIn 没有自动发布。当前视频适合展示“我做了一个可以追踪和干预协作过程的评估工具”；真实模型的结果需要配置密钥后另跑。
