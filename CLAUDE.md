# Claude Code

If the user did not already provide their original `SBTI`, your first reply must be:

```text
你的原始SBTI是什么？
```

Then:

1. read `SKILL.md`
2. read `references/portable-agent-spec.md`
3. inspect all same-user records you can already access
4. do not ask the user to paste logs or evidence unless broader history is truly unavailable
5. if the current channel supports image sending, send the generated image directly
6. otherwise return only:

```text
人格：
描述：
图片：
```
