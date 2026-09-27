from typing import List, Dict, Any
from pydantic import BaseModel


class TestModuleMetadata(BaseModel):
    id: str
    name_en: str
    name_ar: str
    category: str  # web_security, api_security, functional_reliability
    status: str    # "implemented", "prerequisites_missing", "not_implemented"
    required_target_info: List[str]
    authentication_required: bool
    supported_technologies: List[str]
    side_effects: str
    risk_level: str  # low, medium, high
    tool_dependencies: List[str]
    verification_method: str
    expected_evidence: str
    known_limitations: str


TEST_CATALOG: List[TestModuleMetadata] = [
    # 1. Headers & TLS Security
    TestModuleMetadata(
        id="mod-sec-headers",
        name_en="Security Headers & Cookie Flags",
        name_ar="ترويسات الأمان وخصائص ملفات تعريف الارتباط",
        category="web_security",
        status="implemented",
        required_target_info=["base_urls"],
        authentication_required=False,
        supported_technologies=["HTTP/1.1", "HTTP/2", "TLS"],
        side_effects="Read-only HTTP requests",
        risk_level="low",
        tool_dependencies=["controlled_http"],
        verification_method="Inspection of response headers (HSTS, CSP, X-Frame-Options) and cookie attributes (Secure, HttpOnly, SameSite).",
        expected_evidence="Raw HTTP request and response header snapshots with flagged missing security directives.",
        known_limitations="Does not verify dynamic DOM policy enforcement in older browsers."
    ),
    # 2. Path Traversal & Source Access
    TestModuleMetadata(
        id="mod-path-traversal",
        name_en="Source Code Path Traversal & Workspace Escape",
        name_ar="اجتياز المسارات والهروب من مساحة العمل",
        category="web_security",
        status="implemented",
        required_target_info=["source_path"],
        authentication_required=False,
        supported_technologies=["File Systems", "Node.js", "Python"],
        side_effects="Static file system analysis inside sandbox",
        risk_level="low",
        tool_dependencies=["source_inspector"],
        verification_method="Static analysis of file resolution paths and canonical boundaries.",
        expected_evidence="Identified file path resolution calls that omit canonicalization or bounds checking.",
        known_limitations="Does not simulate runtime symlink race conditions."
    ),
    # 3. Secret Leakage & Exposed Credentials
    TestModuleMetadata(
        id="mod-secret-scan",
        name_en="Repository Secret & Credential Scanning",
        name_ar="فحص أسرار المستودعات وبيانات الاعتماد المكشوفة",
        category="web_security",
        status="implemented",
        required_target_info=["source_path"],
        authentication_required=False,
        supported_technologies=["Git", "Source Repositories"],
        side_effects="Read-only repository file inspection",
        risk_level="low",
        tool_dependencies=["gitleaks", "source_inspector"],
        verification_method="Pattern matching and entropy analysis for API keys, private keys, and passwords.",
        expected_evidence="Redacted credential tokens with matched regex pattern and source file location.",
        known_limitations="High-entropy test mocks may yield potential false positives if not configured."
    ),
    # 4. AST Python Syntax & Static Analysis
    TestModuleMetadata(
        id="mod-ast-sast",
        name_en="Python AST Syntax & Dangerous Builtins Analysis",
        name_ar="التحليل الثابت لصيغة بايثون والدوال الخطيرة",
        category="web_security",
        status="implemented",
        required_target_info=["source_path"],
        authentication_required=False,
        supported_technologies=["Python 3.x"],
        side_effects="Read-only offline AST parsing",
        risk_level="low",
        tool_dependencies=["ast_parser"],
        verification_method="Offline AST traversal checking for eval(), exec(), and unsafe subprocess(shell=True).",
        expected_evidence="AST Node line number and code snippet demonstrating unsafe usage.",
        known_limitations="Limited to Python source code; does not trace cross-module taint."
    ),
    # 5. XSS (Cross-Site Scripting)
    TestModuleMetadata(
        id="mod-xss-reflection",
        name_en="Cross-Site Scripting (XSS) Reflection & Context Check",
        name_ar="فحص حقن البرمجيات الخبيثة عبر المواقع (XSS)",
        category="web_security",
        status="prerequisites_missing",
        required_target_info=["base_urls", "parameter_list"],
        authentication_required=False,
        supported_technologies=["HTML5", "DOM", "JavaScript"],
        side_effects="Injecting harmless diagnostic strings into input parameters",
        risk_level="medium",
        tool_dependencies=["playwright_browser", "controlled_http"],
        verification_method="Execution verification in headless browser DOM (not reflection alone).",
        expected_evidence="Browser DOM execution trace or event dispatch proof.",
        known_limitations="Requires headless browser worker setup; disabled on static targets."
    ),
    # 6. Broken Access Control & IDOR
    TestModuleMetadata(
        id="mod-idor-bola",
        name_en="Broken Object Level Authorization (BOLA/IDOR)",
        name_ar="كسر صلاحيات الوصول على مستوى الكائنات (IDOR/BOLA)",
        category="web_security",
        status="prerequisites_missing",
        required_target_info=["base_urls", "auth_accounts"],
        authentication_required=True,
        supported_technologies=["REST APIs", "GraphQL"],
        side_effects="Access attempts between two isolated test account objects",
        risk_level="medium",
        tool_dependencies=["controlled_http"],
        verification_method="Differential comparison of resource access between user A and user B tokens.",
        expected_evidence="HTTP 200 response with private resource data returned to unauthorized account.",
        known_limitations="Requires minimum two distinct test credentials configured in target."
    ),
    # 7. CSRF (Cross-Site Request Forgery)
    TestModuleMetadata(
        id="mod-csrf-state",
        name_en="Cross-Site Request Forgery State Change Validation",
        name_ar="التحقق من تزوير الطلبات عبر المواقع (CSRF)",
        category="web_security",
        status="prerequisites_missing",
        required_target_info=["base_urls", "mutating_endpoints", "auth_accounts"],
        authentication_required=True,
        supported_technologies=["Web Forms", "Session Cookies"],
        side_effects="Simulated cross-origin state mutation using test account",
        risk_level="high",
        tool_dependencies=["controlled_http", "playwright_browser"],
        verification_method="Execution of simulated cross-origin request and verification of persistent state change.",
        expected_evidence="Confirmed database or state alteration without valid anti-CSRF token.",
        known_limitations="Requires stateful endpoint and verified rollback mechanism."
    ),
    # 8. SSRF (Server-Side Request Forgery)
    TestModuleMetadata(
        id="mod-ssrf-validation",
        name_en="Server-Side Request Forgery (SSRF) Boundary Check",
        name_ar="فحص تزوير الطلبات من جانب الخادم (SSRF)",
        category="web_security",
        status="not_implemented",
        required_target_info=["base_urls", "webhook_endpoints"],
        authentication_required=False,
        supported_technologies=["HTTP Services", "Webhooks"],
        side_effects="Submitting controlled callback URLs",
        risk_level="high",
        tool_dependencies=["controlled_http", "dns_resolver"],
        verification_method="Triggering webhooks pointing to controlled listeners with DNS resolution verification.",
        expected_evidence="External DNS or HTTP callback received from server egress.",
        known_limitations="Not implemented in current release. Planned for v0.2."
    ),
    # 9. Functional Reliability: Form Validation & Empty States
    TestModuleMetadata(
        id="mod-func-form-validation",
        name_en="Form Validation & Boundary Value Handling",
        name_ar="التحقق من صحة النماذج والتعامل مع القيم الحدودية",
        category="functional_reliability",
        status="implemented",
        required_target_info=["base_urls", "form_selectors"],
        authentication_required=False,
        supported_technologies=["HTML Forms", "JSON APIs"],
        side_effects="Submitting boundary payloads (empty strings, large integers, unicode)",
        risk_level="low",
        tool_dependencies=["controlled_http"],
        verification_method="Evaluating HTTP status code and error messages for contract adherence vs 500 Unhandled Exceptions.",
        expected_evidence="HTTP 500 Internal Server Error stack trace or unhandled exception response.",
        known_limitations="Cannot infer business logic constraints without OpenAPI specification."
    )
]


def get_all_test_modules() -> List[TestModuleMetadata]:
    return TEST_CATALOG


def get_test_module_by_id(module_id: str) -> TestModuleMetadata | None:
    for mod in TEST_CATALOG:
        if mod.id == module_id:
            return mod
    return None
