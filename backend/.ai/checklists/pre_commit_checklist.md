# Pre-Commit Checklist

Run through this checklist **before** staging and committing changes to Git.

---

## 1. Code Quality & Formatting
- [ ] No temporary `print()` debug statements left in production code.
- [ ] Pydantic models use `model_config = ConfigDict(from_attributes=True)`.
- [ ] Timezone-aware datetimes used (`datetime.now(timezone.utc)`).
- [ ] Error messages are informative and logged visibly.

## 2. Testing Verification Gate
- [ ] Full automated test suite passes with 0 failures:
  ```bash
  PYTHONPATH=backend pytest app/tests/ -v
  ```
- [ ] New functionality or bug fix is accompanied by new test cases.

## 3. Git Staging Hygiene
- [ ] Run `git status` to inspect staged files.
- [ ] Confirm no secrets, API keys, `.env` files, `.venv/`, `__pycache__/`, or `storage/` files are staged.
- [ ] Commit message conforms to Conventional Commits:
  ```
  <type>(<scope>): <imperative summary>
  ```
