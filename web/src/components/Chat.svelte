<script>
  import { onMount, onDestroy } from 'svelte';
  import axios from 'axios';
  
  let messages = [];
  let inputText = '';
  let isLoading = false;
  let messagesEnd;
  let backendStatus = 'checking';
  
  onMount(() => {
    // Add welcome message
    messages = [
      { role: 'assistant', content: 'Hello! I\'m ClawMate, your AI personal assistant. How can I help you today?' }
    ];
    
    // Check backend status
    checkBackendStatus();
  });
  
  async function checkBackendStatus() {
    try {
      const response = await axios.get('/api/v1/health', { timeout: 5000 });
      backendStatus = response.data.status === 'healthy' ? 'connected' : 'error';
    } catch (error) {
      backendStatus = 'disconnected';
      messages = [
        ...messages,
        { role: 'system', content: '⚠️ Backend server is not running. Please start the Python backend first.' }
      ];
    }
  }
  
  async function sendMessage() {
    if (!inputText.trim() || isLoading || backendStatus !== 'connected') return;
    
    const userMessage = inputText.trim();
    inputText = '';
    
    // Add user message
    messages = [...messages, { role: 'user', content: userMessage }];
    isLoading = true;
    
    try {
      const response = await axios.post('/api/v1/chat/send', {
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        stream: false
      });
      
      // Add assistant response
      messages = [...messages, { role: 'assistant', content: response.data.message }];
    } catch (error) {
      console.error('Chat error:', error);
      let errorMessage = 'Sorry, I encountered an error.';
      
      if (error.response) {
        if (error.response.status === 500) {
          errorMessage = 'Backend server error. Please check the server logs.';
        } else if (error.response.status === 404) {
          errorMessage = 'API endpoint not found. Please check if the backend is running.';
        }
      } else if (error.request) {
        errorMessage = 'Unable to connect to backend server. Please make sure it\'s running.';
      }
      
      messages = [...messages, { role: 'assistant', content: errorMessage }];
    } finally {
      isLoading = false;
      scrollToBottom();
    }
  }
  
  function scrollToBottom() {
    if (messagesEnd) {
      messagesEnd.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
  
  function clearChat() {
    messages = [
      { role: 'assistant', content: 'Chat cleared. How can I help you today?' }
    ];
  }
</script>

<div class="h-full flex flex-col max-w-4xl mx-auto">
  <!-- Chat Messages -->
  <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
    {#each messages as message}
      <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
        <div class="max-w-3xl {message.role === 'user' 
          ? 'bg-blue-600 text-white rounded-l-lg rounded-tr-lg' 
          : 'bg-gray-700 text-gray-100 rounded-r-lg rounded-tl-lg'} px-4 py-3">
          <div class="text-xs mb-1 {message.role === 'user' ? 'text-blue-200' : 'text-gray-400'}">
            {message.role === 'user' ? 'You' : 'Assistant'}
          </div>
          <div class="whitespace-pre-wrap">{message.content}</div>
        </div>
      </div>
    {/each}
    
    {#if isLoading}
      <div class="flex justify-start">
        <div class="bg-gray-700 text-gray-100 rounded-r-lg rounded-tl-lg px-4 py-3">
          <div class="text-xs mb-1 text-gray-400">Assistant</div>
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    {/if}
    
    <div bind:this={messagesEnd}></div>
  </div>
  
  <!-- Input Area -->
  <div class="border-t border-gray-700 pt-4">
    <div class="flex gap-3">
      <textarea
        bind:value={inputText}
        on:keydown={handleKeyDown}
        placeholder="Type your message... (Shift+Enter for new line)"
        class="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
        rows="2"
        disabled={isLoading}
      ></textarea>
      <button
        on:click={sendMessage}
        disabled={!inputText.trim() || isLoading}
        class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors self-end"
      >
        {#if isLoading}
          <span class="animate-pulse">...</span>
        {:else}
          Send
        {/if}
      </button>
    </div>
  </div>
</div>
