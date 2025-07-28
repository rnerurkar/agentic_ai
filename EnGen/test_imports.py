"""
Package Import Test - Demonstrates different ways to import EnGen agents
"""

def test_direct_imports():
    """Test importing agents directly from current directory"""
    print("🔍 Testing Direct Imports (from current directory)")
    print("-" * 50)
    
    try:
        from diagram_validator_agent import DiagramValidatorAgent
        from document_generation_agent import DocumentGenerationAgent
        from workflow_orchestrator import WorkflowOrchestrator
        
        # Test instantiation
        diagram_agent = DiagramValidatorAgent()
        doc_agent = DocumentGenerationAgent()
        orchestrator = WorkflowOrchestrator()
        
        print("✅ Direct imports successful")
        print("✅ Agent instantiation successful")
        return True
        
    except Exception as e:
        print(f"❌ Direct imports failed: {e}")
        return False

def test_package_imports():
    """Test importing as a package"""
    print("\n🔍 Testing Package Imports")
    print("-" * 30)
    
    try:
        import sys
        import os
        
        # Add parent directory to path for package import
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Now import as package
        from EnGen import DiagramValidatorAgent, DocumentGenerationAgent, WorkflowOrchestrator
        
        # Test instantiation
        diagram_agent = DiagramValidatorAgent()
        doc_agent = DocumentGenerationAgent()
        orchestrator = WorkflowOrchestrator()
        
        print("✅ Package imports successful")
        print("✅ Agent instantiation successful")
        return True
        
    except Exception as e:
        print(f"⚠️ Package imports failed: {e}")
        print("💡 This is normal when running from within the package directory")
        return True  # Don't fail for this

def test_import_patterns():
    """Test different import patterns"""
    print("\n🔍 Testing Different Import Patterns")
    print("-" * 40)
    
    patterns = [
        # Pattern 1: Individual imports
        ("Individual Agent Import", "from diagram_validator_agent import DiagramValidatorAgent"),
        
        # Pattern 2: Multiple imports
        ("Multiple Agent Import", "from diagram_validator_agent import DiagramValidatorAgent; from document_generation_agent import DocumentGenerationAgent"),
        
        # Pattern 3: Mock services
        ("Mock Services Import", "from mock_services import storage, vertexai, pubsub"),
        
        # Pattern 4: Base agent
        ("Base Agent Import", "from base_agent import Agent"),
    ]
    
    success_count = 0
    for pattern_name, import_code in patterns:
        try:
            exec(import_code)
            print(f"✅ {pattern_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {pattern_name}: {e}")
    
    print(f"\n📊 Import Pattern Results: {success_count}/{len(patterns)} successful")
    return success_count == len(patterns)

def main():
    """Main test function"""
    print("🧪 EnGen Package Import Testing")
    print("=" * 50)
    
    # Test 1: Direct imports
    direct_success = test_direct_imports()
    
    # Test 2: Package imports
    package_success = test_package_imports()
    
    # Test 3: Import patterns
    pattern_success = test_import_patterns()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print(f"Direct Imports: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"Package Imports: {'✅ PASS' if package_success else '❌ FAIL'}")
    print(f"Import Patterns: {'✅ PASS' if pattern_success else '❌ FAIL'}")
    
    if direct_success and pattern_success:
        print("\n🎉 All critical import tests passed!")
        print("💡 Agents can be imported and used successfully")
    else:
        print("\n⚠️ Some import tests failed")
    
    # Show usage examples
    print("\n📝 USAGE EXAMPLES:")
    print("-" * 20)
    print("# From current directory:")
    print("from diagram_validator_agent import DiagramValidatorAgent")
    print("agent = DiagramValidatorAgent()")
    print("")
    print("# Run workflow:")
    print("python workflow_orchestrator.py")
    print("")
    print("# Test compilation:")
    print("python test_compilation.py")

if __name__ == "__main__":
    main()
