#!/usr/bin/env python3
"""
CORS Checker - A CLI tool to check CORS configuration between domains.

This tool allows you to check if a target domain allows cross-origin requests
from a specified origin domain.
"""

import argparse
import requests
import sys
from urllib.parse import urlparse

def validate_url(url):
    """Validate if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_cors(origin, target, method="GET", headers=None, verbose=False):
    """
    Check CORS configuration between origin and target domains.

    Args:
        origin (str): The origin domain (where the request is coming from)
        target (str): The target domain (where the request is going to)
        method (str): HTTP method to use for the preflight request
        headers (list): Additional headers to include in the preflight request
        verbose (bool): Whether to print detailed information

    Returns:
        bool: True if CORS is properly configured, False otherwise
    """
    if not validate_url(target):
        print(f"Error: '{target}' is not a valid URL. Include http:// or https://")
        return False

    if verbose:
        print(f"Checking CORS from {origin} to {target}")
        print(f"Method: {method}")
        if headers:
            print(f"Headers: {headers}")

    # First, perform an OPTIONS preflight request
    try:
        options_headers = {
            'Origin': origin,
            'Access-Control-Request-Method': method
        }

        if headers:
            options_headers['Access-Control-Request-Headers'] = ','.join(headers)

        if verbose:
            print("\nSending OPTIONS preflight request...")

        options_response = requests.options(target, headers=options_headers, timeout=10)

        if verbose:
            print(f"Status code: {options_response.status_code}")
            print("Response headers:")
            for key, value in options_response.headers.items():
                print(f"  {key}: {value}")

        # Check if CORS headers are present in the response
        cors_allowed = 'Access-Control-Allow-Origin' in options_response.headers

        # Check if the origin is allowed
        origin_allowed = False
        if cors_allowed:
            allowed_origin = options_response.headers.get('Access-Control-Allow-Origin')
            origin_allowed = allowed_origin == '*' or origin in allowed_origin

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
        if headers:
            for header in headers:
                # Check if header contains a name-value pair (name:value format)
                if ':' in header:
                    name, value = header.split(':', 1)
                    actual_headers[name.strip()] = value.strip()
                else:
                    # If no value is provided, use the header name as the value
                    actual_headers[header] = ''

        if verbose and headers:
            print(f"Including custom headers: {actual_headers}")

        actual_response = requests.request(method, target, headers=actual_headers, timeout=10)

        if verbose:
            print(f"Status code: {actual_response.status_code}")
            print("Response headers:")
            for key, value in actual_response.headers.items():
                print(f"  {key}: {value}")

        # Check if CORS headers are present in the actual response
        actual_cors_allowed = 'Access-Control-Allow-Origin' in actual_response.headers

        # Check if the origin is allowed in the actual response
        actual_origin_allowed = False
        if actual_cors_allowed:
            actual_allowed_origin = actual_response.headers.get('Access-Control-Allow-Origin')
            actual_origin_allowed = actual_allowed_origin == '*' or origin in actual_allowed_origin

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
        result = cors_allowed and origin_allowed and actual_cors_allowed and actual_origin_allowed

        if verbose:
            if result:
                print("\nResult: CORS is properly configured")
            else:
                print("\nResult: CORS is not properly configured")

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Check CORS configuration between domains')
    parser.add_argument('origin', help='The origin domain (where the request is coming from)')
    parser.add_argument('target', help='The target domain (where the request is going to)')
    parser.add_argument('-m', '--method', default='GET', help='HTTP method to use (default: GET)')
    parser.add_argument('-H', '--headers', nargs='+', help='Additional headers to include in the request')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed information')

    args = parser.parse_args()

    result = check_cors(args.origin, args.target, args.method, args.headers, args.verbose)

    if not args.verbose:
        if result:
            print("CORS is properly configured")
        else:
            print("CORS is not properly configured")

    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()
