# campaign-astra-0400

统一七位Astra直连研究员campaign。模型：gateway_responses/gpt-6-astra:max；最终截止：2026-11-07T04:00:00+08:00。旧Sol/Argon会话、旧窗口和失败/部分产物保留为历史，不与新campaign共享写owner。每位研究员独占campaign worker cwd；共享板通过事务CLI。到04:00先停止所有campaign runs，再ack-pause，停两个campaign monitor，不自动续期。
