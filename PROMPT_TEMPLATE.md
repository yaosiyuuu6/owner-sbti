# Prompt Template

Use this when a non-Codex agent does not automatically treat the repository as a skill.

```text
学习并使用这个仓库：yaosiyuuu6/owner-sbti

规则：
1. 如果我还没说原始SBTI，你第一句只能问：你的原始SBTI是什么？
2. 不要先总结仓库。
3. 在我回答SBTI后，再读取 SKILL.md 和 references/portable-agent-spec.md。
4. 自动读取你能访问到的同一用户全部历史记录；如果权限不够，先问权限。
5. 最终只输出：人格、描述、链接。
```
