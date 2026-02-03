<script>
  import { onMount, onDestroy } from 'svelte';
  import { Terminal } from 'xterm';
  import { FitAddon } from 'xterm-addon-fit';
  import { WebLinksAddon } from 'xterm-addon-web-links';
  
  let terminalContainer;
  let terminal;
  let fitAddon;
  let webLinksAddon;
  let messages = [];
  let inputText = '';
  let isStreaming = false;
  let ws;
  
  onMount(() => {
    // Initialize terminal
    terminal = new Terminal({
      theme: {
        background: '#0f172a',
        foreground: '#f8fafc',
        cursor: '#3b82f6'
      },
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      scrollback: 1000
    });
    
    fitAddon = new FitAddon();
    webLinksAddon = new WebLinksAddon();
    
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    terminal.open(terminalContainer);
    fitAddon.fit();
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Initial greeting
    terminal.writeln('🦀 Welcome to ClawMate!');
    terminal.writeln('Type /help for available commands');
    terminal.writeln('');
  });
  
  onDestroy(() => {
    if (ws) {
      ws.close();
    }
    if (terminal) {
      terminal.dispose();
    }
  });
  
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/chat/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.message) {
          terminal.writeln(`\x1b[34mAssistant:\x1b[0m ${data.message}`);
          isStreaming = false;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  async function sendMessage() {
    if (!inputText.trim() || isStreaming) return;
    
    // Display user message
    terminal.writeln(`\x1b[32mYou:\x1b[0m ${inputText}`);
    terminal.writeln('');
    
    // Send to WebSocket
    const message = {
      messages: [
        { role: 'user', content: inputText }
      ]
    };
    
    ws.send(JSON.stringify(message));
    
    // Clear input
    inputText = '';
    isStreaming = true;
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="h-full flex flex-col">
  <!-- Terminal Area -->
  <div class="flex-1 bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
    <div 
      bind:this={terminalContainer}
      class="h-full w-full"
      style="width: 100%; height: 100%;"
    ></div>
  </div>
  
  <!-- Input Area -->
  <div class="mt-4 flex gap-3">
    <input
      bind:value={inputText}
      on:keydown={handleKeyDown}
      placeholder="Type your message... (use /help for commands)"
      class="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
      disabled={isStreaming}
    />
    <button
      on:click={sendMessage}
      disabled={!inputText.trim() || isStreaming}
      class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
    >
      {isStreaming ? 'Sending...' : 'Send'}
    </button>
  </div>
  
  <!-- Quick Actions -->
  <div class="mt-4 flex gap-2 text-sm text-gray-400">
    <span>Quick actions:</span>
    <span class="text-blue-400">/help</span>
    <span>•</span>
    <span class="text-blue-400">/system</span>
    <span>•</span>
    <span class="text-blue-400">/skills</span>
  </div>
</div>

<style>
  :global(.xterm) {
    font-feature-settings: "liga" 0;
  }
  
  :global(.xterm-viewport) {
    overflow-y: auto;
  }
</style>