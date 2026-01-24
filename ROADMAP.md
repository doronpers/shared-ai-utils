# Shared AI Utils - Roadmap & TODOs

**Last Updated**: 2026-01-24 (Updated with completed documentation tasks)
**Single Source of Truth**: This file contains all TODOs, planned features, and roadmap items.

---

## ✅ Recently Completed

### UX Enhancements (January 2026)

1. ✅ **Unified Onboarding System** - Interactive onboarding with intent detection, repository-specific setup wizards, and progress tracking
   - **CLI Command**: `shared-ai-utils onboard`
   - **Components**: Intent detector, setup wizards, verification system
   - **Status**: Complete and ready for integration
   - **Completed**: 2026-01-24

2. ✅ **Error Recovery Framework** - Automatic recovery steps for common errors with contextual help
   - **Features**: 10+ error patterns, actionable recovery steps, unified error formatting
   - **Integrated into**: sono-eval, feedback-loop
   - **Status**: Complete
   - **Completed**: 2026-01-24

3. ✅ **Documentation Hub** - Unified documentation search across all repositories
   - **Features**: Cross-repo documentation indexing, context-aware loading, relevance-based search
   - **CLI Command**: `shared-ai-utils docs "query"`
   - **Status**: Complete
   - **Completed**: 2026-01-24

### Integration & Adoption

4. ✅ **Council-AI Integration** - Council-AI has successfully migrated to use `shared_ai_utils.llm.LLMManager` and `shared_ai_utils.config.ConfigManager`
   - **Status**: Complete (verified in council-ai codebase)
   - **Completed**: 2026-01-16
   - **Reference**: Council-AI roadmap shows integration as completed

---

## 🔴 High Priority

*No high priority items at this time.*

---

## 🟡 Medium Priority

### Integration & Adoption

#### 1. Feedback-Loop Integration
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Feedback-loop should migrate to use `LLMManager` and `shared_ai_utils.patterns.PatternManager`
- **Reference**: `council-ai/planning/integration-plan.md`
- **Dependencies**: Feedback-loop migration completion

---

## 🟢 Low Priority

### Documentation

#### 3. Enhanced API Documentation
- **Status**: ✅ Completed (2026-01-24)
- **Complexity**: Low
- **Description**: Created comprehensive API_REFERENCE.md with detailed examples for all major components
- **Files**: `API_REFERENCE.md`
- **Components**: LLM, Config, Assessment, FastAPI, Patterns, Error Handling, CLI examples

#### 4. Migration Guides
- **Status**: ✅ Completed (2026-01-24)
- **Complexity**: Low-Medium
- **Description**: Created MIGRATION_GUIDE.md with step-by-step instructions based on council-ai migration experience
- **Files**: `MIGRATION_GUIDE.md`
- **Contents**: LLM migration, Config migration, Pattern migration, common issues, testing guide

### Testing

#### 5. Integration Test Suite
- **Status**: 📝 TODO
- **Description**: Add comprehensive integration tests for cross-module functionality

### Features

#### 6. Additional LLM Providers
- **Status**: 📝 TODO
- **Complexity**: Medium (per provider)
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Add support for additional LLM providers (e.g., Cohere, Mistral)

#### 7. Enhanced Pattern Search
- **Status**: 📝 TODO
- **Description**: Improve semantic search capabilities for pattern library

---

## 📋 Future Considerations

### Version 2.0 Features
- Enhanced async support across all modules
- Plugin system for custom providers
- Advanced caching strategies
- Performance optimizations

---

## 📊 Progress Summary

- **Completed**: 6 items
- **High Priority**: 0 items
- **Medium Priority**: 1 items
- **Low Priority**: 3 items

---

## 📝 Notes

- **Purpose**: This package consolidates functionality from multiple repositories
- **Related Projects**: See README.md for list of related projects
- **Contributing**: See CONTRIBUTING.md for contribution guidelines

---

## 🔄 How to Update This File

1. When starting work on a TODO, change status from `📝 TODO` to `🚧 In Progress`
2. When completing, move to "Recently Completed" section and mark as `✅`
3. Add new TODOs with complexity indicators (Low, Medium, High) rather than time estimates
4. Update "Last Updated" date
5. Keep items organized by priority and category
