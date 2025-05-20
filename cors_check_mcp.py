#!/usr/bin/env python3
"""
CORS Checker MCP Server - CORS 설정을 확인하는 MCP 서버 도구

이 MCP 서버는 지정된 출처(origin) 도메인에서 대상(target) 도메인으로의
크로스 오리진 요청이 허용되는지 확인할 수 있게 해줍니다.
"""

from mcp.server.fastmcp import FastMCP
import io
import sys
import json
from contextlib import redirect_stdout

# Import functions from cors_checker.py
from cors_checker import check_cors as original_check_cors, validate_url, parse_headers

# MCP 서버 생성
mcp = FastMCP("CORS Checker")

@mcp.tool()
def check_cors(origin: str, target: str, method: str = "GET", headers: str = None, verbose: bool = False, timeout: int = 10) -> str:
    """
    두 도메인 간의 CORS 설정을 확인합니다.

    Args:
        origin: 요청이 오는 출처 도메인
        target: 요청이 가는 대상 도메인
        method: preflight 요청에 사용할 HTTP 메서드
        headers: preflight 요청에 포함할 추가 헤더(쉼표로 구분). 헤더는 "이름:값" 형식으로 지정할 수 있습니다(예: "Content-Type:application/json").
        verbose: 상세 정보 반환 여부
        timeout: 요청 타임아웃 시간(초)

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
            result = original_check_cors(origin, target, method, header_list, verbose, timeout)

        captured_output = output_capture.getvalue()

        # 결과 처리
        if verbose:
            if captured_output:
                result_str = captured_output.strip()
                if not result['success']:
                    result_str += f"\n\n요약: {result['message']}"
                return result_str
            else:
                return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return result['message']

    except Exception as e:
        error_message = f"오류: {e}"
        if verbose:
            return f"{error_message}\nCORS 확인 실패."
        else:
            return error_message

@mcp.tool()
def check_cors_json(origin: str, target: str, method: str = "GET", headers: str = None, verbose: bool = False, timeout: int = 10) -> str:
    """
    두 도메인 간의 CORS 설정을 확인하고 결과를 JSON 형식으로 반환합니다.

    Args:
        origin: 요청이 오는 출처 도메인
        target: 요청이 가는 대상 도메인
        method: preflight 요청에 사용할 HTTP 메서드
        headers: preflight 요청에 포함할 추가 헤더(쉼표로 구분).
        verbose: 상세 정보 포함 여부
        timeout: 요청 타임아웃 시간(초)

    Returns:
        CORS 설정 결과를 JSON 형식의 문자열로 반환
    """
    # 헤더 문자열을 리스트로 변환
    header_list = None
    if headers:
        header_list = [h.strip() for h in headers.split(",")]

    # 원본 함수 호출
    try:
        result = original_check_cors(origin, target, method, header_list, verbose, timeout)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"오류: {e}",
            "details": {"exception": str(e.__class__.__name__)}
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)

@mcp.tool()
def validate_domain_url(url: str) -> bool:
    """
    URL이 유효한지 확인합니다.

    Args:
        url: 확인할 URL

    Returns:
        URL이 유효하면 True, 그렇지 않으면 False
    """
    return validate_url(url)

@mcp.resource("cors-help://usage")
def get_cors_help() -> str:
    """CORS 확인 도구에 대한 사용법 정보 제공"""
    return """
    CORS Checker - 도메인 간 CORS 설정을 확인하는 도구

    사용법:
        check_cors(origin, target, method="GET", headers=None, verbose=False, timeout=10)

    매개변수:
        origin: 요청이 오는 출처 도메인
        target: 요청이 가는 대상 도메인
        method: preflight 요청에 사용할 HTTP 메서드
        headers: preflight 요청에 포함할 추가 헤더(쉼표로 구분). 헤더는 "이름:값" 형식으로 지정할 수 있습니다(예: "Content-Type:application/json").
        verbose: 상세 정보 반환 여부
        timeout: 요청 타임아웃 시간(초, 기본값: 10)

    JSON 형식 결과를 원하는 경우:
        check_cors_json(origin, target, method="GET", headers=None, verbose=False, timeout=10)
        
    URL 유효성 검사:
        validate_domain_url(url)

    예시:
        check_cors("https://example.com", "https://api.example.org")
        check_cors("https://localhost:3000", "https://api.example.org", method="POST", headers="Content-Type:application/json,Authorization:Bearer token123", verbose=True)
        check_cors_json("https://example.com", "https://api.example.org")
    """

@mcp.prompt()
def cors_check_prompt() -> str:
    """CORS 설정 확인을 위한 프롬프트 반환"""
    return """
    두 도메인 간의 CORS 설정을 확인하고 싶습니다.

    출처 도메인(요청이 오는 곳): {origin}
    대상 도메인(요청이 가는 곳): {target}

    check_cors 도구를 사용하여 CORS가 올바르게 구성되어 있는지 확인해주세요.
    자세한 정보가 필요하다면 verbose 파라미터를 True로 설정하세요.
    JSON 형식의 결과를 원한다면 check_cors_json 도구를 사용하세요.
    """

@mcp.prompt()
def cors_check_common_issues() -> str:
    """CORS 관련 일반적인 문제 해결을 위한 프롬프트 반환"""
    return """
    CORS 설정 문제가 발생했습니다. 가장 일반적인 CORS 문제와 그 해결 방법에 대해 알려주세요.
    
    내 환경:
    - 프론트엔드: {frontend}
    - 백엔드: {backend}
    - 문제 증상: {issue}
    
    check_cors 도구를 사용하여 구체적인 CORS 설정을 확인한 후, 
    이 환경에서 CORS 문제를 해결하기 위한 구체적인 조언을 제공해주세요.
    """

if __name__ == "__main__":
    mcp.run()
