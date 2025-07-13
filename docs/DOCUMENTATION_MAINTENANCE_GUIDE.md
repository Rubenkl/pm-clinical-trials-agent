# Documentation Maintenance Guide

**Last Updated:** July 11, 2025  
**Purpose:** Ensure documentation stays accurate and useful

## 📋 Documentation Principles

1. **Single Source of Truth**: Each piece of information should have ONE authoritative location
2. **DRY (Don't Repeat Yourself)**: Reference, don't duplicate
3. **Keep It Current**: Update docs with code changes
4. **Clear Hierarchy**: Use MASTER_DOCUMENTATION.md as the central hub
5. **Version Everything**: Track changes in CHANGELOG.md

## 🗂️ Documentation Structure

```
MASTER_DOCUMENTATION.md     # Central reference - links to everything
├── README.md              # Quick start only - refers to master doc
├── CHANGELOG.md           # Version history and updates
├── backend/
│   ├── README.md          # Backend quick start
│   ├── API_DOCUMENTATION.md    # Authoritative API reference
│   └── AGENT_OUTPUT_SCHEMAS.md # Agent response formats
├── frontend/
│   └── CLAUDE.md          # Frontend documentation
└── product-management/
    └── roadmaps/
        └── CURRENT_SPRINT.md   # Always-current sprint status
```

## ✅ When Making Code Changes

### 1. Before Starting Work
- [ ] Check CURRENT_SPRINT.md for priorities
- [ ] Read relevant documentation section
- [ ] Note any outdated information

### 2. After Code Changes
- [ ] Update API_DOCUMENTATION.md if endpoints changed
- [ ] Update AGENT_OUTPUT_SCHEMAS.md if responses changed
- [ ] Update relevant section in MASTER_DOCUMENTATION.md
- [ ] Add entry to CHANGELOG.md (unreleased section)
- [ ] Update "Last Updated" dates

### 3. For Breaking Changes
- [ ] Update all affected documentation
- [ ] Add migration guide to CHANGELOG.md
- [ ] Notify frontend team if API changes
- [ ] Update version number

## 📝 Documentation Checklist by Component

### Backend Changes
```markdown
- [ ] API_DOCUMENTATION.md - New/changed endpoints?
- [ ] AGENT_OUTPUT_SCHEMAS.md - New/changed agent outputs?
- [ ] backend/README.md - New setup requirements?
- [ ] MASTER_DOCUMENTATION.md - Architecture changes?
- [ ] Test documentation - New test scenarios?
```

### Frontend Changes
```markdown
- [ ] frontend/CLAUDE.md - New features/components?
- [ ] frontend/DEMO_GUIDE.md - New demo scenarios?
- [ ] API integration docs - New service calls?
- [ ] MASTER_DOCUMENTATION.md - UI changes?
```

### Agent Changes
```markdown
- [ ] Agent descriptions in MASTER_DOCUMENTATION.md
- [ ] AGENT_OUTPUT_SCHEMAS.md - Output format changes?
- [ ] API endpoints that use the agent
- [ ] Test cases for new functionality
- [ ] Performance metrics updates
```

## 🔄 Regular Maintenance Tasks

### Weekly
- Review CURRENT_SPRINT.md and update progress
- Check for completed TODOs in code
- Update sprint completion percentage

### Monthly
- Review and update "Last Updated" dates
- Archive completed sprint documentation
- Check for outdated examples
- Review open issues for doc updates needed

### Quarterly
- Comprehensive documentation review
- Archive outdated documents
- Update performance metrics
- Review and update roadmaps
- Clean up redundant content

## 📊 Documentation Standards

### File Headers
```markdown
# Document Title

**Last Updated:** YYYY-MM-DD  
**Version:** X.Y (if applicable)  
**Status:** Draft/Review/Final/Deprecated

## Purpose
Brief description of what this document covers
```

### API Endpoint Documentation
```markdown
### Endpoint Name
**Method:** POST  
**Path:** `/api/v1/resource`  
**Description:** What it does

**Request Body:**
```json
{
  "field": "type and description"
}
```

**Response:**
```json
{
  "field": "type and description"  
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/resource \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```
```

### Code Examples
- Always test before documenting
- Include expected output
- Provide context and explanation
- Use real data from test system

## 🚫 Common Pitfalls to Avoid

1. **Updating code without docs** - Always update together
2. **Copy-pasting content** - Reference instead
3. **Outdated examples** - Test all examples
4. **Missing dates** - Always update "Last Updated"
5. **Vague descriptions** - Be specific and clear
6. **Assuming context** - Write for new developers
7. **Forgetting CHANGELOG** - Track all changes

## 🛠️ Useful Commands

### Find Outdated Documentation
```bash
# Find files not updated in 30 days
find . -name "*.md" -mtime +30 -type f | grep -v node_modules

# Search for TODOs in documentation
grep -r "TODO" --include="*.md" .

# Find duplicate content (manual review needed)
grep -r "Git subtree" --include="*.md" .
```

### Update Last Updated Dates
```bash
# Manual process - update when editing
# Future: Consider automation with git hooks
```

## 📋 Documentation Review Template

When reviewing documentation:

```markdown
## Documentation Review - [Date]

### Reviewed Files
- [ ] MASTER_DOCUMENTATION.md
- [ ] Backend documentation
- [ ] Frontend documentation
- [ ] API documentation
- [ ] Sprint/roadmap docs

### Findings
- Outdated: [List files/sections]
- Missing: [List gaps]
- Redundant: [List duplicates]
- Unclear: [List confusing sections]

### Actions Taken
- Updated: [List updates]
- Archived: [List archived files]
- Created: [List new docs]

### Next Review Date: [Date]
```

## 🎯 Quick Reference

### What Goes Where?
- **Architecture decisions** → MASTER_DOCUMENTATION.md
- **API changes** → API_DOCUMENTATION.md
- **Agent outputs** → AGENT_OUTPUT_SCHEMAS.md
- **Version history** → CHANGELOG.md
- **Sprint updates** → CURRENT_SPRINT.md
- **Setup instructions** → Component README.md
- **Historical docs** → /docs/archive/

### Who Updates What?
- **Developers**: API docs, schemas, technical guides
- **Product Managers**: Sprint docs, roadmaps, PRDs
- **Tech Leads**: Architecture, master documentation
- **Everyone**: CHANGELOG.md entries

## 📞 Getting Help

If documentation is unclear or missing:
1. Check MASTER_DOCUMENTATION.md first
2. Search existing documentation
3. Ask in team chat
4. Create an issue for missing docs
5. Contribute improvements via PR

Remember: Good documentation is a team effort!