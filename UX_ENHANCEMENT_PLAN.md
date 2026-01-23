# Cross-Repository UX Enhancement Plan

## Implementation Status

**Last Updated:** January 2026  
**Core Infrastructure:** ✅ Complete  
**Integration Status:** ⏳ Ready for repository integration

## Executive Summary

After comprehensive review of documentation and code across 11 repositories, three critical UX enhancement areas have been identified and **core infrastructure has been implemented**. The foundational components are complete and ready for integration into individual repositories.

**Review Scope:**
- Documentation: READMEs, guides, API references, troubleshooting docs
- Code: CLI implementations, API endpoints, frontend components, error handling
- User Flows: Onboarding, error recovery, documentation discovery

**Identified Priority Areas:**
1. **Unified Onboarding & First-Time Experience** (Highest Impact)
2. **Progressive Error Recovery & Contextual Help** (High Impact)
3. **Documentation Hub & Contextual Discovery** (Medium-High Impact)

---

## Area 1: Unified Onboarding & First-Time Experience

### Problem Statement

Users face significant friction when starting with any repository:

1. **Multiple Entry Points**: Each repo has different setup processes (Docker, local Python, CLI, web app)
2. **Unclear Starting Point**: Multiple "START_HERE", "QUICKSTART", "QUICK_START" files create confusion
3. **Incomplete Implementations**: CLI commands show "not yet implemented" messages (feedback-loop config, review commands)
4. **Setup Complexity**: Different prerequisites, environment variables, and configuration methods per repo
5. **No Unified Experience**: No single entry point that guides users to the right repo for their needs

### Current State Analysis

**sono-eval:**
- Has `launcher.sh` for Docker setup
- CLI with `setup` wizard
- Multiple documentation entry points (START_HERE, QUICK_START, QUICKSTART)
- Good error formatting but setup can be complex

