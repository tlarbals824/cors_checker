#!/usr/bin/env python3
"""
CORS Checker MCP Server - CORS 설정을 확인하는 MCP 서버 도구

이 MCP 서버는 지정된 출처(origin) 도메인에서 대상(target) 도메인으로의
크로스 오리진 요청이 허용되는지 확인할 수 있게 해줍니다.
"""

from mcp.server.fastmcp import FastMCP
import io
import sys
from contextlib import redirect_stdout

# Import functions from cors_checker.py
from cors_checker import check_cors as original_check_cors, validate_url

# MCP 서버 생성
mcp = FastMCP("CORS Checker")

@mcp.tool()
def check_cors(origin: str, target: str, method: str = "GET", headers: str = None, verbose: bool = False) -> str:
    """
    두 도메인 간의 CORS 설정을 확인합니다.

    Args:
        origin: 요청이 오는 출처 도메인
        target: 요청이 가는 대상 도메인
        method: preflight 요청에 사용할 HTTP 메서드
        headers: preflight 요청에 포함할 추가 헤더(쉼표로 구분). 헤더는 "이름:값" 형식으로 지정할 수 있습니다(예: "Content-Type:application/json").
        verbose: 상세 정보 반환 여부

    Returns:
        CORS 설정 결과를 설명하는 문자열
    """
    # 헤더 문자열을 리스트로 변환
    header_list = None
    if headers:
        header_list = [h.strip() for h in headers.split(",")]

    # 원본 함수의 출력을 캡처하기 위한 설정
    output_capture = io.StringIO()

    try:
        # 원본 함수 호출 및 출력 캡처
        with redirect_stdout(output_capture):
            result = original_check_cors(origin, target, method, header_list, verbose)

        captured_output = output_capture.getvalue()

        # 결과에 따라 적절한 메시지 반환
        if result:
            summary = "CORS가 올바르게 구성되어 있습니다"
        else:
            summary = "CORS가 올바르게 구성되어 있지 않습니다"

        # 상세 정보 요청 시 캡처된 출력 반환
        if verbose:
            if captured_output:
                return captured_output.strip()
            else:
                return summary
        else:
            return summary

    except Exception as e:
        error_message = f"오류: {e}"
        if verbose:
            return f"{error_message}\nCORS 확인 실패."
        else:
            return error_message

@mcp.resource("cors-help://usage")
def get_cors_help() -> str:
    """CORS 확인 도구에 대한 사용법 정보 제공"""
    return """
    CORS Checker - 도메인 간 CORS 설정을 확인하는 도구

    사용법:
        check_cors(origin, target, method="GET", headers=None, verbose=False)

    매개변수:
        origin: 요청이 오는 출처 도메인
        target: 요청이 가는 대상 도메인
        method: preflight 요청에 사용할 HTTP 메서드
        headers: preflight 요청에 포함할 추가 헤더(쉼표로 구분). 헤더는 "이름:값" 형식으로 지정할 수 있습니다(예: "Content-Type:application/json").
        verbose: 상세 정보 반환 여부

    예시:
        check_cors("https://example.com", "https://api.example.org")
        check_cors("https://localhost:3000", "https://api.example.org", method="POST", headers="Content-Type:application/json,Authorization:Bearer token123", verbose=True)
    """

@mcp.prompt()
def cors_check_prompt() -> str:
    """CORS 설정 확인을 위한 프롬프트 반환"""
    return """
    두 도메인 간의 CORS 설정을 확인하고 싶습니다.

    출처 도메인(요청이 오는 곳): {origin}
    대상 도메인(요청이 가는 곳): {target}

    check_cors 도구를 사용하여 CORS가 올바르게 구성되어 있는지 확인해주세요.
    """

if __name__ == "__main__":
    mcp.run()
