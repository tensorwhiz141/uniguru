#!/usr/bin/env python3
"""
Quick setup script for Uniguru-LM Composer
Validates installation and runs basic tests
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required modules are available"""
    required_modules = [
        'typing', 'logging', 'json', 'time', 're', 'string', 
        'collections', 'functools', 'enum', 'os', 'pickle'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing modules: {missing}")
        return False
    
    print("✅ All required modules available")
    return True

def check_composer_files():
    """Check if all composer files exist"""
    required_files = [
        'composer/__init__.py',
        'composer/compose.py',
        'composer/templates.py',
        'composer/ngram_scorer.py',
        'composer/gru.py',
        'composer/grounding.py',
        'composer/composer_api.py',
        'tests/test_compose.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print("✅ All composer files present")
    return True

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    try:
        result = subprocess.run(
            [sys.executable, 'tests/test_compose.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ All unit tests passed")
            return True
        else:
            print(f"❌ Unit tests failed:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def test_api_functionality():
    """Test basic API functionality"""
    print("\n🔧 Testing API functionality...")
    try:
        # Import composer
        sys.path.append('.')
        from composer.compose import compose
        
        # Test data
        test_chunks = [
            {
                'text': 'Test text for grounding verification.',
                'source': 'Test Source',
                'score': 0.9
            }
        ]
        
        # Run composition
        result = compose(
            trace_id='setup_test_001',
            extractive_answer='Test answer for verification.',
            top_chunks=test_chunks,
            lang='EN'
        )
        
        # Validate result
        required_fields = ['trace_id', 'final_text', 'grounded', 'template_id']
        for field in required_fields:
            if field not in result:
                print(f"❌ Missing field in result: {field}")
                return False
        
        print("✅ API functionality working")
        print(f"   - Template: {result['template_id']}")
        print(f"   - Grounded: {result['grounded']}")
        print(f"   - Time: {result['composition_time_ms']}ms")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'composer/models',
        'composer/data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created")

def main():
    """Main setup function"""
    print("🚀 Uniguru-LM Composer Setup")
    print("=" * 40)
    
    # Change to server directory if not already there
    if os.path.basename(os.getcwd()) != 'server':
        if os.path.exists('server'):
            os.chdir('server')
            print("📁 Changed to server directory")
        else:
            print("❌ Please run from project root or server directory")
            return False
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Composer Files", check_composer_files),
        ("Create Directories", create_directories),
        ("Unit Tests", run_unit_tests),
        ("API Functionality", test_api_functionality)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}...")
        try:
            if callable(check_func):
                success = check_func()
            else:
                check_func()
                success = True
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SETUP SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Install Python dependencies: pip install -r composer/requirements.txt")
        print("   2. Start Node.js server: npm run dev")
        print("   3. Test endpoints: curl http://localhost:8000/api/composer/test")
        return True
    else:
        print("\n⚠️  Setup incomplete. Please resolve the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)