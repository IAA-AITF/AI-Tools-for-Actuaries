# Contributing to AI Tools for Actuaries

Thank you for your interest in contributing! We welcome submissions from actuaries, data scientists, and AI practitioners to build a comprehensive resource hub for AI applications in actuarial work. **No prior GitHub experience is required** — just follow the instructions below.

> [!NOTE]
> **What is GitHub?** GitHub is a platform for collaboratively managing and sharing files — similar to a shared drive, but with built-in version control. Every change is tracked, so nothing is ever lost. This repository uses GitHub to collect and publish tutorials, guides, and tools for actuaries working with AI.

---

## Prerequisites

Before you begin, make sure you have:

1. **A GitHub account** — Sign up for free at [github.com](https://github.com/signup) if you do not have one yet.

That is all you need. The workflow below uses **forking**, which means you create your own copy of the repository under your GitHub account. You do not need any special permissions.

> [!IMPORTANT]
> You must be **logged in** to your GitHub account to fork, create branches, and edit files. If you do not see the **"Fork"** button or editing options, you are not logged in.

---

## What You Can Contribute

- **Tutorials and Guides** — Practical walkthroughs on using AI tools (e.g., LLM APIs, coding assistants, data analysis tools) in actuarial contexts. Formats include Jupyter notebooks, written guides, video walkthroughs, and more.
- **Templates** — Propose improvements or new templates to better structure future contributions. Open an [issue](https://github.com/IAA-AITF/AI-Tools-for-Actuaries/issues) or [contact us](mailto:simon.hatzesberger@gmail.com) with your suggestion.

> [!TIP]
> Review the [templates](./templates/) and existing tutorials before you start. They show the expected structure and style.

---

## How to Contribute (GitHub Web UI)

This section walks you through each step using the GitHub website. If you prefer working locally with Git, see the [CLI Workflow](#for-experienced-git-users-cli-workflow) section below.

### Step 1: Fork the Repository

A **fork** is your personal copy of the repository. You make all your changes there, then propose them back to the original repository via a pull request.

1. **Navigate** to the repository: [github.com/IAA-AITF/AI-Tools-for-Actuaries](https://github.com/IAA-AITF/AI-Tools-for-Actuaries)
2. **Confirm you are logged in** — your profile picture should be visible in the top-right corner. If you see a **"Sign in"** button instead, log in first.
3. **Click** the **"Fork"** button (top-right of the page).
4. On the fork creation page, leave the defaults and **click** **"Create fork"**.
5. GitHub will redirect you to your fork. Confirm the repository name at the top says **`your-username/AI-Tools-for-Actuaries`** with a note "forked from IAA-AITF/AI-Tools-for-Actuaries".

> [!TIP]
> You only need to fork once. If you have already forked this repository, navigate to your fork at `github.com/your-username/AI-Tools-for-Actuaries` instead.

### Step 2: Create Your Working Branch

1. On your fork's main page, **click** the branch dropdown (top-left, it likely says **"main"**).
2. **Type** a short, descriptive branch name with no spaces (e.g., `tutorial_doc-to-md`, `guide_llm-apis`).
3. **Click** **"Create branch: your-branch-name from 'main'"**.

> [!NOTE]
> **What is a branch?** Think of a branch as your own private workspace. You can make changes freely without affecting anyone else's work. Once you are done, you merge your changes back via a pull request.

### Step 3: Add Your Content

1. **Make sure** the branch dropdown shows your branch name.
2. **Navigate** to the appropriate folder (e.g., `tutorials-and-guides/`).
3. To **create a new subfolder** for your tutorial:
   - **Click** **"Add file"** → **"Create new file"**.
   - In the file name field, type: `your-tutorial-name/README.md` (the slash creates the subfolder automatically).
   - Write or paste your content, then commit (see Step 4).
4. To **upload files** (notebooks, data, images):
   - Navigate into your new subfolder.
   - **Click** **"Add file"** → **"Upload files"**.
   - **Drag and drop** your files or select them from your computer.
   - Commit the uploaded files (see Step 4).

> [!TIP]
> **Check your formatting** by switching to the **Preview** tab in the editor. This shows you exactly how the content will look on the published page.

### Step 4: Save Your Work (Commit)

1. **Click** the green **"Commit changes..."** button (top-right of the editor).
2. A dialog will appear:
   - **Commit message** — Write a short description (e.g., "Add doc-to-md tutorial").
   - **Commit directly to `[your-branch-name]`** — Confirm it shows your branch name.
3. **Click** the green **"Commit changes"** button.

> [!NOTE]
> **What is a commit?** A commit is like saving your work. Each commit creates a snapshot of your changes. You can make multiple commits as you add more files.

> [!IMPORTANT]
> Make sure the dialog says **"Commit directly to `[your-branch-name]`"**, not to `main`. If it shows the wrong branch, cancel and switch to your branch first.

### Step 5: Create a Pull Request

When you are satisfied with your changes, propose merging them into the original repository.

> [!NOTE]
> **What is a pull request?** A pull request (PR) is a formal proposal to merge your changes into the original repository. It lets maintainers review what you changed before the changes go live.

1. **Navigate** to your fork's main page on GitHub.
2. GitHub will show a banner saying your branch is ahead of the original repository, with a **"Contribute"** button or a **"Compare & pull request"** button. **Click** it.
   - If you do not see this banner: **click** the **"Pull requests"** tab on the **original** repository, then **click** **"New pull request"** → **"compare across forks"**. Select the original repository's `main` branch as the **base** and your fork's branch as the **compare** branch.
3. On the pull request form:
   - **Title** — Write a short title (e.g., "Add doc-to-md tutorial").
   - **Description** — Briefly describe what you added or changed.
4. **Click** the green **"Create pull request"** button.

### Step 6: Wait for Review

After creating the pull request, a maintainer will review your contribution. You may receive feedback or change requests — GitHub will notify you by email. Once approved, a maintainer will merge your changes.

> [!TIP]
> You can check the status of your pull request at any time by navigating to the **"Pull requests"** tab on the original repository.

---

## For Experienced Git Users: CLI Workflow

If you prefer working locally with Git, here is the quick-reference workflow:

```bash
# 1. Fork the repository on GitHub (use the "Fork" button), then clone your fork
git clone https://github.com/your-username/AI-Tools-for-Actuaries.git
cd AI-Tools-for-Actuaries

# 2. Create a branch
git checkout -b your-branch-name

# 3. Add your content (tutorials, guides, etc.)

# 4. Stage and commit
git add .
git commit -m "Add your-tutorial-name"

# 5. Push to your fork
git push origin your-branch-name

# 6. Open a pull request on GitHub
#    Go to the original repository and click "Compare & pull request",
#    or use:  gh pr create --repo IAA-AITF/AI-Tools-for-Actuaries
```

> [!TIP]
> If your fork is behind the original repository, sync it before starting: on your fork's GitHub page, click **"Sync fork"**, or run `git fetch upstream && git merge upstream/main`.

---

## Guidelines for Submissions

- **Clarity & Practicality** — Guides should be clear, actionable, and oriented toward practical actuarial use cases.
- **Reproducibility** — Include code, dependencies (e.g., `requirements.txt` with version numbers), and steps to reproduce results.
- **Attribution** — Properly attribute third-party content and respect licensing conditions.
- **Formatting** — Follow Markdown conventions and structure submissions based on the provided [templates](./templates/).
- **Licensing** — By contributing, you agree that your submissions will be available under:
  - [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) for textual content
  - [MIT License](./LICENSE) for code and scripts

---

## Need Help?

- [Open an issue](https://github.com/IAA-AITF/AI-Tools-for-Actuaries/issues) on the GitHub issue tracker
- [Contact us via email](mailto:simon.hatzesberger@gmail.com)

---

*This document may be updated. Please check back before each submission.*
