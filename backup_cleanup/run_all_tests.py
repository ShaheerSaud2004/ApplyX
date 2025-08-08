#!/usr/bin/env python3
"""
Master Test Runner for ApplyX
Runs all test suites and generates comprehensive reports
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

def run_test_suite(test_file: str, description: str):
    """Run a test suite and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {description}")
    print(f"{'='*60}")
    
    try:
        # Run the test file
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        success = result.returncode == 0
        output = result.stdout
        error = result.stderr
        
        print(output)
        if error:
            print(f"Errors: {error}")
            
        return {
            "test_suite": description,
            "success": success,
            "output": output,
            "error": error,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 5 minutes")
        return {
            "test_suite": description,
            "success": False,
            "output": "",
            "error": "Test timed out",
            "return_code": -1
        }
    except Exception as e:
        print(f"❌ Error running {description}: {str(e)}")
        return {
            "test_suite": description,
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1
        }

def check_services():
    """Check if required services are running"""
    print("🔍 Checking required services...")
    
    services = [
        ("Backend", "http://localhost:8000"),
        ("Frontend", "http://localhost:3000")
    ]
    
    import requests
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ Running" if response.status_code == 200 else "⚠️  Responding but not 200"
            print(f"  {service_name}: {status} ({response.status_code})")
        except Exception as e:
            print(f"  {service_name}: ❌ Not running ({str(e)})")

def main():
    """Main function to run all tests"""
    print("🚀 ApplyX Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check services
    check_services()
    
    # Define test suites
    test_suites = [
        ("tests/comprehensive_functionality_test.py", "Comprehensive Functionality Tests"),
        ("tests/frontend_component_test.py", "Frontend Component Tests"),
        ("tests/button_interaction_test.py", "Button and Interaction Tests")
    ]
    
    # Run all test suites
    results = []
    start_time = time.time()
    
    for test_file, description in test_suites:
        if os.path.exists(test_file):
            result = run_test_suite(test_file, description)
            results.append(result)
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append({
                "test_suite": description,
                "success": False,
                "output": "",
                "error": "Test file not found",
                "return_code": -1
            })
    
    # Calculate summary
    total_time = time.time() - start_time
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result['success'])
    failed_tests = total_tests - passed_tests
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 MASTER TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Suites: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    
    if failed_tests > 0:
        print(f"\n🔍 FAILED TEST SUITES:")
        for result in results:
            if not result['success']:
                print(f"  - {result['test_suite']}: {result['error']}")
    
    # Save comprehensive results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"master_test_results_{timestamp}.json"
    
    master_results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "total_time": total_time,
        "results": results
    }
    
    with open(filename, 'w') as f:
        json.dump(master_results, f, indent=2)
    
    print(f"\n💾 Master results saved to: {filename}")
    
    # Generate HTML report
    generate_html_report(master_results, timestamp)
    
    # Exit with appropriate code
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test suite(s) failed!")
        sys.exit(1)
    else:
        print(f"\n🎉 All test suites passed!")
        sys.exit(0)

def generate_html_report(results, timestamp):
    """Generate an HTML report"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ApplyX Test Results - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .test-result {{ margin-bottom: 20px; padding: 15px; border-radius: 8px; border-left: 4px solid; }}
        .test-result.passed {{ background: #d4edda; border-color: #28a745; }}
        .test-result.failed {{ background: #f8d7da; border-color: #dc3545; }}
        .output {{ background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }}
        .error {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ApplyX Test Results</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <p style="font-size: 2em; font-weight: bold;">{results['total_tests']}</p>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <p style="font-size: 2em; font-weight: bold; color: #28a745;">{results['passed_tests']}</p>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <p style="font-size: 2em; font-weight: bold; color: #dc3545;">{results['failed_tests']}</p>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <p style="font-size: 2em; font-weight: bold; color: {'#28a745' if results['success_rate'] >= 80 else '#ffc107' if results['success_rate'] >= 60 else '#dc3545'};">{results['success_rate']:.1f}%</p>
            </div>
        </div>
        
        <h2>Test Results</h2>
"""
    
    for result in results['results']:
        status_class = "passed" if result['success'] else "failed"
        status_icon = "✅" if result['success'] else "❌"
        
        html_content += f"""
        <div class="test-result {status_class}">
            <h3>{status_icon} {result['test_suite']}</h3>
            <p><strong>Status:</strong> {'Passed' if result['success'] else 'Failed'}</p>
            <p><strong>Return Code:</strong> {result['return_code']}</p>
"""
        
        if result['error']:
            html_content += f"""
            <div class="error">
                <strong>Error:</strong> {result['error']}
            </div>
"""
        
        if result['output']:
            html_content += f"""
            <details>
                <summary>View Output</summary>
                <div class="output">{result['output']}</div>
            </details>
"""
        
        html_content += """
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    
    html_filename = f"test_report_{timestamp}.html"
    with open(html_filename, 'w') as f:
        f.write(html_content)
    
    print(f"📄 HTML report generated: {html_filename}")

if __name__ == "__main__":
    main() 