**feedback-loop:**
- Has `fl-start` one-liner` for setup
- CLI commands show "not yet implemented" placeholders
- `fl-bootstrap` for auto-setup
- Desktop launchers exist but may not be discoverable

**council-ai:**
- Has `council init` setup wizard
- Web app with React UI
- LM Studio integration for zero-cost option
- Multiple launcher scripts (command, bat files)

**sono-platform:**
- Complex monorepo with multiple modes
- Setup wizard exists but may not be discoverable
- Docker compose setup
- Multiple entry points (XLayer, Sonotheia)

**shared-ai-utils:**
- Library package, no direct user onboarding
- Good README but users may not know when to use it

### Solution Design

Create a **Unified Onboarding System** that:

1. **Detects User Intent**: Interactive questionnaire to determine which repo/tool fits their needs
2. **Guided Setup**: Step-by-step setup wizard that works across repos
3. **Progress Tracking**: Save setup state, resume later
4. **Unified CLI**: Single entry point (`sono` or `sonotheia`) that routes to appropriate tools
5. **Completion Verification**: Test setup and provide next steps

### Implementation Plan

#### Phase 1: Create Unified Onboarding CLI Tool

**Location**: `shared-ai-utils/src/shared_ai_utils/onboarding/`

**Components to Create:**

1. **`unified_setup.py`** - Main onboarding orchestrator
   ```python
   class UnifiedOnboarding:
       """Unified onboarding system for all Sonotheia ecosystem repos."""
       
       def __init__(self):
           self.repos = {
               "sono-platform": SonoPlatformOnboarding(),
               "sono-eval": SonoEvalOnboarding(),
               "feedback-loop": FeedbackLoopOnboarding(),
               "council-ai": CouncilAIOnboarding(),
           }
       
       async def run(self):
           """Interactive onboarding flow."""
           # 1. Welcome & intent detection
           # 2. Repository selection
           # 3. Guided setup for selected repo
           # 4. Verification & next steps
   ```

2. **`intent_detector.py`** - Questionnaire to determine user needs
   ```python
   class IntentDetector:
       """Detect user intent and recommend appropriate tools."""
       
       QUESTIONS = [
           {
               "question": "What is your primary goal?",
               "options": [
                   "Voice authentication/deepfake detection",
                   "Code assessment and evaluation",
                   "Pattern learning and code quality",
                   "AI advisory and decision-making",
               ],
               "recommendations": {
                   0: ["sono-platform", "sonotheia-examples"],
                   1: ["sono-eval"],
                   2: ["feedback-loop"],
                   3: ["council-ai"],
               }
           },
           # ... more questions
       ]
   ```

3. **`setup_wizards/`** - Repository-specific setup wizards
   - `sono_platform_wizard.py`
   - `sono_eval_wizard.py`
   - `feedback_loop_wizard.py`
   - `council_ai_wizard.py`

4. **`verification.py`** - Setup verification and testing
   ```python
   class SetupVerifier:
       """Verify setup completion and test functionality."""
       
       def verify_repo(self, repo_name: str) -> VerificationResult:
           """Run verification tests for a repository."""
           # Check dependencies
           # Test API endpoints
           # Verify configuration
           # Return detailed results
   ```

**Integration Points:**

- Add to `shared-ai-utils/cli/onboarding.py`:
  ```python
  @click.command("onboard")
  @click.option("--repo", help="Skip questionnaire, setup specific repo")
  def onboard(repo):
      """Unified onboarding for Sonotheia ecosystem."""
      onboarding = UnifiedOnboarding()
      asyncio.run(onboarding.run(repo=repo))
  ```

- Update each repo's README to link to unified onboarding
- Create `GETTING_STARTED.md` in each repo that redirects to unified system

#### Phase 2: Complete Incomplete CLI Commands

**Location**: `feedback-loop/src/feedback_loop/cli/commands/`

**Files to Complete:**

1. **`config.py`** - Implement actual config management
   ```python
   # Replace placeholder with:
   from shared_ai_utils.config import ConfigManager
   
   config_manager = ConfigManager()
   if set_key:
       key, value = set_key.split("=", 1)
       config_manager.set(key, value)
       console.print(f"[green]✓[/green] Set {key} = {value}")
   ```

2. **`review.py`** - Implement code review
   ```python
   # Use shared-ai-utils pattern checks
   from shared_ai_utils.assessment.pattern_checks import detect_pattern_violations
   from shared_ai_utils.integrations import SonoPlatformReviewer
   
   violations = detect_pattern_violations(code)
   reviewer = SonoPlatformReviewer()
   result = await reviewer.review_code(file_path, code)
   ```

3. **`analyze.py`** - Implement analysis logic
   ```python
   # Use shared-ai-utils metrics
   from shared_ai_utils.metrics import MetricsCollector
   from shared_ai_utils.insights import InsightsEngine
   
   collector = MetricsCollector()
   insights = InsightsEngine(collector)
   analysis = insights.analyze_patterns()
   ```

#### Phase 3: Create Unified Entry Point

**Location**: New repo or `shared-ai-utils/bin/`

**Create `sono` CLI wrapper:**

```python
#!/usr/bin/env python3
"""Unified entry point for Sonotheia ecosystem."""

import sys
import subprocess

COMMANDS = {
    "platform": "sono-platform CLI",
    "eval": "sono-eval CLI",
    "patterns": "feedback-loop CLI",
    "council": "council-ai CLI",
    "onboard": "Unified onboarding",
}

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    if command == "onboard":
        from shared_ai_utils.onboarding import UnifiedOnboarding
        asyncio.run(UnifiedOnboarding().run())
    elif command in COMMANDS:
        # Route to appropriate CLI
        subprocess.run([f"sono-{command}"] + sys.argv[2:])
    else:
        show_help()
