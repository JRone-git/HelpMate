<script>
  import { onMount, onDestroy } from 'svelte';
  import { Terminal } from 'xterm';
  import { FitAddon } from 'xterm-addon-fit';
  import { WebLinksAddon } from 'xterm-addon-web-links';
  
  let terminalContainer;
  let terminal;
  let fitAddon;
  let webLinksAddon;
  let ws;
  let commandInput = '';
  let isStreaming = false;
  let isConnected = false;
  
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
      scrollback: 1000,
      convertEol: true
    });
    
    fitAddon = new FitAddon();
    webLinksAddon = new WebLinksAddon();
    
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    terminal.open(terminalContainer);
    fitAddon.fit();
    
    // Connect to command WebSocket
    connectCommandWebSocket();
    
    // Initial setup
    terminal.writeln('🖥️  ClawMate Terminal Interface');
    terminal.writeln('Connected to local shell executor');
    terminal.writeln('');
    terminal.writeln('Available commands:');
    terminal.writeln('  /help     - Show help');
    terminal.writeln('  /clear    - Clear terminal');
    terminal.writeln('  /system   - Show system info');
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
  
  function connectCommandWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/commands/stream/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('Command WebSocket connected');
      isConnected = true;
    };
    
    ws.onmessage = (event) => {
      try {
        const output = event.data;
        terminal.write(output);
      } catch (e) {
        console.error('Failed to parse command output:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('Command WebSocket disconnected');
      isConnected = false;
      // Attempt to reconnect after 3 seconds
      setTimeout(connectCommandWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('Command WebSocket error:', error);
    };
  }
  
  function sendCommand() {
    if (!commandInput.trim() || !isConnected) return;
    
    // Display command
    terminal.writeln(`$ ${commandInput}`);
    
    // Send to WebSocket
    const request = {
      command: commandInput,
      args: [],
      pty: true
    };
    
    ws.send(JSON.stringify(request));
    
    // Clear input
    commandInput = '';
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendCommand();
    }
  }
  
  function clearTerminal() {
    terminal.clear();
    terminal.writeln('🖥️  ClawMate Terminal Interface');
    terminal.writeln('Connected to local shell executor');
    terminal.writeln('');
  }
  
  function showHelp() {
    terminal.writeln('');
    terminal.writeln('🔧 Available Commands:');
    terminal.writeln('  /help     - Show this help message');
    terminal.writeln('  /clear    - Clear terminal screen');
    terminal.writeln('  /system   - Show system information');
    terminal.writeln('  /exit     - Close terminal connection');
    terminal.writeln('');
    terminal.writeln('💡 Tips:');
    terminal.writeln('  - Use standard shell commands (ls, cd, pwd, etc.)');
    terminal.writeln('  - Commands run with user permissions by default');
    terminal.writeln('  - Use /exit to safely disconnect');
    terminal.writeln('');
  }
</script>

<div class="h-full flex flex-col">
  <!-- Terminal Header -->
  <div class="flex items-center justify-between p-4 bg-gray-800 border border-gray-700 rounded-t-lg">
    <div class="flex items-center gap-3">
      <div class="flex gap-2">
        <div class="w-3 h-3 bg-red-500 rounded-full"></div>
        <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
        <div class="w-3 h-3 bg-green-500 rounded-full"></div>
      </div>
      <span class="text-sm font-medium text-gray-300">Terminal</span>
    </div>
    
    <div class="flex gap-2 text-sm">
      <span class="px-2 py-1 bg-gray-700 rounded text-gray-300">Shell: {navigator.platform.includes('Win') ? 'PowerShell' : 'Bash'}</span>
      <span class="px-2 py-1 bg-gray-700 rounded text-gray-300">Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
    </div>
  </div>
  
  <!-- Terminal Area -->
  <div class="flex-1 bg-gray-900 border border-gray-700 border-t-0 rounded-b-lg overflow-hidden">
    <div 
      bind:this={terminalContainer}
      class="h-full w-full"
      style="width: 100%; height: 100%;"
    ></div>
  </div>
  
  <!-- Input Area -->
  <div class="mt-4 flex gap-3">
    <input
      bind:value={commandInput}
      on:keydown={handleKeyDown}
      placeholder="Enter command... (type /help for available commands)"
      class="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
      disabled={!isConnected}
    />
    <button
      on:click={sendCommand}
      disabled={!commandInput.trim() || !isConnected}
      class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
    >
      Execute
    </button>
  </div>
  
  <!-- Quick Actions -->
  <div class="mt-4 flex gap-2 text-sm text-gray-400">
    <span>Quick commands:</span>
    <button on:click={() => { commandInput = 'ls'; sendCommand(); }} class="text-blue-400 hover:text-blue-300">ls</button>
    <span>•</span>
    <button on:click={() => { commandInput = 'pwd'; sendCommand(); }} class="text-blue-400 hover:text-blue-300">pwd</button>
    <span>•</span>
    <button on:click={() => { commandInput = 'whoami'; sendCommand(); }} class="text-blue-400 hover:text-blue-300">whoami</button>
    <span>•</span>
    <button on:click={() => { commandInput = 'date'; sendCommand(); }} class="text-blue-400 hover:text-blue-300">date</button>
  </div>
</div>

<style>
  :global(.xterm) {
    font-feature-settings: "liga" 0;
  }
  
  :global(.xterm-viewport) {
    overflow-y: auto;
  }
  
  :global(.xterm .xterm-rows) {
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  }
</style>