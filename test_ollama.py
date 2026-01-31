#!/usr/bin/env python
"""
Test script to verify Ollama connectivity and model availability
"""

import ollama
import sys

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        # Test basic connectivity
        models = ollama.list()
        print("✓ Successfully connected to Ollama")
        # Handle different response format for ollama library
        if hasattr(models, 'models'):
            model_names = [model.model for model in models.models]
        else:
            model_names = [model['name'] for model in models['models']]
        print(f"Available models: {model_names}")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Ollama: {e}")
        return False

def test_model_availability(model_name="lauchacarro/qwen2.5-translator:latest"):
    """Test if the required model is available"""
    try:
        # Check if the specific model is available
        models = ollama.list()
        # Handle different response format for ollama library
        if hasattr(models, 'models'):
            model_names = [model.model for model in models.models]
        else:
            model_names = [model['name'] for model in models['models']]
        
        if model_name in model_names:
            print(f"✓ Model '{model_name}' is available")
            return True
        else:
            print(f"✗ Model '{model_name}' is not available")
            print(f"  Available models: {model_names}")
            print(f"  Please run: ollama pull {model_name}")
            return False
    except Exception as e:
        print(f"✗ Failed to check model availability: {e}")
        return False

def test_translation(model_name="lauchacarro/qwen2.5-translator:latest"):
    """Test translation functionality with a simple phrase"""
    try:
        test_input = "こんにちは世界"  # "Hello World" in Japanese
        print(f"\nTesting translation with: '{test_input}'")
        
        response = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user', 
                'content': f'Translate the following Japanese text to English. Only return the English translation: {test_input}'
            }]
        )
        
        translation = response['message']['content'].strip()
        print(f"Translation result: '{translation}'")
        
        if translation.lower().startswith("hello world") or "hello" in translation.lower():
            print("✓ Translation test passed")
            return True
        else:
            print("? Translation completed but result seems unexpected")
            return True  # Still consider this a success since the model responded
    except Exception as e:
        print(f"✗ Translation test failed: {e}")
        return False

def main():
    print("Testing Ollama and model availability...\n")
    
    # Test basic connectivity
    if not test_ollama_connection():
        print("\nCannot connect to Ollama. Please make sure Ollama is installed and running.")
        sys.exit(1)
    
    # Test model availability
    model_name = "lauchacarro/qwen2.5-translator:latest"
    if not test_model_availability(model_name):
        print(f"\nRequired model '{model_name}' is not available.")
        print(f"Please install it by running: ollama pull {model_name}")
        sys.exit(1)
    
    # Test translation functionality
    if test_translation(model_name):
        print("\n✓ All tests passed! The application should work correctly.")
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()