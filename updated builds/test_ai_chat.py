#!/usr/bin/env python3
"""
Simple test for AI chat page layout
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

def create_test_ai_page():
    root = tk.Tk()
    root.title("AI Chat Test")
    root.geometry("800x600")
    root.configure(bg="#222222")
    
    # Header with AI provider info
    header_frame = tk.Frame(root, bg="#222222")
    header_frame.pack(fill=tk.X, padx=10, pady=5)
    
    lbl_title = tk.Label(header_frame, text="AI Conversation", bg="#222222", fg="white", font=("Arial", 12, "bold"))
    lbl_title.pack(side=tk.LEFT)
    
    # Show current AI provider
    provider_label = tk.Label(header_frame, text="Provider: OpenAI", bg="#222222", fg="lightgray", font=("Arial", 9))
    provider_label.pack(side=tk.RIGHT)

    # Chat History
    history_frame = tk.Frame(root, bg="#222222")
    history_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
    
    chat_history = tk.Text(history_frame, bg="#333333", fg="#d2d2d2", font=("Arial", 10), 
                          wrap=tk.WORD, state=tk.DISABLED, bd=0, insertbackground="white")
    scrollbar = ttk.Scrollbar(history_frame, command=chat_history.yview)
    chat_history.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Tags for styling
    chat_history.tag_config("user", foreground="#87CEEB", justify="left")
    chat_history.tag_config("ai", foreground="#90EE90", justify="left")
    chat_history.tag_config("system", foreground="#FFD700", justify="center")

    # Input Area - This should be visible at the bottom
    input_frame = tk.Frame(root, bg="#444444", relief=tk.RAISED, bd=2)  # Added border to make it visible
    input_frame.pack(fill=tk.X, padx=10, pady=5, side=tk.BOTTOM)  # Explicitly pack at bottom
    
    # Add placeholder text functionality
    placeholder_text = "Ask me anything..."
    input_entry = tk.Entry(input_frame, bg="#333333", fg="gray", font=("Arial", 12), 
                          bd=0, insertbackground="white")
    input_entry.insert(0, placeholder_text)
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5, ipady=8)
    
    def on_entry_click(event):
        if input_entry.get() == placeholder_text:
            input_entry.delete(0, tk.END)
            input_entry.config(fg="white")

    def on_focusout(event):
        if input_entry.get() == '':
            input_entry.insert(0, placeholder_text)
            input_entry.config(fg="gray")
    
    input_entry.bind('<FocusIn>', on_entry_click)
    input_entry.bind('<FocusOut>', on_focusout)
    
    send_btn = tk.Button(input_frame, text="Send", bg="#4CAF50", fg="white", 
                        font=("Arial", 10), bd=0, cursor="hand2", padx=15, pady=5)
    send_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    # Clear chat button
    clear_btn = tk.Button(input_frame, text="Clear", bg="#666666", fg="white", 
                         font=("Arial", 10), bd=0, cursor="hand2", padx=10, pady=5)
    clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def append_message(sender, message, tag):
        chat_history.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        if sender:
            chat_history.insert(tk.END, f"[{timestamp}] {sender}:\n", tag)
        chat_history.insert(tk.END, f"{message}\n\n", tag)
        chat_history.config(state=tk.DISABLED)
        chat_history.see(tk.END)

    def handle_send(event=None):
        msg = input_entry.get().strip()
        if not msg or msg == placeholder_text:
            return
            
        input_entry.delete(0, tk.END)
        input_entry.config(fg="white")
        append_message("You", msg, "user")
        
        # Simulate AI response
        append_message("AI", f"You said: {msg}", "ai")
        input_entry.focus()
    
    def clear_chat():
        chat_history.config(state=tk.NORMAL)
        chat_history.delete(1.0, tk.END)
        chat_history.config(state=tk.DISABLED)
        append_message("System", "Chat cleared", "system")

    send_btn.config(command=handle_send)
    clear_btn.config(command=clear_chat)
    input_entry.bind("<Return>", handle_send)
    
    # Add welcome message
    append_message("System", "Welcome to AI Chat Test! The input box should be visible at the bottom.", "system")
    
    root.mainloop()

if __name__ == "__main__":
    create_test_ai_page()