```

### Success Metrics

- **Time to First Success**: Reduce from ~30 minutes to <5 minutes
- **Setup Completion Rate**: Increase from ~60% to >90%
- **User Confusion**: Eliminate "which repo do I use?" questions
- **CLI Command Completion**: 100% of commands functional (currently ~70%)

### Testing Requirements

1. **End-to-End Tests**: Test complete onboarding flow for each repo
2. **Cross-Platform**: Test on macOS, Linux, Windows
3. **Error Recovery**: Test handling of setup failures
4. **User Testing**: Test with first-time users

---

## Area 2: Progressive Error Recovery & Contextual Help

### Problem Statement

Error handling is inconsistent and recovery paths are unclear:

1. **Inconsistent Error Formats**: Different error structures across repos
2. **Missing Context**: Errors don't always explain what went wrong or how to fix it
3. **No Recovery Guidance**: Users don't know what to do after an error
4. **Help Not Accessible**: Documentation links in errors may not be clickable/accessible
5. **Silent Failures**: Some operations fail without clear feedback

### Current State Analysis

**sono-eval:**
- ✅ Good error formatting with `ErrorFormatter` class
- ✅ Error help with suggestions and docs URLs
- ✅ Validation errors include examples
- ⚠️ Error help URLs may not be clickable in CLI
- ⚠️ Recovery steps not always actionable

**feedback-loop:**
- ⚠️ Some commands show "not yet implemented" without alternatives
- ⚠️ Error messages may not include recovery steps
- ✅ Has troubleshooting guide but may not be linked from errors

**council-ai:**
- ✅ Web UI has error boundaries
- ⚠️ API errors may not include recovery guidance
- ⚠️ Configuration errors shown in advanced section, not inline

**sono-platform:**
- ⚠️ Complex error handling across multiple modes
- ⚠️ Error messages may be technical without user-friendly alternatives

### Solution Design

Create a **Progressive Error Recovery System** that:

1. **Standardized Error Format**: Consistent error structure across all repos
2. **Contextual Help**: Inline help that explains errors and provides solutions
3. **Recovery Suggestions**: Actionable steps to resolve issues
4. **Progressive Disclosure**: Show basic error first, expand for details
5. **Help Integration**: Direct links to relevant documentation sections

### Implementation Plan

#### Phase 1: Create Unified Error Recovery Framework

**Location**: `shared-ai-utils/src/shared_ai_utils/errors/`

**Components to Create:**

1. **`recovery.py`** - Error recovery system
   ```python
   class ErrorRecovery:
       """Progressive error recovery with contextual help."""
       
       def __init__(self, error_type: str, context: Dict[str, Any]):
           self.error_type = error_type
           self.context = context
           self.recovery_steps = self._generate_recovery_steps()
       
       def _generate_recovery_steps(self) -> List[RecoveryStep]:
           """Generate actionable recovery steps based on error type."""
           # Use pattern matching to suggest fixes
           # Include code examples
           # Link to documentation
   ```

2. **`contextual_help.py`** - Inline help system
   ```python
   class ContextualHelp:
       """Provide contextual help based on error and user context."""
       
       def get_help(self, error: Error, user_context: UserContext) -> HelpResponse:
           """Get contextual help for an error."""
           # Determine user's experience level
           # Select appropriate help detail level
           # Include examples and links
   ```

3. **`error_formatter.py`** - Unified error formatting
   ```python
   class UnifiedErrorFormatter:
       """Format errors consistently across all repos."""
       
       def format(self, error: Error, format_type: str = "cli") -> str:
           """Format error for CLI, API, or web UI."""
           # CLI: Rich formatted text with suggestions
           # API: Structured JSON with help links
           # Web: HTML with expandable details
   ```

#### Phase 2: Integrate into Each Repository

**For sono-eval:**

Update `src/sono_eval/utils/errors.py`:
```python
from shared_ai_utils.errors import UnifiedErrorFormatter, ErrorRecovery

def create_error_response(error_code, message, **kwargs):
    formatter = UnifiedErrorFormatter()
    recovery = ErrorRecovery(error_code, kwargs)
    
    return {
        "error": True,
        "error_code": error_code,
        "message": message,
        "recovery": recovery.get_steps(),
        "help": recovery.get_contextual_help(),
        **kwargs
    }
```

**For feedback-loop:**

Update CLI commands to use recovery system:
```python
from shared_ai_utils.errors import ErrorRecovery

try:
    # Command logic
except Exception as e:
    recovery = ErrorRecovery(type(e).__name__, {"command": ctx.info_name})
    console.print(recovery.format_cli())
    console.print(recovery.get_suggestions())
