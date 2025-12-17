#!/usr/bin/env python3
"""
Test AI settings functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests

def chat_with_ai_test(message, provider="OpenAI", api_key="test_key"):
    """Test AI chat function"""
    try:
        if provider == "OpenAI":
            # This will fail with test key but shows the structure works
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 100
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - API key invalid or other issue"
        else:
            return "Provider not implemented in test"
    except Exception as e:
        return f"Connection error: {str(e)}"

def test_ai_settings():
    root = tk.Tk()
    root.title("AI Settings Test")
    root.geometry("400x300")
    root.configure(bg="#333333")
    
    # Header
    tk.Label(root, text="AI Configuration Test", font=("Arial", 14, "bold"), 
             bg="#333333", fg="white").pack(pady=15)

    # Provider Selection
    provider_frame = tk.Frame(root, bg="#333333")
    provider_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(provider_frame, text="Provider:", bg="#333333", fg="#d2d2d2", 
             font=("Arial", 11), width=12, anchor="w").pack(side=tk.LEFT)
    
    provider_var = tk.StringVar(value="OpenAI")
    provider_combo = ttk.Combobox(provider_frame, textvariable=provider_var, 
                                 state="readonly", font=("Arial", 10))
    provider_combo['values'] = ('OpenAI', 'Gemini')
    provider_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    # API Key Entry
    key_frame = tk.Frame(root, bg="#333333")
    key_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(key_frame, text="API Key:", bg="#333333", fg="#d2d2d2", 
             font=("Arial", 11), width=12, anchor="w").pack(side=tk.LEFT)
    
    key_var = tk.StringVar(value="")
    key_entry = tk.Entry(key_frame, textvariable=key_var, bg="#222222", fg="white", 
                        insertbackground="white", font=("Arial", 10))
    key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    # Test connection button
    test_frame = tk.Frame(root, bg="#333333")
    test_frame.pack(fill=tk.X, padx=20, pady=10)
    
    def test_connection():
        temp_provider = provider_var.get()
        temp_key = key_var.get()
        
        if not temp_key:
            messagebox.showwarning("Warning", "Please enter an API key first.")
            return
        
        test_btn.config(text="Testing...", state=tk.DISABLED)
        
        def run_test():
            try:
                response = chat_with_ai_test("Hello, this is a test message.", temp_provider, temp_key)
                if response and not response.startswith("Error:"):
                    # Fixed the typo here - using root instead of settindow
                    root.after(0, lambda: show_test_result(True, "Connection successful!"))
                else:
                    root.after(0, lambda: show_test_result(False, response))
            except Exception as e:
                root.after(0, lambda: show_test_result(False, str(e)))
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def show_test_result(success, message):
        test_btn.config(text="Test Connection", state=tk.NORMAL)
        if success:
            messagebox.showinfo("Test Result", message)
        else:
            messagebox.showerror("Test Failed", f"Connection failed: {message}")
    
    test_btn = tk.Button(test_frame, text="Test Connection", command=test_connection,
                        bg="#666666", fg="white", font=("Arial", 10))
    test_btn.pack()

    # Close button
    tk.Button(root, text="Close", command=root.destroy, 
              bg="#f44336", fg="white", width=12, font=("Arial", 10)).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_ai_settings()