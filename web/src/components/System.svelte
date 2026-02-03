<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  let systemInfo = null;
  let healthStatus = null;
  let loading = true;
  let error = null;
  
  onMount(() => {
    loadSystemInfo();
  });
  
  async function loadSystemInfo() {
    loading = true;
    error = null;
    
    try {
      const [healthRes, systemRes] = await Promise.all([
        axios.get('/api/v1/health'),
        axios.get('/api/v1/system')
      ]);
      
      healthStatus = healthRes.data;
      systemInfo = systemRes.data;
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
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
</script>

<div class="max-w-4xl mx-auto space-y-6">
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-400">Loading system information...</span>
    </div>
  {:else if error}
    <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
      <h3 class="text-red-400 font-medium">Error loading system info</h3>
      <p class="text-red-300 text-sm mt-1">{error}</p>
      <button on:click={loadSystemInfo} class="mt-2 text-red-400 hover:text-red-300">Try again</button>
    </div>
  {:else}
    <!-- Status Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-sm text-gray-400">Status</div>
        <div class="flex items-center gap-2 mt-1">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-lg font-semibold">{healthStatus?.status || 'Unknown'}</span>
        </div>
      </div>
      
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-sm text-gray-400">Ollama</div>
        <div class="flex items-center gap-2 mt-1">
          <div class="w-2 h-2 {healthStatus?.ollama_connected ? 'bg-green-500' : 'bg-red-500'} rounded-full"></div>
          <span class="text-lg font-semibold">{healthStatus?.ollama_connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
      
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-sm text-gray-400">Skills Loaded</div>
        <div class="text-lg font-semibold mt-1">{healthStatus?.skills_loaded || 0}</div>
      </div>
    </div>
    
    <!-- System Details -->
    {#if systemInfo}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold mb-4">System Details</h3>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-400">Platform:</span>
            <span class="ml-2">{systemInfo.platform}</span>
          </div>
          <div>
            <span class="text-gray-400">Python:</span>
            <span class="ml-2">{systemInfo.python_version}</span>
          </div>
          <div>
            <span class="text-gray-400">CPU Cores:</span>
            <span class="ml-2">{systemInfo.cpu_count}</span>
          </div>
          <div>
            <span class="text-gray-400">Memory:</span>
            <span class="ml-2">{formatBytes(systemInfo.memory_available)} / {formatBytes(systemInfo.memory_total)}</span>
          </div>
          <div>
            <span class="text-gray-400">Shell:</span>
            <span class="ml-2">{systemInfo.shell}</span>
          </div>
          <div>
            <span class="text-gray-400">Working Directory:</span>
            <span class="ml-2 font-mono">{systemInfo.cwd}</span>
          </div>
        </div>
      </div>
    {/if}
    
    <!-- Refresh Button -->
    <div class="flex justify-end">
      <button
        on:click={loadSystemInfo}
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
      >
        Refresh
      </button>
    </div>
  {/if}
</div>