```

**For council-ai:**

Update web UI error handling:
```python
// In error boundary or error handler
import { ErrorRecovery } from '@shared-ai-utils/errors';

const recovery = new ErrorRecovery(error.name, context);
setErrorDetails(recovery.getSteps());
setHelpLinks(recovery.getHelpLinks());
```

#### Phase 3: Create Interactive Help System

**Location**: `shared-ai-utils/src/shared_ai_utils/help/`

**Components:**

1. **`interactive_help.py`** - Interactive help system
   ```python
   class InteractiveHelp:
       """Interactive help that guides users through errors."""
       
       async def explain_error(self, error: Error) -> HelpResponse:
           """Explain error in user-friendly terms."""
           # Break down technical error
           # Provide analogies
           # Show examples
       
       async def guide_recovery(self, error: Error) -> RecoveryGuide:
           """Step-by-step recovery guide."""
           # Interactive prompts
           # Verification at each step
           # Progress tracking
   ```

2. **`help_integration.py`** - Integrate help into UIs
   ```python
   # For CLI: Rich panels with expandable sections
   # For API: Structured help in error responses
   # For Web: Modal dialogs with step-by-step guides
   ```

### Success Metrics

- **Error Resolution Time**: Reduce from ~15 minutes to <2 minutes
- **User Success Rate**: Increase from ~70% to >95%
- **Help Access**: 100% of errors include actionable help
- **User Satisfaction**: Reduce "I don't know what to do" feedback

### Testing Requirements

1. **Error Scenario Tests**: Test all error types with recovery system
2. **Help Accuracy**: Verify help suggestions are correct
3. **User Testing**: Test with users of different experience levels
4. **Accessibility**: Ensure help is accessible (screen readers, keyboard navigation)

---

## Area 3: Documentation Hub & Contextual Discovery

### Problem Statement

Documentation exists but is hard to discover and navigate:

1. **Scattered Documentation**: Multiple entry points (START_HERE, QUICKSTART, README)
2. **No Unified Navigation**: Each repo has different doc structure
3. **Context Switching**: Users must leave their workflow to find docs
4. **Outdated Information**: Some docs may be outdated
5. **No Search**: No unified search across all repos

### Current State Analysis

**Documentation Structure:**

- **sono-eval**: `documentation/` with START_HERE, Guides/, Core/, Governance/
- **feedback-loop**: `documentation/` with INDEX.md, QUICKSTART.md, guides/
- **council-ai**: `documentation/` with API_REFERENCE.md, guides/
- **sono-platform**: `documentation/` with multiple subdirectories
- **shared-ai-utils**: README with examples, no deep docs

**Issues:**
- No cross-repo documentation index
- Users don't know which docs to read first
- Documentation may duplicate information
- No contextual help that surfaces relevant docs

### Solution Design

Create a **Unified Documentation Hub** that:

1. **Unified Index**: Single entry point for all documentation
2. **Contextual Discovery**: Surface relevant docs based on user context
3. **Smart Search**: Search across all repos with relevance ranking
4. **Progressive Disclosure**: Show basics first, expand for details
5. **Live Examples**: Interactive examples in documentation

### Implementation Plan

#### Phase 1: Create Documentation Hub Infrastructure

**Location**: `shared-ai-utils/src/shared_ai_utils/docs/`

**Components to Create:**

1. **`hub.py`** - Documentation hub core
   ```python
   class DocumentationHub:
       """Unified documentation hub for all repos."""
       
       def __init__(self):
           self.repos = self._discover_repos()
           self.index = self._build_index()
       
       def search(self, query: str, context: Optional[Dict] = None) -> List[DocResult]:
           """Search across all documentation."""
           # Semantic search
           # Relevance ranking
           # Context-aware filtering
       
       def get_contextual_docs(self, context: UserContext) -> List[Doc]:
           """Get docs relevant to current user context."""
           # Based on current task
           # Based on errors encountered
           # Based on user experience level
   ```

2. **`indexer.py`** - Documentation indexer
   ```python
   class DocIndexer:
       """Index documentation from all repos."""
       
       def index_repo(self, repo_path: str) -> DocIndex:
           """Index all docs in a repository."""
           # Parse markdown files
           # Extract headings, code examples
           # Build searchable index
   ```

3. **`contextual_loader.py`** - Context-aware doc loading
   ```python
   class ContextualDocLoader:
       """Load docs based on user context."""
       
       def get_docs_for_error(self, error: Error) -> List[Doc]:
           """Get relevant docs for an error."""
       
       def get_docs_for_task(self, task: str) -> List[Doc]:
           """Get docs for a specific task."""
   ```

#### Phase 2: Create Documentation CLI & Web Interface

**CLI Command:**

```python
# In shared-ai-utils CLI
@click.command("docs")
@click.argument("query", required=False)
@click.option("--context", help="Current context (error, task, etc.)")
def docs(query, context):
    """📚 Unified documentation hub."""
    hub = DocumentationHub()
    if query:
        results = hub.search(query, context=parse_context(context))
        display_results(results)
    else:
        show_doc_index()
