# CORS Checker

A command-line tool to check Cross-Origin Resource Sharing (CORS) configuration between domains.

## Overview

CORS Checker allows you to verify if a target domain allows cross-origin requests from a specified origin domain. This is useful for:

- Testing CORS configuration during development
- Debugging CORS issues in production
- Verifying security policies

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cors_checker.git
   cd cors_checker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make the script executable (Unix/Linux/macOS):
   ```
   chmod +x cors_checker.py
   ```

## Usage

Basic usage:
```
./cors_checker.py <origin> <target>
```

Where:
- `<origin>` is the domain where the request is coming from (e.g., https://example.com)
- `<target>` is the domain where the request is going to (e.g., https://api.example.com)

### Options

- `-m, --method METHOD`: HTTP method to use (default: GET)
- `-H, --headers HEADER [HEADER ...]`: Additional headers to include in the request. Headers can be specified in the format "name:value" (e.g., "Content-Type:application/json"). If no value is provided, an empty string will be used as the value.
- `-v, --verbose`: Print detailed information about the requests and responses
- `-t, --timeout SECONDS`: Request timeout in seconds (default: 10)
- `-j, --json`: Output results in JSON format

### Examples

1. Basic check:
   ```
   ./cors_checker.py https://example.com https://api.example.com
   ```

2. Check with a specific HTTP method:
   ```
   ./cors_checker.py https://example.com https://api.example.com -m POST
   ```

3. Check with custom headers:
   ```
   ./cors_checker.py https://example.com https://api.example.com -H Content-Type:application/json X-Custom-Header:12345
   ```

4. Verbose output:
   ```
   ./cors_checker.py https://example.com https://api.example.com -v
   ```

5. JSON format output:
   ```
   ./cors_checker.py https://example.com https://api.example.com -j
   ```

6. Custom timeout:
   ```
   ./cors_checker.py https://example.com https://api.example.com -t 5
   ```

## How It Works

The tool performs the following steps:

1. Sends an OPTIONS preflight request to the target domain with the specified origin
2. Checks if the response includes the necessary CORS headers
3. Verifies if the specified origin is allowed
4. Performs an actual request with the specified method
5. Checks if the actual response also includes the necessary CORS headers

## Response Structure

When using the JSON output option (`-j`), the tool returns a structured response:

```json
{
  "success": true|false,
  "message": "CORS is properly configured"|"CORS is not properly configured"|"Error message",
  "preflight_check": {
    "allowed": true|false,
    "status_code": 200,
    "headers": { ... },
    "allowed_origin": "*"|"https://example.com"
  },
  "actual_check": {
    "allowed": true|false,
    "status_code": 200,
    "headers": { ... },
    "allowed_origin": "*"|"https://example.com"
  },
  "details": { ... }
}
```

## Exit Codes

- `0`: CORS is properly configured
- `1`: CORS is not properly configured or an error occurred

## Claude Desktop Integration

To use CORS Checker with Claude Desktop, add the following configuration to your Claude Desktop settings:

```json
"CORS Checker": {
    "command": "uv",
    "args": [
        "--directory",
        "/Users/simgyumin/projects/cors_checker",
        "run",
        "python",
        "cors_check_mcp.py"
    ]
}
```

### MCP (Model Context Protocol) Tools

The CORS Checker provides the following MCP tools:

1. `check_cors`: Check CORS configuration and return results as text
   ```python
   check_cors(origin, target, method="GET", headers=None, verbose=False, timeout=10)
   ```

2. `check_cors_json`: Check CORS configuration and return results as JSON
   ```python
   check_cors_json(origin, target, method="GET", headers=None, verbose=False, timeout=10)
   ```

3. `validate_domain_url`: Check if a URL is valid
   ```python
   validate_domain_url(url)
   ```

### MCP Prompts

The following prompts are available:

1. `cors_check_prompt`: For basic CORS checks
2. `cors_check_common_issues`: For troubleshooting common CORS issues

## Recent Updates

### Version 1.1.0 (2025-05-20)

- Added timeout configuration option (`-t`, `--timeout`)
- Added JSON format output option (`-j`, `--json`)
- Improved error handling with specific error messages
- Enhanced headers parsing logic
- Structured response data for better programmatic usage
- Added new MCP tools:
  - `check_cors_json` for JSON output
  - `validate_domain_url` for URL validation
- Added new MCP prompt for common CORS issues troubleshooting
