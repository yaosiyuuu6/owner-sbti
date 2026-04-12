# OpenClaw

If the user did not already provide their original `SBTI`, your first reply must be:

```text
你的原始SBTI是什么？
```

Do not ask for MBTI types such as `INTJ`、`ENTP`、`INFP`.
Use the original SBTI codes from `references/original-types.md`, such as `LOVE-R`、`SHIT`、`CTRL`.

Then:

1. read `SKILL.md`
2. read `references/portable-agent-spec.md`
3. inspect all same-user records you can already access
4. build a report JSON object and run `python3 scripts/finalize_report.py --input /path/to/report.json`
5. do not design your own image layout and do not replace the bundled poster renderer
6. do not ask the user to paste logs or evidence unless broader history is truly unavailable
7. if the current channel supports image sending, send the generated image directly
8. otherwise return only:

```text
人格：
描述：
图片：
```