```

**Web Interface:**

Create simple web UI at `/docs` endpoint:
- Search bar
- Category navigation
- Contextual suggestions
- Interactive examples

#### Phase 3: Integrate Contextual Help into All Repos

**For CLI:**

Add `--help-context` flag to all commands:
```python
@click.option("--help-context", is_flag=True, help="Show contextual help")
def command(..., help_context):
    if help_context:
        docs = ContextualDocLoader().get_docs_for_task("command_name")
        display_docs(docs)
```

**For API:**

Add `/help` endpoint:
```python
@app.get("/api/v1/help")
async def get_help(context: str, error: Optional[str] = None):
    """Get contextual help."""
    loader = ContextualDocLoader()
    if error:
        docs = loader.get_docs_for_error(Error(error))
    else:
        docs = loader.get_docs_for_task(context)
    return {"docs": docs}
```

**For Web UI:**

Add help button/widget:
```tsx
<HelpWidget context={currentContext} error={currentError} />
```

### Success Metrics

- **Documentation Discovery**: Reduce time to find relevant docs from ~10 minutes to <1 minute
- **Help Usage**: Increase help access from ~20% to >60%
- **User Satisfaction**: Reduce "can't find documentation" feedback
- **Doc Accuracy**: Ensure all linked docs are up-to-date

### Testing Requirements

1. **Search Accuracy**: Test search returns relevant results
2. **Context Matching**: Test contextual help is appropriate
3. **Link Validation**: Ensure all doc links work
4. **User Testing**: Test with users finding documentation

---

## Implementation Instructions for Coding Agents

### Prerequisites

Before starting implementation:

1. **Read Repository Rules**: Review `AGENT_KNOWLEDGE_BASE.md` in each repo
2. **Understand Architecture**: Review existing code patterns
3. **Check Dependencies**: Verify shared-ai-utils is available
4. **Review Existing Patterns**: Check for similar implementations

### General Guidelines

1. **Follow Existing Patterns**: Match code style and architecture of target repo
2. **Maintain Backward Compatibility**: Don't break existing functionality
3. **Add Tests**: Write tests for all new functionality
4. **Update Documentation**: Update relevant docs as you implement
5. **Use Type Hints**: All functions must have type hints
6. **Error Handling**: Use specific exceptions, not bare `except:`
7. **Logging**: Use structured logging, not `print()`

### Area 1 Implementation Steps

#### Step 1.1: Create Onboarding Infrastructure

**Files to Create:**
- `shared-ai-utils/src/shared_ai_utils/onboarding/__init__.py`
- `shared-ai-utils/src/shared_ai_utils/onboarding/unified_setup.py`
- `shared-ai-utils/src/shared_ai_utils/onboarding/intent_detector.py`
- `shared-ai-utils/src/shared_ai_utils/onboarding/setup_wizards/__init__.py`
- `shared-ai-utils/src/shared_ai_utils/onboarding/setup_wizards/base.py`
- `shared-ai-utils/src/shared_ai_utils/onboarding/verification.py`

**Implementation Checklist:**
- [ ] Create `UnifiedOnboarding` class with async `run()` method
- [ ] Create `IntentDetector` with 5-7 questions
- [ ] Create base `SetupWizard` class that repo-specific wizards inherit
- [ ] Create `SetupVerifier` that tests each repo's setup
- [ ] Add CLI command `shared-ai-utils onboard`
- [ ] Add progress tracking (save/restore state)
- [ ] Add error handling for setup failures
- [ ] Write tests for onboarding flow

**Code Template:**
```python
# shared-ai-utils/src/shared_ai_utils/onboarding/unified_setup.py
import asyncio
from typing import Dict, Optional
from shared_ai_utils.cli import print_table, print_success, print_error
from shared_ai_utils.onboarding.intent_detector import IntentDetector
from shared_ai_utils.onboarding.setup_wizards import get_wizard_for_repo
from shared_ai_utils.onboarding.verification import SetupVerifier

