<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  let commands = [];
  let currentCommand = '';
  let isExecuting = false;
  let terminalEnd;
  let backendStatus = 'checking';
  
  onMount(() => {
    commands = [
      { type: 'system', content: 'ClawMate Terminal - Ready' },
      { type: 'system', content: 'Type commands to execute them on your system' }
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
      commands = [
        ...commands,
        { type: 'error', content: '⚠️ Backend server is not running. Please start the Python backend first.' }
      ];
    }
  }
  
  async function executeCommand() {
    if (!currentCommand.trim() || isExecuting || backendStatus !== 'connected') return;
    
    const cmd = currentCommand.trim();
    currentCommand = '';
    
    commands = [...commands, { type: 'input', content: cmd }];
    isExecuting = true;
    
    try {
      const response = await axios.post('/api/v1/commands/execute', {
        command: cmd,
        args: [],
        pty: false
      });
      
      commands = [...commands, { 
        type: 'output', 
        content: response.data.stdout || 'Command executed successfully',
        error: response.data.stderr,
        exitCode: response.data.exit_code
      }];
    } catch (error) {
      console.error('Terminal error:', error);
      let errorMessage = 'Command execution failed.';
      
      if (error.response) {
        if (error.response.status === 500) {
          errorMessage = 'Backend server error. Please check the server logs.';
        } else if (error.response.status === 404) {
          errorMessage = 'API endpoint not found. Please check if the backend is running.';
        }
      } else if (error.request) {
        errorMessage = 'Unable to connect to backend server. Please make sure it\'s running.';
      }
      
      commands = [...commands, { 
        type: 'error', 
        content: errorMessage 
      }];
    } finally {
      isExecuting = false;
      scrollToBottom();
    }
  }
  
  function scrollToBottom() {
    if (terminalEnd) {
      terminalEnd.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      executeCommand();
    }
  }
  
  function clearTerminal() {
    commands = [
      { type: 'system', content: 'Terminal cleared. Ready for new commands.' }
    ];
  }
</script>

<div class="h-full flex flex-col max-w-4xl mx-auto font-mono">
  <!-- Terminal Output -->
  <div class="flex-1 overflow-y-auto bg-gray-950 border border-gray-700 rounded-lg p-4 mb-4 space-y-2">
    {#each commands as cmd}
      {#if cmd.type === 'system'}
        <div class="text-gray-500 text-sm">{cmd.content}</div>
      {:else if cmd.type === 'input'}
        <div class="flex gap-2">
          <span class="text-green-400">$</span>
          <span class="text-white">{cmd.content}</span>
        </div>
      {:else if cmd.type === 'output'}
        <div class="pl-4 text-gray-300 whitespace-pre-wrap">{cmd.content}</div>
        {#if cmd.error}
          <div class="pl-4 text-red-400 whitespace-pre-wrap">{cmd.error}</div>
        {/if}
      {:else if cmd.type === 'error'}
        <div class="pl-4 text-red-400">Error: {cmd.content}</div>
      {/if}
    {/each}
    
    <div bind:this={terminalEnd}></div>
  </div>
  
  <!-- Command Input -->
  <div class="flex gap-2">
    <span class="text-green-400 py-2">$</span>
    <input
      bind:value={currentCommand}
      on:keydown={handleKeyDown}
      placeholder="Enter command..."
      class="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
      disabled={isExecuting}
    />
    <button
      on:click={executeCommand}
      disabled={!currentCommand.trim() || isExecuting}
      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
    >
      {#if isExecuting}
        <span class="animate-pulse">...</span>
      {:else}
        Execute
      {/if}
    </button>
  </div>
</div>
