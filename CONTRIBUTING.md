# Contributing to AlbumAI Studio

Welcome! We are excited to collaborate with you to build the ultimate photo-separation and restoration Monorepo.

---

## 🛠️ Code Quality & Conventions

To maintain a clean codebase, every pull request must satisfy these style guidelines:

### Python (Backend)
* **Standard:** Follow Google Style Python docstrings.
* **Formatting:** Format code using `ruff` or `black` prior to submitting changes.
* **Types:** Always use Pydantic v2 strict models for API endpoints.

### TypeScript / Next.js (Frontend)
* **Standard:** Standardize components as modular, type-safe structures.
* **Linting:** Ensure no TypeScript compiler warnings (`tsc`) or ESLint issues remain prior to commits.

---

## 🏁 How to Propose Changes

1. Fork the repository and create a branch named `feature/your-feature-name`.
2. Commit your modifications following standard semantic formatting (`feat: add card mode aspect ratio`).
3. Ensure test coverage remains above `80%` by running `pytest`.
4. Open a Pull Request referencing the objective/issue.
