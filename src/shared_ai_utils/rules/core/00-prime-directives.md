## 0. Prime Directives (NON-NEGOTIABLE)

1. **Patent Compliance**:
    * **NEVER** use Linear Predictive Coding (LPC), source-filter models, glottal closure/opening detection, or static formant values.
    * **ALWAYS** use dynamic trajectories, phase analysis, and velocity-based methods.

2. **Security & Privacy**:
    * **NEVER** log raw audio bytes, PII, or API keys.
    * **ALWAYS** use environment variables for secrets.

3. **Design Philosophy (The Advisory Council)**:
    * **Dieter Rams ("Less but Better")**: Radical simplification. If a feature adds complexity without proportional value, kill it.
    * **Daniel Kahneman ("System 2 Thinking")**: Code should handle failure gracefully. validation before execution.
    * **Constraint**: No "branding" of these names in code. Use descriptive names.

4. **Agent Behavior: "Defense Against Complexity"**:
    * **Stop and Think**: Before writing code, ask: "Is this the simplest way to solve the user's *actual* problem?"
    * **No Speculative Features**: Do not add "nice to have" flexibility. Build exactly what is needed now.
    * **Refactor First**: If the code is hard to change, refactor it first. Do not pile hacks on top of technical debt.
    * **Error Prevention**:
        * **Type Safety**: Use Pydantic strict mode where possible.
        * **Fail Fast**: Validate inputs at the boundary (API/CLI), not deep in the stack.
        * **Atomic Operations**: Side effects (DB writes, File IO) should be isolated.
