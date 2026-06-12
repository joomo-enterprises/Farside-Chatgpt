# Contributing to On The FarSide Series

Thank you for your interest in contributing to the companion code repository for the **"On The FarSide Series"** YouTube channel! This repo contains code examples and exercises based on the book **"FarSide ChatGPT"** by the Joomo Enterprises.

## How to Contribute

### Reporting Issues

If you find a bug, error, or have a question about the code:

1. **Check existing issues** first to avoid duplicates.
2. Open a new issue with a clear title and description.
3. Include:
   - The episode and file where the issue occurs
   - Steps to reproduce
   - Expected vs. actual behavior
   - Your environment (Python version, OS, etc.)

### Submitting Code

1. **Fork** the repository.
2. **Create a branch** for your changes:
   ```bash
   git checkout -b fix/episode-03-typo-in-readme
   ```
3. **Make your changes** — keep them focused and minimal.
4. **Test your code** — make sure examples run without errors.
5. **Commit** with a clear message:
   ```bash
   git commit -m "fix: correct API endpoint in episode-03 multimodal example"
   ```
6. **Push** and open a Pull Request against `main`.

### Code Style

- Follow **PEP 8** for Python code.
- Use **type hints** where practical.
- Include **docstrings** for functions and classes.
- Keep lines under **100 characters**.
- Add **comments** explaining non-obvious logic.

### Adding New Episodes

Use the template in `episodes/template/` as a starting point:

```bash
cp -r episodes/template episodes/episode-XX-your-topic
```

Then update the README.md, requirements.txt, and add your source code in `src/`.

### Commit Message Format

We use conventional commit prefixes:

- `feat:` — New feature or example
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `refactor:` — Code restructuring
- `chore:` — Maintenance tasks

## Code of Conduct

- Be respectful and constructive.
- Welcome newcomers.
- Focus on what is best for the community and learners.

## Questions?

Open an issue with the `question` label, or reach out via the YouTube channel community tab.

---

Thank you for helping make this resource better for everyone!
