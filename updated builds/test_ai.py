#!/usr/bin/env python3
"""
AI Model Tester - Lists all available models for your API keys
"""

import json
import os

# Test Gemini Models
def test_gemini_models(api_key):
    """List all Gemini models available with your API key"""
    try:
        import google.generativeai as genai
        
        print("\n" + "="*70)
        print("GEMINI MODELS - LISTING ALL AVAILABLE MODELS")
        print("="*70)
        
        genai.configure(api_key=api_key)
        
        # List all available models
        print("\nAvailable Models:")
        print("-" * 70)
        
        models = genai.list_models()
        gemini_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                # Extract simple name
                simple_name = model.name.replace('models/', '')
                gemini_models.append(simple_name)
                
                print(f"\n✓ Model: {simple_name}")
                print(f"  Full Name: {model.name}")
                print(f"  Display: {model.display_name}")
                print(f"  Description: {model.description}")
        
        # Test each model
        print("\n" + "="*70)
        print("TESTING EACH MODEL")
        print("="*70)
        
        test_prompt = "Say 'Hello' in one word"
        working_models = []
        
        for simple_name in gemini_models:
            try:
                print(f"\nTesting: {simple_name}...", end=" ")
                model = genai.GenerativeModel(simple_name)
                response = model.generate_content(test_prompt)
                print(f"✓ WORKS - Response: {response.text.strip()}")
                working_models.append(simple_name)
            except Exception as e:
                print(f"✗ FAILED - {str(e)[:50]}")
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nTotal models found: {len(gemini_models)}")
        print(f"Working models: {len(working_models)}")
        print("\nWorking models you can use:")
        for model in working_models:
            print(f"  - {model}")
        
        return working_models
        
    except ImportError:
        print("\n✗ Error: google-generativeai library not installed")
        print("Install: pip install google-generativeai")
        return []
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return []


# Test OpenAI Models
def test_openai_models(api_key):
    """List all OpenAI models available with your API key"""
    try:
        import openai
        
        print("\n" + "="*70)
        print("OPENAI MODELS - LISTING ALL AVAILABLE MODELS")
        print("="*70)
        
        client = openai.OpenAI(api_key=api_key)
        
        # List all models
        print("\nAll available models:")
        print("-" * 70)
        
        models = client.models.list()
        all_models = [model.id for model in models.data]
        
        # Filter GPT models
        gpt_models = [m for m in all_models if 'gpt' in m.lower()]
        
        print("\nGPT models found:")
        for model in sorted(gpt_models):
            print(f"  - {model}")
        
        # Test common chat models
        print("\n" + "="*70)
        print("TESTING COMMON CHAT MODELS")
        print("="*70)
        
        common_models = [
            'gpt-3.5-turbo',
            'gpt-4',
            'gpt-4-turbo',
            'gpt-4o',
            'gpt-4o-mini'
        ]
        
        test_prompt = "Say 'Hello' in one word"
        working_models = []
        
        for model_name in common_models:
            try:
                print(f"\nTesting: {model_name}...", end=" ")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip()
                print(f"✓ WORKS - Response: {result}")
                working_models.append(model_name)
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg:
                    print(f"✗ NOT AVAILABLE")
                else:
                    print(f"✗ FAILED - {error_msg[:50]}")
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nTotal models found: {len(all_models)}")
        print(f"GPT models: {len(gpt_models)}")
        print(f"Working chat models: {len(working_models)}")
        print("\nWorking models you can use:")
        for model in working_models:
            print(f"  - {model}")
        
        return working_models
        
    except ImportError:
        print("\n✗ Error: openai library not installed")
        print("Install: pip install openai")
        return []
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return []


def main():
    """Main function"""
    print("\n" + "="*70)
    print("AI MODEL AVAILABILITY TESTER")
    print("Lists all models available with your API keys")
    print("="*70)
    
    # Load config
    config_file = "upmenuconfig.json"
    gemini_key = None
    openai_key = None
    
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                ai_config = config.get("ai_integration", {})
                
                # Find keys
                if ai_config.get("ai_provider_1") == "Gemini":
                    gemini_key = ai_config.get("ai_api_key_1")
                elif ai_config.get("ai_provider_2") == "Gemini":
                    gemini_key = ai_config.get("ai_api_key_2")
                
                if ai_config.get("ai_provider_1") == "OpenAI":
                    openai_key = ai_config.get("ai_api_key_1")
                elif ai_config.get("ai_provider_2") == "OpenAI":
                    openai_key = ai_config.get("ai_api_key_2")
                
                print(f"\n✓ Loaded API keys from {config_file}")
        except:
            pass
    
    # Ask for keys if not found
    if not gemini_key:
        gemini_key = input("\nEnter Gemini API key (or press Enter to skip): ").strip()
    
    if not openai_key:
        openai_key = input("Enter OpenAI API key (or press Enter to skip): ").strip()
    
    # Test
    if gemini_key:
        test_gemini_models(gemini_key)
    else:
        print("\n⚠ Skipping Gemini (no API key)")
    
    if openai_key:
        test_openai_models(openai_key)
    else:
        print("\n⚠ Skipping OpenAI (no API key)")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
    print("\nUse the working model names in your menu.py configuration.")


if __name__ == "__main__":
    main()