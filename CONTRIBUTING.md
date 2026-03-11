# Contributing to AI Tools for Actuaries

Thank you for your interest in contributing! This guide walks you through the entire process step by step. **No prior GitHub experience is required** — just follow the instructions below.

> [!NOTE]
> **What is GitHub?** GitHub is a platform for collaboratively managing and sharing files — similar to a shared drive, but with built-in version control. Every change is tracked, so nothing is ever lost. This repository uses GitHub to collect and publish tutorials and guides for actuaries working with AI tools.

---

## Prerequisites

Before you begin, make sure you have:

1. **A GitHub account** — Sign up for free at [github.com](https://github.com/signup) if you do not have one yet.
2. **Write access** to this repository — If you are part of the IAA AI Task Force, request access from a maintainer by [sending an email](mailto:simon.hatzesberger@gmail.com). Your access is tied to your GitHub account.

> [!IMPORTANT]
> You must be **logged in** to your GitHub account to create branches and upload files. If you do not see editing options (e.g., the **"New branch"** button), you are either not logged in or your access has not been set up yet.

---

## What You Can Contribute

- **Tutorials and Guides** — Practical walkthroughs on using AI tools (e.g., LLM APIs, coding assistants, data analysis tools) in actuarial contexts. Formats include Jupyter notebooks, written guides, video walkthroughs, and more.
- **Templates** — Propose improvements or new templates to better structure future contributions. Open an [issue](https://github.com/IAA-AITF/AI-Tools-for-Actuaries/issues) or [contact us](mailto:simon.hatzesberger@gmail.com) with your suggestion.

---

## Step-by-Step: Adding a Tutorial or Guide

### Step 1: Open the Repository

1. **Navigate** to the repository: [github.com/IAA-AITF/AI-Tools-for-Actuaries](https://github.com/IAA-AITF/AI-Tools-for-Actuaries)
2. **Confirm you are logged in** — your profile picture should be visible in the top-right corner of the page. If you see a **"Sign in"** button instead, log in first.
3. You will see the repository's main page with a file listing and a README displayed below it. At the top-left, a dropdown shows the current branch (likely **main**).

### Step 2: Create Your Working Branch

You will create a personal copy of the `dev` branch to work on. This keeps your changes separate until they are ready to be merged.

> [!NOTE]
> **What is a branch?** Think of a branch as your own private workspace. You can make changes freely without affecting anyone else's work. Once you are done, you merge your changes back into the shared `dev` branch.

1. **Click** the branch dropdown (top-left of the page, it likely says **"main"**).
2. **Click** **"View all branches"** at the bottom of the dropdown.
3. On the Branches page, **click** the green **"New branch"** button.
4. A dialog will appear:
   - **New branch name** — Choose a short, descriptive name with no spaces. Use your name or initials so others can identify it (e.g., `tutorial_wilson`, `guide_smith`).
   - **Source** — Make sure **`dev`** is selected as the source.
5. **Click** **"Create new branch"**.

> [!IMPORTANT]
> Always select **`dev`** as the source — not `main`. The `dev` branch contains the latest working version. The `main` branch is only updated by maintainers.

> [!TIP]
> You will see your new branch listed on the Branches page. You can always return to this page to find or switch between branches.

### Step 3: Switch to Your Branch

1. **Navigate** back to the repository's main page by clicking the repository name (**"AI-Tools-for-Actuaries"**) at the top.
2. **Click** the branch dropdown (top-left). It might still show **main**.
3. **Select** your newly created branch from the list.
4. **Verify** that the branch dropdown now displays your branch name.

> [!WARNING]
> **Always confirm you are on your own branch before making any changes.** If the branch dropdown shows `main` or `dev`, you are not on your branch. Any changes made directly to `dev` or `main` will affect everyone. Switch to your branch first.

### Step 4: Prepare Your Files

Before uploading, organize your tutorial or guide into a self-contained folder. A typical tutorial directory includes:

| File | Description |
|:-----|:------------|
| `README.md` | Description, prerequisites, and instructions for getting started |
| Tutorial content | Jupyter notebook (`.ipynb`), written guide (`.md`), video link, or other format |
| `requirements.txt` | Python dependencies with version numbers (if applicable) |
| Any additional files | Datasets, images, configuration files, or supplementary materials |

> [!TIP]
> Use the existing [GenAI Beyond the Basics](./tutorials-and-guides/GenAI_Beyond_the_Basics/) tutorial as a reference for how to structure your directory and README.

> [!TIP]
> **All formats are welcome.** You can contribute Jupyter notebooks, step-by-step written guides, video walkthroughs with supporting materials, or any other format that effectively teaches the topic. Use whichever format best fits your content.

### Step 5: Upload Your Files

1. **Click** the **`tutorials-and-guides/`** folder in the file listing.
2. **Click** **"Add file"** (top-right) and then **"Upload files"**.
3. **Drag and drop** your tutorial folder or select files from your computer.

> [!NOTE]
> **Folder naming convention:** Use a short, descriptive folder name with underscores instead of spaces (e.g., `Intro_to_Prompt_Engineering`, `RAG_for_Actuaries`). This name will appear in the repository URL, so keep it concise and clear.

### Step 6: Save Your Work (Commit)

Once you have uploaded your files:

1. **Scroll down** to the commit section below the file upload area.
2. **Write a commit message** — a short description of what you are uploading (e.g., "Add prompt engineering tutorial").
3. **Confirm** that **"Commit directly to `[your-branch-name]`"** is selected. It should show your branch name.
4. **Click** the green **"Commit changes"** button.

> [!NOTE]
> **What is a commit?** A commit is like saving your work. Each commit creates a snapshot of your changes. You can make multiple commits — for example, one for uploading files and another for fixing a typo.

> [!IMPORTANT]
> Make sure the option says **"Commit directly to `[your-branch-name]`"**, not to `dev` or `main`. If it shows the wrong branch, cancel and switch to your branch first (see Step 3).

> [!TIP]
> **Save often.** You can commit after each change you make. If something goes wrong, you can always go back to a previous commit.

### Step 7: Review Your Changes

1. After committing, you are returned to the file view. **Navigate** to your uploaded folder.
2. **Open** the `README.md` file and check that it renders correctly.
3. **Verify** that all files are present and any links work correctly.

If you spot errors, you can edit files directly on GitHub (click the pencil icon) or upload corrected versions.

### Step 8: Create a Pull Request

When you are satisfied with your changes, you need to propose merging them into the shared `dev` branch. This is done through a **pull request**.

> [!NOTE]
> **What is a pull request?** A pull request (PR) is a formal proposal to merge your changes into another branch. It lets others review what you changed before the changes go live.

1. **Navigate** to the repository's main page.
2. If you recently pushed commits, GitHub will show a yellow banner at the top saying **"[your-branch] had recent pushes"** with a **"Compare & pull request"** button. **Click** it.
   - If you do not see this banner: **click** the **"Pull requests"** tab at the top of the page, then **click** the green **"New pull request"** button. Select `dev` as the **base** branch and your branch as the **compare** branch.
3. On the pull request form:
   - **Title** — Write a short title (e.g., "Add prompt engineering tutorial").
   - **Description** — Briefly describe what you added or changed.
   - **Base branch** — Confirm it says **`dev`** (not `main`).
4. **Click** the green **"Create pull request"** button.

### Step 9: Merge the Pull Request

After creating the pull request, you can merge it yourself if there are no conflicts.

1. On the pull request page, **scroll down**. You should see a green message: **"This branch has no conflicts with the base branch."**
2. **Click** the green **"Merge pull request"** button.
3. **Click** **"Confirm merge"**.
4. You should see a success message: **"Pull request successfully merged and closed."**

> [!WARNING]
> If you see a message about **merge conflicts**, do not force the merge. This means someone else has edited the same part of the file. Contact a maintainer for help resolving the conflict.

> [!TIP]
> After merging, GitHub may offer to **delete your branch**. You can safely delete it — the branch is no longer needed once its changes have been merged.

### Step 10: Verify Your Contribution

1. **Navigate** back to the repository's main page.
2. **Switch** to the **`dev`** branch using the branch dropdown.
3. **Open** the `tutorials-and-guides/` folder.
4. **Confirm** that your tutorial directory appears and its contents are correct.

Your contribution is now part of the shared `dev` branch. A maintainer will periodically transfer approved changes from `dev` to `main`.

---

## Quick Reference: Markdown Syntax

The README files in this repository use [Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax), a simple formatting language. Here are the patterns you will need:

| What you type | What it produces |
|:--------------|:-----------------|
| `**bold text**` | **bold text** |
| `` `code` `` | `code` |
| `[Link Text](https://url)` | [Link Text](https://url) |
| `### Heading` | A heading (level 3) |
| `- List item` | A bullet point |

---

## Guidelines for Submissions

- **Clarity & Practicality** — Guides should be clear, actionable, and oriented toward practical actuarial use cases.
- **Reproducibility** — Include setup instructions, dependencies, and all steps needed to follow along.
- **Attribution** — Properly attribute third-party content and respect licensing conditions.
- **Formatting** — Follow the structure of existing tutorials and the provided [templates](./templates/).
- **Licensing** — By contributing, you agree that your submissions will be available under the [MIT License](./LICENSE) (code) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (content).

---

## Need Help?

- [Open an issue](https://github.com/IAA-AITF/AI-Tools-for-Actuaries/issues) on the GitHub issue tracker
- [Contact us via email](mailto:simon.hatzesberger@gmail.com)

---

*This document may be updated. Please refer to it before each submission.*
