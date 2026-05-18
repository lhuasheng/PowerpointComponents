Run the PPTX screenshot updater for this project.

Execute the following bash command:

```bash
bash scripts/update_pptx_screenshots.sh
```

After it completes:
1. Report how many slides were rendered per deck.
2. List the output directories that were updated under `docs/screenshots/`.
3. If any deck failed or produced 0 slides, investigate and report the error.
