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
- `-H, --headers HEADER [HEADER ...]`: Additional headers to include in the request
- `-v, --verbose`: Print detailed information about the requests and responses

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
   ./cors_checker.py https://example.com https://api.example.com -H Content-Type X-Custom-Header
   ```

4. Verbose output:
   ```
   ./cors_checker.py https://example.com https://api.example.com -v
   ```

## How It Works

The tool performs the following steps:

1. Sends an OPTIONS preflight request to the target domain with the specified origin
2. Checks if the response includes the necessary CORS headers
3. Verifies if the specified origin is allowed
4. Performs an actual request with the specified method
5. Checks if the actual response also includes the necessary CORS headers

## Exit Codes

- `0`: CORS is properly configured
- `1`: CORS is not properly configured or an error occurred

## License

MIT