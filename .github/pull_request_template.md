# Pull Request

## Changes Summary
<!-- Provide a clear and concise description of what changes were made -->

### What was changed?
<!-- Describe the specific changes made to the codebase -->

### Why was this change needed?
<!-- Explain the motivation behind these changes -->

### Impact Assessment
<!-- Describe how this change affects the system, users, or other components -->

## Related Issues
<!-- Link to related issues using GitHub's automatic linking format -->
Closes #<!-- issue number -->
Related to #<!-- issue number -->

## Type of Change
<!-- Mark the type of change with an [x] -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Configuration change

## Testing Checklist
<!-- Ensure all relevant testing has been completed -->

### Unit Testing
- [ ] New unit tests added for new functionality
- [ ] Existing unit tests pass
- [ ] Code coverage maintained or improved

### Integration Testing
- [ ] Integration tests added/updated as needed
- [ ] All integration tests pass
- [ ] API endpoints tested (if applicable)

### Manual Testing
- [ ] Feature tested manually in development environment
- [ ] Edge cases and error scenarios tested
- [ ] User interface tested across different browsers/devices (if applicable)
- [ ] Performance impact assessed

### Testing Environment
- [ ] Tested locally
- [ ] Tested in development environment
- [ ] Tested in staging environment (if available)

## Breaking Changes
<!-- If this PR introduces breaking changes, describe them here -->
<!-- Include migration instructions for users/developers -->

### What breaks?
<!-- Describe what existing functionality will no longer work -->

### Migration Instructions
<!-- Provide step-by-step instructions for migrating existing code/configurations -->

### Backward Compatibility
<!-- Describe any backward compatibility measures taken -->

## Deployment Instructions
<!-- Provide specific instructions for deploying this change -->

### Pre-deployment Steps
- [ ] Database migrations (if any)
- [ ] Configuration updates required
- [ ] Environment variables to be set/updated
- [ ] Dependencies to be installed/updated

### Deployment Steps
1. <!-- Step-by-step deployment instructions -->

### Post-deployment Verification
- [ ] Application starts successfully
- [ ] Key functionality works as expected
- [ ] No errors in logs
- [ ] Performance metrics within acceptable range

### Rollback Plan
<!-- Describe how to rollback this change if issues arise -->
1. <!-- Step-by-step rollback instructions -->

## Documentation Updates
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Code comments added/updated
- [ ] Configuration documentation updated
- [ ] User documentation updated (if applicable)

## Security Considerations
- [ ] No sensitive information exposed in code
- [ ] Input validation implemented where needed
- [ ] Authentication/authorization properly handled
- [ ] Security best practices followed

## Performance Impact
<!-- Describe any performance implications -->
- [ ] No significant performance degradation
- [ ] Performance improvements measured and documented
- [ ] Resource usage impact assessed

## Screenshots/Demo
<!-- Add screenshots or demo links if this change affects the UI -->

## Additional Notes
<!-- Any additional information that reviewers should know -->

---

## Reviewer Guidelines

### Code Quality Checklist
- [ ] Code follows project coding standards and conventions
- [ ] Code is readable and well-documented
- [ ] No code duplication or unnecessary complexity
- [ ] Error handling is appropriate and consistent
- [ ] Logging is adequate for debugging and monitoring

### Security Review
- [ ] No hardcoded secrets or sensitive information
- [ ] Input validation and sanitization implemented
- [ ] Authentication and authorization properly implemented
- [ ] SQL injection and XSS vulnerabilities addressed
- [ ] Dependencies are up-to-date and secure

### Performance Review
- [ ] No obvious performance bottlenecks introduced
- [ ] Database queries are optimized
- [ ] Caching strategies implemented where appropriate
- [ ] Resource usage is reasonable

### Testing Review
- [ ] Test coverage is adequate
- [ ] Tests are meaningful and test the right things
- [ ] Edge cases are covered
- [ ] Tests are maintainable and not brittle

### Documentation Review
- [ ] Code is self-documenting or properly commented
- [ ] API changes are documented
- [ ] Configuration changes are documented
- [ ] User-facing changes are documented

### Deployment Review
- [ ] Deployment instructions are clear and complete
- [ ] Rollback plan is feasible
- [ ] Breaking changes are properly communicated
- [ ] Migration scripts are tested and safe

## Approval Workflow
<!-- This section defines the approval requirements -->

### Required Reviewers
- [ ] Code owner approval required
- [ ] Security team approval (for security-related changes)
- [ ] DevOps team approval (for infrastructure changes)

### Approval Criteria
- [ ] All automated checks pass (CI/CD pipeline)
- [ ] At least 2 approvals from team members
- [ ] All reviewer checklist items addressed
- [ ] No unresolved conversations

### Final Checks Before Merge
- [ ] Branch is up-to-date with target branch
- [ ] All CI/CD checks pass
- [ ] Required approvals obtained
- [ ] Deployment plan confirmed
- [ ] Stakeholders notified (if needed)