import re

import pytest
from logassistant.domain.policy_engine import PolicyEngine
from logassistant.schemas import GlobalSecurityPolicy, NetworkLogEntry


@pytest.fixture
def get_policy_engine() -> PolicyEngine:
    content = {
        "rules": [
            {
                "name": "SQL Injection Detection",
                "pattern": "(UNION\\s+SELECT|AND\\s+1=1|select\\+from)",
                "target_field": "url",
                "on_success_score": 100,
                "on_reject_score": 100,
                "type": "signature",
            },
            {
                "name": "WordPress Brute Force",
                "pattern": "/wp-login.php",
                "target_field": "url",
                "on_success_score": 150,
                "on_reject_score": 50,
                "type": "volumetric",
                "volumetric_threshold": 5,
            },
        ]
    }
    policy_object = GlobalSecurityPolicy.model_validate(content)
    for rule in policy_object.rules:
        rule.compiled_regex = re.compile(rule.pattern, re.IGNORECASE)
    policy_engine = PolicyEngine(policy_object)
    policy_engine.treshold = 100
    return policy_engine


def test_policy_engine_no_rule_pass(get_policy_engine):
    log_entry = NetworkLogEntry.from_raw_line(
        '192.168.1.46 - - [06/Aug/2026:09:17:36 +0000] "GET /news/post-1 HTTP/1.1" 200 1428 "Mozilla/5.0 (X11; Linux x86_64)"'
    )
    assert get_policy_engine.evaluate_line(log_entry) is None


def test_policy_engine_signature_rule(get_policy_engine):
    log_entry = NetworkLogEntry.from_raw_line(
        '198.51.100.12 - - [06/Aug/2026:09:17:38 +0000] "GET /api/users?id=1+union+select+from+users HTTP/1.1" 200 1045 "Mozilla/5.0 (X11; Linux x86_64)"'
    )
    (rule_name, final_reason, final_score) = get_policy_engine.evaluate_line(log_entry)
    assert "Signature" in final_reason
    assert rule_name != ""
    assert final_score >= get_policy_engine.treshold


def test_policy_engine_volumetric_rule(get_policy_engine):
    log_entry = NetworkLogEntry.from_raw_line(
        '203.0.113.5 - - [06/Aug/2026:09:14:23 +0000] "POST /wp-login.php HTTP/1.1" 401 234 "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'
    )
    get_policy_engine.evaluate_line(log_entry)
    get_policy_engine.evaluate_line(log_entry)
    get_policy_engine.evaluate_line(log_entry)
    get_policy_engine.evaluate_line(log_entry)
    get_policy_engine.evaluate_line(log_entry)
    (rule_name, final_reason, final_score) = get_policy_engine.evaluate_line(log_entry)
    assert "Volumetric" in final_reason
    assert rule_name != ""
    assert final_score >= get_policy_engine.treshold
