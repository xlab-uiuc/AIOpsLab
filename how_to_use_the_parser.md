## Use parse_result.py to generate results.json
**If ran the evaluation by gpt-full.py**

Ensure `SHOW_PROMPT = True`. It will read the `task_message` prompt from the trajectory.

**Otherwise**

Set `SHOW_PROMPT = False`, and fill `DOCS_SHELL_ONLY` with the prompt the agent uses. (If more arguments are needed, please modify line 152 at the same time)

Itself will generate the `task_message` prompt.

----

For different models, please modify `AGENT_MODEL="gpt-4o"` at line 10

**If you are using a different model than GPT-4o or llama3**:

Please modify line 85 `count_message_tokens()`

- **IMPORTANT**: You need to modify the model for tiktoken (`tiktoken.encoding_for_model(model)`)
- You need to modify `tokens_per_message` and `tokens_per_name` because different model uses different way to translate the list. If you have a better way to compute (like calling some API), please raise a PR. (Actually this part only affects little)


----

**Please ensure all the evaluation tasks end normally**

```
./parse_result.py | tee parser.out
grep "Error processing" parser.out
```

If nothing was output by grep, then everything is okay. Otherwise you should re-run these failed tasks.

For multiple runs of one task, the parser will pick the latest one (lexicographical order in fact).
So you don't need to remove the earlier trajectory of failed tasks.

## Use results.json to generate tables
**Ensure there is a 'results.json' in the same directory`

It will generate four `<task_type>_table.csv`.

**Please make sure all the evaluation tasks end normally before run this script.**

Then paste it into the table. Choose 'Split text to columns' (Each time you paste, G-sheet will show a button. Click it and you will see this in the selections)