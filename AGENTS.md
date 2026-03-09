# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

History Hub (历史文献馆) — a FastAPI + vanilla JS app that searches and displays public-domain books from Project Gutenberg via the Gutendex API. See `README.md` for project structure and API reference.

### Running the dev server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading on code changes. The server serves both the API (`/api/*`) and static frontend files (`index.html`, `script.js`, `styles.css`) from the workspace root.

### Lint / syntax check

There is no dedicated linter configured. CI runs:

```bash
python3 -m py_compile app.py
```

### Caveats

- `uvicorn` is installed to `~/.local/bin`. Ensure `$HOME/.local/bin` is on `PATH` (it is by default in most shells, but if commands are not found, run `export PATH="$HOME/.local/bin:$PATH"`).
- The app requires outbound internet access to reach `gutendex.com` and `gutenberg.org`. Without it, search and book-reading endpoints will return 502 errors.
- There are no automated tests in this repository; validation is done via `py_compile` syntax check and manual testing of the API endpoints.