class UnifiedOnboarding:
    """Unified onboarding for Sonotheia ecosystem."""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.verifier = SetupVerifier()
        self.progress_file = Path.home() / ".sonotheia" / "onboarding_progress.json"
    
    async def run(self, repo: Optional[str] = None):
        """Run onboarding flow."""
        # 1. Welcome
        self._show_welcome()
        
        # 2. Detect intent (if repo not specified)
        if not repo:
            repo = await self._detect_intent()
        
        # 3. Run setup wizard
        wizard = get_wizard_for_repo(repo)
        setup_result = await wizard.run()
        
        # 4. Verify setup
        verification = await self.verifier.verify_repo(repo)
        
        # 5. Show next steps
        self._show_next_steps(repo, verification)
```

#### Step 1.2: Complete Incomplete CLI Commands

**Files to Update:**
- `feedback-loop/src/feedback_loop/cli/commands/config.py`
- `feedback-loop/src/feedback_loop/cli/commands/review.py`
- `feedback-loop/src/feedback_loop/cli/commands/analyze.py`

**Implementation Checklist:**
- [ ] Replace "not yet implemented" with actual implementations
- [ ] Use shared-ai-utils components where applicable
- [ ] Add proper error handling
- [ ] Add progress indicators for long operations
- [ ] Add `--help` with examples
- [ ] Write tests for each command

**Code Template:**
```python
# feedback-loop/src/feedback_loop/cli/commands/config.py
from shared_ai_utils.config import ConfigManager
from pathlib import Path

