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
- **Description**: Council-AI should migrate to use `shared_ai_utils.llm.LLMManager` and `shared_ai_utils.config.ConfigManager`
- **Reference**: `council-ai/planning/integration-plan.md`
- **Estimated Effort**: Dependent on council-ai migration

#### 2. Feedback-Loop Integration
- **Status**: 📝 TODO
- **Description**: Feedback-loop should migrate to use `LLMManager` and `shared_ai_utils.patterns.PatternManager`
- **Reference**: `council-ai/planning/integration-plan.md`
- **Estimated Effort**: Dependent on feedback-loop migration

---

## 🟢 Low Priority

### Documentation

#### 3. Enhanced API Documentation
- **Status**: 📝 TODO
- **Description**: Expand API reference documentation with more examples
- **Estimated Effort**: 2-3 hours

#### 4. Migration Guides
- **Status**: 📝 TODO
- **Description**: Create migration guides for repositories adopting shared-ai-utils
- **Estimated Effort**: 1-2 days

### Testing

#### 5. Integration Test Suite
- **Status**: 📝 TODO
- **Description**: Add comprehensive integration tests for cross-module functionality
- **Estimated Effort**: 2-3 days

### Features

#### 6. Additional LLM Providers
- **Status**: 📝 TODO
- **Description**: Add support for additional LLM providers (e.g., Cohere, Mistral)
- **Estimated Effort**: 1-2 days per provider

#### 7. Enhanced Pattern Search
- **Status**: 📝 TODO
- **Description**: Improve semantic search capabilities for pattern library
- **Estimated Effort**: 2-3 days

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
3. Add new TODOs with appropriate priority and estimated effort
4. Update "Last Updated" date
5. Keep items organized by priority and category
