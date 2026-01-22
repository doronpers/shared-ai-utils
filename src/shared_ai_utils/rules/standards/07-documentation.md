## 7. Documentation

### Documentation Maintenance (REQUIRED)

**CRITICAL**: Documentation maintenance is a mandatory part of every task completion. This is not optional.

* **Always Update Documentation**: As part of completing any task, you MUST update relevant documentation to reflect changes, additions, or improvements.

* **Prefer Existing Documentation**: Add new documents ONLY when absolutely necessary for clarity and understandability. When possible, add information to existing documentation files to maintain organization and reduce fragmentation.

* **Maintain Organization**: Keep documentation organized by:
  * Adding to existing relevant sections rather than creating new files
  * Following established documentation structure and patterns
  * Grouping related information together

* **Revise Outdated Content**: When you encounter outdated, irrelevant, or redundant information in documentation during your work, you MUST:
  * Update outdated information to reflect current state
  * Remove or consolidate redundant content
  * Mark or remove irrelevant sections
  * Do not leave documentation in a worse state than you found it

* **Update These Files When Relevant**:
  * `README.md` - If installation steps, setup, or project overview changes
  * `AGENT_KNOWLEDGE_BASE.md` - If you discover new recurrent issues, patterns, or guidelines
  * `ROADMAP.md` - If completing TODOs or adding new tasks
  * API documentation - If endpoints, parameters, or responses change
  * Code comments and docstrings - If function behavior or interfaces change

* **Documentation as Part of Definition of Done**: A task is not complete until:
  1. Code changes are implemented and tested
  2. All relevant documentation is updated
  3. Outdated information encountered during the task is revised
  4. Documentation passes linting checks (markdownlint)

### Documentation Standards

* **Markdown Linting**: When creating or editing markdown files, ensure all headings are unique to avoid markdownlint MD024 errors. If multiple sections use the same heading text (e.g., "Problem Statement", "Solution Overview"), make them unique by adding context (e.g., "Problem Statement - Error Handling", "Problem Statement - Onboarding"). Always run markdownlint before committing documentation changes.

* **Heading Spacing (MD022)**: Headings must be surrounded by blank lines both above and below. This applies to all heading levels (##, ###, ####, etc.). For example:

  ```markdown
  ## Section Title
  
  Content here...
  
  ### Subsection
  
  More content...
  ```

  Always ensure there's a blank line after headings, especially before code blocks, lists, or other content.

* **Code Block Spacing (MD031)**: Fenced code blocks (```) must be surrounded by blank lines both above and below. Always add a blank line before opening a code block and after closing it.

* **Markdown Tables**: When creating markdown tables, use the "compact" style format required by markdownlint MD060. This means separator rows must have spaces around pipes: `| ------ | ------ |` instead of `|------|------|`. The header row and separator row must have consistent spacing. Always verify table formatting with markdownlint before committing.
