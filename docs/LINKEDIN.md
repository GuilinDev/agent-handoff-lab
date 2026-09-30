# LinkedIn draft — gameplay edition

Draft only. Nothing has been posted. Pair the text below with `artifacts/agent-handoff-lab-v3-en.mp4`, the 56-second English video with complete captions. A 58-second Yunyang Mandarin version is also supplied. Both now explain the setup, intervention, refill, result and evaluation viewpoint in one continuous read. The repository is public; its link is included below.

---

15/15 runs succeeded. That wasn't the whole story.

I started by recreating an agents-in-a-game demo. I ended up building a small lab to study what a success rate hides.

Built on AgentWorld, five roles turn ore, coal, and wood into three tools. I cap one coal delivery, then add a delayed coordination message in a third condition.

In this scripted baseline, all runs eventually finish. Mean rounds to completion: 5.0 → 7.2 → 9.0.

The video follows the evidence: ten coal requested, five delivered, a missing-material error, a delayed request, then recovery. One run also encounters an engine cooldown; that stays in the trace and limits how we attribute the extra cost.

My working view: agent-team evals should measure handoffs and recovery alongside the final result. A team can get there while spending avoidable effort getting unstuck.

And I want to be precise about “explainability.” An inventory trace shows what changed. An intervention tests a dependency. Neither gives us access to a model's internal reasoning.

This first version uses fixed policies on the real game engine, not LLM agents. It validates the instrumentation. Next: compare LLM policies under the same disruptions and measure recovery and token costs.

Code, recorded traces, and reproduction steps:
https://github.com/GuilinDev/agent-handoff-lab

When a multi-agent system succeeds, what failure modes are your evals still missing?

Built on openagents-org/agentworld; video made with HyperFrames.

#AIAgents #AgentEvaluation #MultiAgentSystems

---

## 中文表达意图

重点是你自己的工程判断：团队任务不能只看最终成功；交接、恢复和沟通成本同样需要评估。可解释性先落在可检查的行为证据上，再用干预验证具体依赖。当前的固定策略实验是在验证这套测量工具，不能写成“发现了 LLM 的涌现协作规律”。

仓库链接已经写进英文正文。视频里的资源动画是来自实际轨迹的后期标注，角色和游戏场景来自本地真实录屏；没有展示未运行过的 LLM 实验。
