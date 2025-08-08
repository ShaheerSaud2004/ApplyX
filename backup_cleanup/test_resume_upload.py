#!/usr/bin/env python3
"""
Test Resume Upload Functionality
Tests the complete resume upload flow including backend API and file handling.
"""

import requests
import json
import os
import io

def test_resume_upload():
    """Test the complete resume upload flow"""
    print("🧪 Testing Resume Upload Functionality...")
    
    # Test credentials
    email = "shaheersaud2004@gmail.com"
    password = "TestPassword123!"
    
    # Base URL
    base_url = "http://localhost:5001"
    
    try:
        # 1. Login
        print("📝 Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # 2. Create a test PDF file
        print("📄 Creating test resume file...")
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000203 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
295
%%EOF"""
        
        # 3. Test resume upload
        print("📤 Testing resume upload...")
        files = {
            'file': ('test_resume.pdf', io.BytesIO(test_pdf_content), 'application/pdf')
        }
        
        upload_response = requests.post(
            f"{base_url}/api/upload/resume",
            headers=headers,
            files=files
        )
        
        if upload_response.status_code == 200:
            print("✅ Resume upload successful!")
            upload_data = upload_response.json()
            print(f"   📋 Response: {json.dumps(upload_data, indent=2)}")
            resume_id = upload_data.get('resumeId')
            
            # 4. Test getting user resumes
            print("📋 Testing resume list retrieval...")
            resumes_response = requests.get(
                f"{base_url}/api/resumes",
                headers=headers
            )
            
            if resumes_response.status_code == 200:
                print("✅ Resume list retrieved successfully!")
                resumes_data = resumes_response.json()
                print(f"   📋 Resumes: {json.dumps(resumes_data, indent=2)}")
            else:
                print(f"❌ Failed to get resumes: {resumes_response.text}")
            
            # 5. Test resume download (if we have a resume ID)
            if resume_id:
                print("📥 Testing resume download...")
                download_response = requests.get(
                    f"{base_url}/api/resumes/{resume_id}/download",
                    headers=headers
                )
                
                if download_response.status_code == 200:
                    print("✅ Resume download successful!")
                    print(f"   📋 Content length: {len(download_response.content)} bytes")
                else:
                    print(f"❌ Failed to download resume: {download_response.text}")
            
            # 6. Test file validation (invalid file type)
            print("🚫 Testing file validation with invalid file...")
            invalid_files = {
                'file': ('test.txt', io.BytesIO(b"This is not a valid resume file"), 'text/plain')
            }
            
            invalid_response = requests.post(
                f"{base_url}/api/upload/resume",
                headers=headers,
                files=invalid_files
            )
            
            if invalid_response.status_code == 400:
                print("✅ File validation working correctly!")
                print(f"   📋 Error message: {invalid_response.json().get('error')}")
            else:
                print(f"❌ File validation failed: {invalid_response.text}")
            
            print("\n🎉 All resume upload tests completed!")
            return True
            
        else:
            print(f"❌ Resume upload failed: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_resume_upload() 