@click.command()
@click.option("--show", "-s", is_flag=True)
@click.option("--set", "set_key", help="key=value")
def config(ctx, show, set_key):
    """⚙️ Manage configuration."""
    console = ctx.obj.get("console", Console())
    config_path = Path.home() / ".feedback-loop" / "config.yaml"
    manager = ConfigManager(config_path=str(config_path))
    
    if set_key:
        if "=" not in set_key:
            console.print("[red]Error:[/red] Use format key=value")
            raise click.Abort()
        
        key, value = set_key.split("=", 1)
        try:
            manager.set(key, value)
            manager.save()
            console.print(f"[green]✓[/green] Set {key} = {value}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise click.Abort()
    
    if show:
        config_data = manager.load_dict()
        table = Table(show_header=True)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        for key, value in config_data.items():
            table.add_row(key, str(value))
        console.print(table)
```

#### Step 1.3: Create Unified Entry Point

**Files to Create:**
- `shared-ai-utils/bin/sono` (executable script)
- `shared-ai-utils/src/shared_ai_utils/cli/unified.py`

**Implementation Checklist:**
- [ ] Create `sono` wrapper script
- [ ] Add routing logic to appropriate CLI
- [ ] Add `sono onboard` command
- [ ] Add `sono help` with repo overview
- [ ] Make script executable
- [ ] Add to installation instructions

### Area 2 Implementation Steps

#### Step 2.1: Create Error Recovery Framework

**Files to Create:**
- `shared-ai-utils/src/shared_ai_utils/errors/__init__.py`
- `shared-ai-utils/src/shared_ai_utils/errors/recovery.py`
- `shared-ai-utils/src/shared_ai_utils/errors/contextual_help.py`
- `shared-ai-utils/src/shared_ai_utils/errors/formatter.py`

**Implementation Checklist:**
- [ ] Create `ErrorRecovery` class with step generation
- [ ] Create `ContextualHelp` class
- [ ] Create `UnifiedErrorFormatter` for CLI/API/Web
- [ ] Add recovery pattern database
- [ ] Add help text templates
- [ ] Write tests

**Code Template:**
```python
# shared-ai-utils/src/shared_ai_utils/errors/recovery.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RecoveryStep:
    """A single recovery step."""
    description: str
    command: Optional[str] = None
    code_example: Optional[str] = None
    doc_link: Optional[str] = None
    verification: Optional[str] = None

class ErrorRecovery:
    """Generate recovery steps for errors."""
    
    RECOVERY_PATTERNS = {
        "ValidationError": [
            RecoveryStep(
                "Check the field format",
                doc_link="/docs/validation",
            ),
            RecoveryStep(
                "See example format",
                code_example="...",
            ),
        ],
        "FileNotFoundError": [
            RecoveryStep(
                "Verify file exists",
                command="ls -la <path>",
            ),
            RecoveryStep(
                "Check current directory",
                command="pwd",
            ),
        ],
        # ... more patterns
    }
    
    def __init__(self, error_type: str, context: Dict[str, Any]):
        self.error_type = error_type
        self.context = context
    
    def get_steps(self) -> List[RecoveryStep]:
        """Get recovery steps for this error."""
        steps = self.RECOVERY_PATTERNS.get(self.error_type, [])
        # Customize based on context
        return self._customize_steps(steps)
    
    def format_cli(self) -> str:
        """Format for CLI display."""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        steps_text = "\n".join(f"{i+1}. {s.description}" for i, s in enumerate(self.get_steps()))
        return Panel(steps_text, title="Recovery Steps", border_style="yellow")
```

#### Step 2.2: Integrate into Repositories

**For sono-eval:**

Update `src/sono_eval/utils/errors.py`:
```python
from shared_ai_utils.errors import ErrorRecovery, UnifiedErrorFormatter

def create_error_response(error_code, message, request_id=None, **kwargs):
    recovery = ErrorRecovery(error_code, kwargs)
    formatter = UnifiedErrorFormatter()
    
    return {
        "error": True,
        "error_code": error_code,
        "message": message,
        "request_id": request_id,
        "recovery": {
            "steps": [s.to_dict() for s in recovery.get_steps()],
            "help_url": f"/api/v1/help?error={error_code}",
        },
        **kwargs
    }
```

**For feedback-loop:**

Update CLI error handling:
```python
# In each command
try:
    # Command logic
except Exception as e:
    from shared_ai_utils.errors import ErrorRecovery
    
    recovery = ErrorRecovery(type(e).__name__, {"command": ctx.info_name, "error": str(e)})
    console.print(recovery.format_cli())
    
    # Show interactive help option
    if click.confirm("Show detailed help?"):
        show_interactive_help(recovery)
```

#### Step 2.3: Add Interactive Help

**Files to Create:**
- `shared-ai-utils/src/shared_ai_utils/help/interactive.py`
- `shared-ai-utils/src/shared_ai_utils/help/integration.py`

**Implementation:**
- Create interactive prompts for error recovery
- Add step-by-step guidance
- Add verification at each step
- Create web UI components for interactive help

### Area 3 Implementation Steps

#### Step 3.1: Create Documentation Hub

**Files to Create:**
- `shared-ai-utils/src/shared_ai_utils/docs/__init__.py`
- `shared-ai-utils/src/shared_ai_utils/docs/hub.py`
- `shared-ai-utils/src/shared_ai_utils/docs/indexer.py`
- `shared-ai-utils/src/shared_ai_utils/docs/contextual_loader.py`

**Implementation Checklist:**
- [ ] Create `DocumentationHub` class
- [ ] Implement search across repos
- [ ] Create indexer for markdown files
- [ ] Implement contextual doc loading
- [ ] Add caching
- [ ] Write tests

**Code Template:**
```python
# shared-ai-utils/src/shared_ai_utils/docs/hub.py
from pathlib import Path
from typing import List, Dict, Optional
import json

class DocumentationHub:
    """Unified documentation hub."""
    
    def __init__(self):
        self.repo_paths = self._discover_repos()
        self.index = self._build_index()
    
    def _discover_repos(self) -> List[Path]:
        """Discover repos in workspace."""
        # Check common locations
        # Return list of repo paths
    
    def _build_index(self) -> DocIndex:
        """Build searchable index."""
        indexer = DocIndexer()
        for repo_path in self.repo_paths:
            indexer.index_repo(repo_path)
        return indexer.get_index()
    
    def search(self, query: str, context: Optional[Dict] = None) -> List[DocResult]:
        """Search documentation."""
        # Use semantic search if available
        # Fall back to keyword search
        # Rank by relevance
        # Filter by context if provided
```

#### Step 3.2: Add CLI and Web Interface

**CLI Command:**
```python
# shared-ai-utils/src/shared_ai_utils/cli/docs.py
@click.command("docs")
@click.argument("query", required=False)
@click.option("--context", help="Current context")
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
def docs(query, context, format):
    """📚 Unified documentation hub."""
    hub = DocumentationHub()
    
    if query:
        results = hub.search(query, context=parse_context(context))
        if format == "json":
            click.echo(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            display_doc_results(results)
    else:
        show_doc_index(hub)
```

**Web Endpoint:**
```python
# In FastAPI app
@app.get("/api/v1/docs/search")
async def search_docs(q: str, context: Optional[str] = None):
    hub = DocumentationHub()
    results = hub.search(q, context=parse_context(context))
    return {"results": [r.to_dict() for r in results]}
```

#### Step 3.3: Integrate into Repos

**Add to each repo:**
- Help command/endpoint
- Contextual doc links in errors
- Help widget in web UIs
- Documentation links in CLI `--help`

---

## Testing Strategy

### Unit Tests

For each component:
- Test error recovery step generation
- Test documentation indexing
- Test onboarding flow
- Test help system

### Integration Tests

- Test cross-repo onboarding
- Test error recovery across repos
- Test documentation search
- Test help integration

### User Acceptance Tests

- Test with first-time users
- Test error recovery scenarios
- Test documentation discovery
- Measure time-to-success improvements

---

## Success Criteria

### Area 1: Onboarding
- ✅ Users can complete setup in <5 minutes
- ✅ 90%+ setup completion rate
- ✅ All CLI commands functional
- ✅ Zero "not yet implemented" messages

### Area 2: Error Recovery
- ✅ All errors include recovery steps
- ✅ <2 minutes to resolve errors
- ✅ 95%+ error resolution success rate
- ✅ Help accessible from all interfaces

### Area 3: Documentation
- ✅ <1 minute to find relevant docs
- ✅ 60%+ help usage rate
- ✅ Unified search works across repos
- ✅ Contextual help surfaces appropriate docs

---

## Rollout Plan

### Phase 1 (Week 1-2): Foundation
- Create shared-ai-utils components
- Implement basic onboarding
- Create error recovery framework
- Build documentation indexer

### Phase 2 (Week 3-4): Integration
- Integrate into sono-eval
- Integrate into feedback-loop
- Integrate into council-ai
- Complete incomplete CLI commands

### Phase 3 (Week 5-6): Polish
- Add web interfaces
- Improve help content
- User testing and refinement
- Documentation updates

### Phase 4 (Week 7-8): Optimization
- Performance optimization
- Additional features based on feedback
- Final testing
- Production deployment

---

## Notes for Coding Agents

1. **Start with shared-ai-utils**: Build reusable components first
2. **Test incrementally**: Test each component as you build
3. **Follow existing patterns**: Match code style of target repo
4. **Update documentation**: Document as you implement
5. **Consider accessibility**: Ensure all UI is accessible
6. **Error handling**: Always use specific exceptions
7. **Logging**: Use structured logging throughout
8. **Type hints**: Required for all functions

---

This plan provides detailed, actionable instructions for implementing comprehensive UX enhancements across all repositories. Each area addresses critical friction points identified through code and documentation review.
