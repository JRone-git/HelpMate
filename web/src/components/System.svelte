<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  let systemInfo = null;
  let ollamaStatus = null;
  let healthCheck = null;
  let loading = false;
  let error = null;
  
  onMount(() => {
    loadSystemInfo();
  });
  
  async function loadSystemInfo() {
    loading = true;
    error = null;
    
    try {
      // Load all system data in parallel
      const [systemResponse, ollamaResponse, healthResponse] = await Promise.all([
        axios.get('/api/v1/system'),
        axios.get('/api/v1/ollama/status'),
        axios.get('/api/v1/health')
      ]);
      
      systemInfo = systemResponse.data;
      ollamaStatus = ollamaResponse.data;
      healthCheck = healthResponse.data;
    } catch (err) {
      error = err.message;
      console.error('Failed to load system info:', err);
    } finally {
      loading = false;
    }
  }
  
  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  }
</script>

<div class="h-full">
  <!-- Header -->
  <div class="mb-6">
    <h2 class="text-2xl font-bold text-white mb-2">System Information</h2>
    <p class="text-gray-400">Monitor system resources and ClawMate status</p>
  </div>
  
  <!-- Controls -->
  <div class="flex gap-3 mb-6">
    <button
      on:click={loadSystemInfo}
      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
    >
      Refresh
    </button>
    <button
      class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
    >
      Export Report
    </button>
  </div>
  
  <!-- Loading State -->
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-400">Loading system information...</span>
    </div>
  {/if}
  
  <!-- Error State -->
  {#if error}
    <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
      <h3 class="text-red-400 font-medium">Error loading system info</h3>
      <p class="text-red-300 text-sm mt-1">{error}</p>
      <button on:click={loadSystemInfo} class="mt-2 text-red-400 hover:text-red-300">Try again</button>
    </div>
  {/if}
  
  <!-- System Overview -->
  {#if !loading && !error && healthCheck}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Status Card -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-gray-400">Status</h3>
          <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
        </div>
        <div class="text-2xl font-bold text-white">{healthCheck.status}</div>
        <div class="text-sm text-gray-400 mt-1">Version {healthCheck.version}</div>
      </div>
      
      <!-- Ollama Status -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-gray-400">Ollama</h3>
          <div class={healthCheck.ollama_connected ? 'w-3 h-3 bg-green-500 rounded-full' : 'w-3 h-3 bg-red-500 rounded-full'}></div>
        </div>
        <div class="text-2xl font-bold text-white">{healthCheck.ollama_connected ? 'Connected' : 'Disconnected'}</div>
        <div class="text-sm text-gray-400 mt-1">{healthCheck.skills_loaded} skills loaded</div>
      </div>
      
      <!-- CPU Usage -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-gray-400">CPU</h3>
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-white">{systemInfo?.cpu_count || 'N/A'}</div>
        <div class="text-sm text-gray-400 mt-1">Cores</div>
      </div>
      
      <!-- Memory Usage -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-gray-400">Memory</h3>
          <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3-3m0 0l3 3m-3-3v12"></path>
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-white">{systemInfo ? formatBytes(systemInfo.memory_available) : 'N/A'}</div>
        <div class="text-sm text-gray-400 mt-1">Available</div>
      </div>
    </div>
    
    <!-- Detailed Information -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- System Details -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">System Details</h3>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-400">Platform</span>
            <span class="text-white">{systemInfo?.platform || 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Shell</span>
            <span class="text-white">{systemInfo?.shell || 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Python Version</span>
            <span class="text-white">{systemInfo?.python_version || 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">CPU Cores</span>
            <span class="text-white">{systemInfo?.cpu_count || 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Total Memory</span>
            <span class="text-white">{systemInfo ? formatBytes(systemInfo.memory_total) : 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Available Memory</span>
            <span class="text-white">{systemInfo ? formatBytes(systemInfo.memory_available) : 'Unknown'}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Disk Usage</span>
            <span class="text-white">{systemInfo ? formatBytes(systemInfo.disk_usage) : 'Unknown'}</span>
          </div>
        </div>
      </div>
      
      <!-- Ollama Details -->
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Ollama Status</h3>
        {#if ollamaStatus}
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-400">Connection</span>
              <span class={ollamaStatus.connected ? 'text-green-400' : 'text-red-400'}>
                {ollamaStatus.connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Current Model</span>
              <span class="text-white">{ollamaStatus.current_model}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Available Models</span>
              <span class="text-white">{ollamaStatus.models.length}</span>
            </div>
            
            {#if ollamaStatus.models.length > 0}
              <div class="mt-4">
                <h4 class="text-sm font-medium text-gray-400 mb-2">Available Models</h4>
                <div class="space-y-2">
                  {#each ollamaStatus.models as model}
                    <div class="flex justify-between items-center p-2 bg-gray-700 rounded">
                      <span class="text-sm text-white">{model.name}</span>
                      <span class="text-xs text-gray-400">{model.size ? formatBytes(model.size) : 'Unknown size'}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <div class="text-gray-400">Ollama status not available</div>
        {/if}
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-white mb-4">Quick Actions</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button class="p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7h16M4 12h16M4 17h16"></path>
              </svg>
            </div>
            <div>
              <div class="font-medium text-white">View Logs</div>
              <div class="text-sm text-gray-400">Check system logs</div>
            </div>
          </div>
        </button>
        
        <button class="p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <div class="font-medium text-white">Run Diagnostics</div>
              <div class="text-sm text-gray-400">System health check</div>
            </div>
          </div>
        </button>
        
        <button class="p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
            <div>
              <div class="font-medium text-white">Configure Settings</div>
              <div class="text-sm text-gray-400">Adjust preferences</div>
            </div>
          </div>
        </button>
      </div>
    </div>
  {/if}
</div>