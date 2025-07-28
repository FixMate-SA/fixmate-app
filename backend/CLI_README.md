# FixMate-SA CLI Commands

This document describes the command-line interface for FixMate-SA administration.

## Installation

The CLI commands are located in the `/app/backend/` directory. You can run them using:

```bash
cd /app/backend
python run_cli.py <command> [args...]
```

Or directly with:

```bash
cd /app/backend
python cli_commands.py <command> [args...]
```

## Available Commands

### User Management

#### `add-fixer <name> <phone> <skills>`
Add a new fixer to the system.

**Parameters:**
- `name`: Full name of the fixer
- `phone`: Phone number (10-digit SA format: 0821234567 or international: +27821234567)
- `skills`: Comma-separated list of skills (e.g., "plumbing,electrical,carpentry")

**Example:**
```bash
python run_cli.py add-fixer "John Smith" "0821234567" "plumbing,electrical"
```

#### `promote-admin <phone>`
Promote a user to admin status or create a new admin.

**Parameters:**
- `phone`: Phone number (10-digit SA format: 0821234567)

**Example:**
```bash
python run_cli.py promote-admin "0829876543"
```

#### `demote-admin <phone>`
Demote an admin to regular client status.

**Parameters:**
- `phone`: Phone number (10-digit SA format: 0821234567)

**Example:**
```bash
python run_cli.py demote-admin "0829876543"
```

#### `remove-fixer <phone>`
Remove a fixer from the system (with confirmation).

**Parameters:**
- `phone`: Phone number (10-digit SA format or international)

**Example:**
```bash
python run_cli.py remove-fixer "0821234567"
```

#### `remove-client <phone>`
Remove a client from the system (with confirmation).

**Parameters:**
- `phone`: Phone number (10-digit SA format or international)

**Example:**
```bash
python run_cli.py remove-client "0821234567"
```

#### `remove-all-clients`
Remove all non-admin clients and their associated jobs (with confirmation).

**Example:**
```bash
python run_cli.py remove-all-clients
```

### Information and Statistics

#### `stats`
Display system statistics including user count, fixer count, and job statistics.

**Example:**
```bash
python run_cli.py stats
```

#### `list-admins`
List all administrators in the system.

**Example:**
```bash
python run_cli.py list-admins
```

#### `list-jobs [--status <status>] [--limit <limit>]`
List jobs with optional filtering.

**Parameters:**
- `--status`: Filter by job status (pending, assigned, completed, etc.)
- `--limit`: Number of jobs to display (default: 20)

**Examples:**
```bash
python run_cli.py list-jobs
python run_cli.py list-jobs --status completed
python run_cli.py list-jobs --limit 10
```

### Job Management

#### `reassign-job <job_id> <fixer_phone>`
Reassign a job to a different fixer.

**Parameters:**
- `job_id`: Job ID (UUID)
- `fixer_phone`: Phone number of the new fixer

**Example:**
```bash
python run_cli.py reassign-job "12345678-1234-1234-1234-123456789012" "0821234567"
```

#### `toggle-fixer-active <phone>`
Toggle fixer active status (active/inactive).

**Parameters:**
- `phone`: Phone number of the fixer

**Example:**
```bash
python run_cli.py toggle-fixer-active "0821234567"
```

### AI and Analytics

#### `analyze-data`
Analyze job data and generate business insights using AI.

**Example:**
```bash
python run_cli.py analyze-data
```

#### `generate-insight`
Generate and display a new business insight.

**Example:**
```bash
python run_cli.py generate-insight
```

#### `list-insights [--limit <limit>]`
List recent business insights.

**Parameters:**
- `--limit`: Number of insights to display (default: 10)

**Example:**
```bash
python run_cli.py list-insights
python run_cli.py list-insights --limit 5
```

### WhatsApp Integration

#### `send-whatsapp <phone> <message>`
Send a WhatsApp message to a user.

**Parameters:**
- `phone`: Phone number (10-digit SA format or international)
- `message`: Message content

**Example:**
```bash
python run_cli.py send-whatsapp "0821234567" "Hello from FixMate-SA!"
```

### Data Management

#### `backup-data <output_file>`
Create a backup of system data in JSON format.

**Parameters:**
- `output_file`: Path to output file

**Example:**
```bash
python run_cli.py backup-data "/tmp/fixmate_backup.json"
```

## Phone Number Formats

The CLI accepts phone numbers in the following formats:
- **10-digit SA format**: 0821234567
- **International format**: +27821234567

All phone numbers are internally stored with the WhatsApp prefix: `whatsapp:+27821234567`

## Error Handling

The CLI includes comprehensive error handling:
- Database connection errors are handled gracefully
- Invalid phone number formats are rejected
- Missing entities are reported clearly
- Confirmation prompts prevent accidental deletions

## Examples

### Basic Setup
```bash
# Check system status
python run_cli.py stats

# Add a fixer
python run_cli.py add-fixer "Jane Doe" "0821234567" "plumbing,electrical"

# Promote an admin
python run_cli.py promote-admin "0829876543"

# List all admins
python run_cli.py list-admins
```

### Job Management
```bash
# List all jobs
python run_cli.py list-jobs

# List only completed jobs
python run_cli.py list-jobs --status completed

# Reassign a job
python run_cli.py reassign-job "12345678-1234-1234-1234-123456789012" "0821234567"
```

### Analytics
```bash
# Generate business insights
python run_cli.py generate-insight

# List recent insights
python run_cli.py list-insights --limit 5

# Run full data analysis
python run_cli.py analyze-data
```

### WhatsApp Features
```bash
# Send a message
python run_cli.py send-whatsapp "0821234567" "Your job has been assigned!"
```

## Requirements

- Python 3.8+
- PostgreSQL database
- All backend dependencies installed
- Environment variables configured (DATABASE_URL, API keys)

## Troubleshooting

### Database Connection Issues
If you encounter database connection errors, the CLI will attempt to recreate the database tables automatically.

### Missing API Keys
Some commands (like WhatsApp messaging and AI insights) require API keys to be configured in the environment variables. The CLI will provide appropriate fallback behavior when keys are missing.

### Permission Issues
Make sure the CLI script has execution permissions:
```bash
chmod +x /app/backend/fixmate-cli
```

## Security Notes

- CLI commands that perform destructive operations (delete, remove-all) require confirmation
- Phone numbers are validated before processing
- Database transactions are properly handled with rollback on errors
- Sensitive operations are logged for audit purposes