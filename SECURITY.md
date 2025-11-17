# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions receive security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Instead, please report it via one of the following methods:

1. **Email**: Send details to security@yourdomain.com
2. **Private Security Advisory**: Use GitHub's private vulnerability reporting feature

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- We will acknowledge receipt within 48 hours
- We will provide an initial assessment within 7 days
- We will keep you informed of our progress

## Security Best Practices

When using SQL Agent:

1. **API Keys**: Never commit API keys to version control. Use environment variables or secure secret management.

2. **Database Access**: 
   - Use read-only database users when possible
   - Enable safe mode for untrusted inputs
   - Validate database paths and connections

3. **Input Validation**: 
   - Always validate user inputs
   - Use safe mode to block destructive operations
   - Set appropriate query length limits

4. **Network Security**:
   - Use HTTPS for API communications
   - Validate SSL certificates
   - Use secure connections for database access

5. **Logging**: 
   - Avoid logging sensitive data (API keys, passwords, PII)
   - Secure log file permissions
   - Rotate logs regularly

## Known Security Considerations

- **SQL Injection**: The agent generates SQL from natural language. While we validate queries, always use safe mode and validate inputs.
- **API Key Exposure**: Ensure API keys are stored securely and never logged.
- **Database Access**: The executor has direct database access. Use appropriate database permissions.

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2). We recommend keeping your installation up to date.

