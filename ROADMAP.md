# Shared AI Utils - Roadmap & TODOs

**Last Updated**: 2026-01-16
**Single Source of Truth**: This file contains all TODOs, planned features, and roadmap items.

---

## ✅ Recently Completed

*No completed items to report yet.*

---

## 🔴 High Priority

*No high priority items at this time.*

---

## 🟡 Medium Priority

### Integration & Adoption

#### 1. Council-AI Integration
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Council-AI should migrate to use `shared_ai_utils.llm.LLMManager` and `shared_ai_utils.config.ConfigManager`
- **Reference**: `council-ai/planning/integration-plan.md`
- **Dependencies**: Council-AI migration completion

#### 2. Feedback-Loop Integration
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
- **Status**: 📝 TODO
- **Complexity**: Low
- **Recommended Models**: 1. Claude Sonnet 4.5, 2. GPT-5.1, 3. Gemini 3 Flash
- **Description**: Expand API reference documentation with more examples

#### 4. Migration Guides
- **Status**: 📝 TODO
- **Complexity**: Low-Medium
- **Recommended Models**: 1. Claude Sonnet 4.5, 2. GPT-5.1, 3. Gemini 3 Flash
- **Description**: Create migration guides for repositories adopting shared-ai-utils

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

- **Completed**: 0 items
- **High Priority**: 0 items
- **Medium Priority**: 2 items
- **Low Priority**: 5 items

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
