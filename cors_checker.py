#!/usr/bin/env python3
"""
CORS Checker - A CLI tool to check CORS configuration between domains.

This tool allows you to check if a target domain allows cross-origin requests
from a specified origin domain.
"""

import argparse
import requests
import sys
import json
from urllib.parse import urlparse

def validate_url(url):
    """Validate if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def parse_headers(headers):
    """Parse headers from string or list format into a dictionary."""
    if not headers:
        return {}

    header_dict = {}

    if isinstance(headers, str):
        headers = [headers]

    for header in headers:
        # 이름:값 형식으로 지정된 헤더 처리
        if ':' in header:
            name, value = header.split(':', 1)
            header_dict[name.strip()] = value.strip()
        else:
            # 값이 없는 경우 빈 문자열 사용
            header_dict[header.strip()] = ''

    return header_dict

def check_cors(origin, target, method="GET", headers=None, verbose=False, timeout=10):
    """
    Check CORS configuration between origin and target domains.

    Args:
        origin (str): The origin domain (where the request is coming from)
        target (str): The target domain (where the request is going to)
        method (str): HTTP method to use for the preflight request
        headers (list|str): Additional headers to include in the preflight request
        verbose (bool): Whether to print detailed information
        timeout (int): Request timeout in seconds

    Returns:
        dict: A dictionary containing CORS check results and details
    """
    result = {
        'success': False,
        'message': '',
        'preflight_check': {'allowed': False},
        'actual_check': {'allowed': False},
        'details': {}
    }

    if not validate_url(target):
        result['message'] = f"Error: '{target}' is not a valid URL. Include http:// or https://"
        if verbose:
            print(result['message'])
        return result

    if not validate_url(origin):
        result['message'] = f"Error: '{origin}' is not a valid URL. Include http:// or https://"
        if verbose:
            print(result['message'])
        return result

    if verbose:
        print(f"Checking CORS from {origin} to {target}")
        print(f"Method: {method}")
        if headers:
            print(f"Headers: {headers}")

    # Parse headers into dictionary
    parsed_headers = parse_headers(headers)

    # First, perform an OPTIONS preflight request
    try:
        options_headers = {
            'Origin': origin,
            'Access-Control-Request-Method': method
        }

        if parsed_headers:
            options_headers['Access-Control-Request-Headers'] = ','.join(parsed_headers.keys())

        if verbose:
            print("\nSending OPTIONS preflight request...")
            print(f"Request headers: {options_headers}")

        options_response = requests.options(target, headers=options_headers, timeout=timeout)

        if verbose:
            print(f"Status code: {options_response.status_code}")
            print("Response headers:")
            for key, value in options_response.headers.items():
                print(f"  {key}: {value}")

        result['preflight_check']['status_code'] = options_response.status_code
        result['preflight_check']['headers'] = dict(options_response.headers)

        # Check if CORS headers are present in the response
        cors_allowed = 'Access-Control-Allow-Origin' in options_response.headers

        # Check if the origin is allowed
        origin_allowed = False
        if cors_allowed:
            allowed_origin = options_response.headers.get('Access-Control-Allow-Origin')
            origin_allowed = allowed_origin == '*' or origin in allowed_origin

            result['preflight_check']['allowed'] = origin_allowed
            result['preflight_check']['allowed_origin'] = allowed_origin

            if verbose:
                if origin_allowed:
                    print(f"\nCORS is enabled for {origin}")
                else:
                    print(f"\nCORS is enabled but {origin} is not allowed")
                    print(f"Allowed origins: {allowed_origin}")
        else:
            if verbose:
                print("\nCORS headers are not present in the response")

        # Now perform the actual request
        if verbose:
            print(f"\nSending {method} request...")

        actual_headers = {'Origin': origin}

        # Add custom headers to the actual request
        actual_headers.update(parsed_headers)

        if verbose and parsed_headers:
            print(f"Including custom headers: {actual_headers}")

        actual_response = requests.request(method, target, headers=actual_headers, timeout=timeout)

        if verbose:
            print(f"Status code: {actual_response.status_code}")
            print("Response headers:")
            for key, value in actual_response.headers.items():
                print(f"  {key}: {value}")

        result['actual_check']['status_code'] = actual_response.status_code
        result['actual_check']['headers'] = dict(actual_response.headers)

        # Check if CORS headers are present in the actual response
        actual_cors_allowed = 'Access-Control-Allow-Origin' in actual_response.headers

        # Check if the origin is allowed in the actual response
        actual_origin_allowed = False
        if actual_cors_allowed:
            actual_allowed_origin = actual_response.headers.get('Access-Control-Allow-Origin')
            actual_origin_allowed = actual_allowed_origin == '*' or origin in actual_allowed_origin

            result['actual_check']['allowed'] = actual_origin_allowed
            result['actual_check']['allowed_origin'] = actual_allowed_origin

            if verbose:
                if actual_origin_allowed:
                    print(f"\nCORS is enabled for {origin} in the actual response")
                else:
                    print(f"\nCORS is enabled but {origin} is not allowed in the actual response")
                    print(f"Allowed origins: {actual_allowed_origin}")
        else:
            if verbose:
                print("\nCORS headers are not present in the actual response")

        # Final result
        success = cors_allowed and origin_allowed and actual_cors_allowed and actual_origin_allowed

        if verbose:
            if success:
                print("\nResult: CORS is properly configured")
            else:
                print("\nResult: CORS is not properly configured")

        result['success'] = success
        result['message'] = "CORS is properly configured" if success else "CORS is not properly configured"

        return result

    except requests.exceptions.Timeout:
        result['message'] = f"Error: Request to {target} timed out after {timeout} seconds"
        if verbose:
            print(result['message'])
        return result
    except requests.exceptions.ConnectionError:
        result['message'] = f"Error: Failed to connect to {target}"
        if verbose:
            print(result['message'])
        return result
    except requests.exceptions.RequestException as e:
        result['message'] = f"Error: {e}"
        if verbose:
            print(result['message'])
        return result

def main():
    parser = argparse.ArgumentParser(description='Check CORS configuration between domains')
    parser.add_argument('origin', help='The origin domain (where the request is coming from)')
    parser.add_argument('target', help='The target domain (where the request is going to)')
    parser.add_argument('-m', '--method', default='GET', help='HTTP method to use (default: GET)')
    parser.add_argument('-H', '--headers', nargs='+', help='Additional headers to include in the request')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed information')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-j', '--json', action='store_true', help='Output results in JSON format')

    args = parser.parse_args()

    result = check_cors(args.origin, args.target, args.method, args.headers, args.verbose, args.timeout)

    if args.json:
        # JSON 형식으로 결과 출력
        print(json.dumps(result, indent=2))
    elif not args.verbose:
        print(result['message'])

    sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
    main()
