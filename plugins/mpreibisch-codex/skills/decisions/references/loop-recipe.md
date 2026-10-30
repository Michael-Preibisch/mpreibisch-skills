# Deterministic-first loop checks

Use the existing loop's state. The Decisions script stores no acknowledgements, cache, cooldown, or next-check deadline.

1. If a scheduled full check is due, run it before considering any cached skip or Decisions answer.
2. Skip without an API call only when authoritative evidence is exactly unchanged, already handled, and before its next scheduled check.
3. Otherwise, call Decisions on sufficient supplied evidence. Run the existing LLM step on uncertainty or any error.
4. If required evidence, handled state, or scheduling state is missing, run the full check.

Equality must cover the task, goal, evidence, errors, unresolved actions, deadlines, and question/rule configuration.
A repeated status label or an agent's repeated narration does not establish equality or handled state.
Only the caller records acknowledgement after the existing workflow handles the evidence.
A Decisions `SKIP` does not create that acknowledgement or extend a deadline.
Keep the watcher's hourly full check independent of cached answers.

This shell branch works in either host. It assumes the caller supplies trusted state:

```sh
if [ "$state_complete" != yes ] || [ "$full_check_due" = yes ]; then
  run_full_check
elif [ "$evidence_unchanged" = yes ] &&
     [ "$already_handled" = yes ] &&
     [ "$before_next_check" = yes ]; then
  : # Skip without calling the API.
elif python3 "$decide_script" --preset-file "$preset_file" \
  --input "$evidence_file" --gate; then
  : # The configured semantic gate selected the cheaper branch.
else
  run_llm_check
fi
```

`state_complete` is `yes` only when all required caller state is known.
The other flags come from the caller's evidence comparison, acknowledgement, and schedule.
`decide_script`, `preset_file`, and `evidence_file` are absolute paths owned by the caller.
Replace `run_full_check` and `run_llm_check` with the existing workflow's actions.
Only a completed full check advances its schedule. Cached skips never advance it.

After repeated API failures, the caller can apply a bounded outage cooldown and run the LLM directly.
The cooldown bypasses API calls, not full checks. An outage never authorizes a skip.
