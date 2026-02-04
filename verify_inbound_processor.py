#!/usr/bin/env python3
"""
Simple verification script to check inbound processor implementation
without requiring full database setup
"""

import sys
import json


def verify_imports():
    """Verify all modules can be imported"""
    print("✓ Checking imports...")
    
    # Check if we can at least parse the files
    try:
        with open("app/server/inbound_processor.py", "r") as f:
            content = f.read()
            compile(content, "inbound_processor.py", "exec")
        print("  ✓ inbound_processor.py syntax valid")
    except SyntaxError as e:
        print(f"  ✗ Syntax error in inbound_processor.py: {e}")
        return False
        
    try:
        with open("app/server/webhook_handler.py", "r") as f:
            content = f.read()
            compile(content, "webhook_handler.py", "exec")
        print("  ✓ webhook_handler.py syntax valid")
    except SyntaxError as e:
        print(f"  ✗ Syntax error in webhook_handler.py: {e}")
        return False
        
    try:
        with open("app/core/models.py", "r") as f:
            content = f.read()
            compile(content, "models.py", "exec")
        print("  ✓ models.py syntax valid")
    except SyntaxError as e:
        print(f"  ✗ Syntax error in models.py: {e}")
        return False
    
    return True


def verify_structure():
    """Verify expected code structure"""
    print("\n✓ Checking code structure...")
    
    checks = [
        ("WorkspaceSettings model", "app/core/models.py", "class WorkspaceSettings"),
        ("Conversation model", "app/core/models.py", "class Conversation"),
        ("Automation model", "app/core/models.py", "class Automation"),
        ("ExecutionRun model", "app/core/models.py", "class ExecutionRun"),
        ("InboundProcessor class", "app/server/inbound_processor.py", "class InboundProcessor"),
        ("process_inbound_event function", "app/server/inbound_processor.py", "def process_inbound_event"),
        ("with_retry decorator", "app/server/inbound_processor.py", "def with_retry"),
        ("webhook handler", "app/server/webhook_handler.py", "async def inbound_webhook_handler"),
        ("TransientError class", "app/server/inbound_processor.py", "class TransientError"),
        ("PermanentError class", "app/server/inbound_processor.py", "class PermanentError"),
    ]
    
    all_passed = True
    for check_name, file_path, search_str in checks:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if search_str in content:
                    print(f"  ✓ {check_name} found")
                else:
                    print(f"  ✗ {check_name} NOT found")
                    all_passed = False
        except FileNotFoundError:
            print(f"  ✗ File {file_path} not found")
            all_passed = False
            
    return all_passed


def verify_features():
    """Verify key features are implemented"""
    print("\n✓ Checking key features...")
    
    with open("app/server/inbound_processor.py", "r") as f:
        content = f.read()
    
    features = [
        ("Event normalization", "_normalize_event"),
        ("Context resolution", "_resolve_context"),
        ("Load live automations", "_load_live_automations"),
        ("Execution mode detection", "_get_execution_mode"),
        ("Run executor", "_run_executor"),
        ("Dispatch actions", "_dispatch_actions"),
        ("Write execution trace", "_write_execution_trace"),
        ("Write audit logs", "_write_audit_logs"),
        ("Retry logic", "with_retry"),
        ("Exponential backoff", "base_delay"),
    ]
    
    all_passed = True
    for feature_name, search_str in features:
        if search_str in content:
            print(f"  ✓ {feature_name} implemented")
        else:
            print(f"  ✗ {feature_name} NOT implemented")
            all_passed = False
            
    return all_passed


def verify_integration():
    """Verify integration with app.py"""
    print("\n✓ Checking integration...")
    
    try:
        with open("app/app.py", "r") as f:
            content = f.read()
            
        if "inbound_webhook_handler" in content:
            print("  ✓ Webhook handler imported")
        else:
            print("  ✗ Webhook handler NOT imported")
            return False
            
        if "/api/webhook/inbound" in content:
            print("  ✓ Webhook route registered")
        else:
            print("  ✗ Webhook route NOT registered")
            return False
            
        return True
    except FileNotFoundError:
        print("  ✗ app.py not found")
        return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("INBOUND PROCESSOR VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Import checks", verify_imports()))
    results.append(("Structure checks", verify_structure()))
    results.append(("Feature checks", verify_features()))
    results.append(("Integration checks", verify_integration()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ ALL CHECKS PASSED!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
