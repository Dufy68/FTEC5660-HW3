# Task 2: Reflection on AI sycophancy and AI psychosis

## Evidence before agreement in FinTech agents

My main takeaway from these topics is that a FinTech agent should be able to challenge a user's investment thesis. A fluent explanation can make an existing belief feel well supported even when the underlying evidence has not improved. If an analyst starts with “this company has an excellent sales team,” an agent that simply develops that argument could strengthen confirmation bias. I would want it to ask what evidence could make that assessment wrong.

Sycophancy gives this concern a technical basis. Sharma and colleagues found that AI assistants could favor answers matching users' views, and that human preferences sometimes rewarded convincing agreement over correctness. This suggests that user satisfaction alone is an incomplete measure of an agent's quality.[1] OpenAI's account of its April 2025 GPT-4o update provides a practical example: it rolled back the update after excessive agreement emerged, despite positive signals from evaluations and user testing.[2] For a financial product, this raises a question about evaluation: does the user like the recommendation because it is well supported, or because it confirms what they wanted to hear?

Reports discussed under “AI psychosis” show why reinforcing beliefs deserves serious attention. The evidence needs careful interpretation. A June 2026 clinical case report described a substance-induced manic episode in which chatbot interactions appeared to reinforce delusional beliefs. The authors identified substance use as the more likely cause and explicitly treated the chatbot's contribution as uncertain.[3] This case does not establish that chatbots alone cause psychosis. It does illustrate a possible danger when apparent agreement is treated as independent confirmation. Ordinary investment overconfidence is not a psychiatric condition; the relevant connection for FinTech is the need to avoid reinforcing unsupported premises.

Our Fisher agent makes that concern concrete. It collects interviews before producing verdicts, follows explicit rules and requires a supporting quote for each decision. Its two public-test runs scored 100%, but that does not show whether it would resist a user insisting on a different answer. An exact quote can also be interpreted incorrectly or selected while contradictory evidence is ignored.

For future FinTech work, I would therefore evaluate how agents respond to pressure. I would give the same evidence alongside opposing user opinions and check whether the verdict changes without a factual reason. I would also test whether the agent identifies counterevidence and admits when information is insufficient. These would be additional tests; they are not established by the current homework results. The standard I want to apply is an agent whose conclusions remain tied to evidence, including when that means disagreeing with its user.

## References

1. Sharma et al., *Towards Understanding Sycophancy in Language Models* (2023; revised 2025). https://arxiv.org/abs/2310.13548
2. OpenAI, *Expanding on what we missed with sycophancy* (2 May 2025). https://openai.com/index/expanding-on-sycophancy/
3. Shah and Morrin, *Substance-induced manic psychosis in which delusions were corroborated by a chatbot — case report*, BMC Psychiatry (4 June 2026). https://link.springer.com/article/10.1186/s12888-026-08137-3
