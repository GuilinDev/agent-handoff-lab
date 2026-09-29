# LinkedIn draft — v0.1

Draft only. Nothing has been posted. Pair the text below with the 50-second video. The repository is currently private; omit the repo link until you choose to make it accessible.

---

If a team of agents finishes the task, what did our evaluation actually learn?

I built a small handoff-evaluation workbench on top of AgentWorld. Five roles turn ore, coal, and wood into three tools. Then I disrupt one resource delivery and delay a coordination message.

In the first scripted baseline, every run eventually succeeds. But the mean completion cost changes from 5.0 to 7.2 to 9.0 rounds across the three conditions.

The interesting part is the evidence behind those numbers: a request for 10 coal delivers only 5; the smelter hits a missing-material error; a delayed request holds up the rest of the chain. One run also hits a real game cooldown, which stays visible in the trace.

My working view: agent-team evals should measure the quality of handoffs and recovery, alongside the final result.

And I want to be precise about “explainability.” An inventory trace shows what changed. An intervention tests a dependency. Neither gives us access to a model's internal reasoning.

This version validates the instrumentation with fixed policies on the real game engine. The next experiment is to compare LLM policies under the same disruptions and measure their recovery and token costs.

When a multi-agent system succeeds, what failure modes are your evals still missing?

Built on openagents-org/agentworld; video made with HyperFrames.

#AIAgents #AgentEvaluation #MultiAgentSystems

---

## 中文表达意图

重点是你自己的工程判断：团队任务不能只看最终成功；交接、恢复和沟通成本同样需要评估。可解释性先落在可检查的行为证据上，再用干预验证具体依赖。当前的固定策略实验是在验证这套测量工具，不能写成“发现了 LLM 的涌现协作规律”。

发布前可把开头换成更个人化的一句，例如：“I started by recreating an agents-in-a-game demo. I ended up thinking more about what the scoreboard misses.”
