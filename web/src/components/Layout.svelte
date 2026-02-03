<script>
  import { Link, useRoute } from 'svelte-spa-router';
  import { Menu, X, Home, Terminal, Settings, Cpu } from 'lucide-svelte';
  
  let isSidebarOpen = true;
  let route = useRoute();
  
  const navigation = [
    { name: 'Chat', href: '/', icon: Home },
    { name: 'Terminal', href: '/terminal', icon: Terminal },
    { name: 'Skills', href: '/skills', icon: Settings },
    { name: 'System', href: '/system', icon: Cpu }
  ];
</script>

<div class="flex h-screen bg-gray-900 text-white">
  <!-- Sidebar -->
  <aside class="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
    <div class="p-4 border-b border-gray-700">
      <h1 class="text-xl font-bold flex items-center gap-2">
        <span class="w-3 h-3 bg-blue-500 rounded-full"></span>
        ClawMate
      </h1>
      <p class="text-sm text-gray-400 mt-1">Personal Assistant</p>
    </div>
    
    <nav class="flex-1 p-4 space-y-2">
      {#each navigation as item}
        <Link
          href={item.href}
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-gray-700 hover:text-white"
          class:active={route.path === item.href}
        >
          <svelte:component this={item.icon} class="w-5 h-5" />
          {item.name}
        </Link>
      {/each}
    </nav>
    
    <div class="p-4 border-t border-gray-700">
      <div class="text-xs text-gray-400">Status</div>
      <div class="flex items-center gap-2 mt-2">
        <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span class="text-sm">Connected</span>
      </div>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="flex-1 flex flex-col overflow-hidden">
    <header class="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold">
            {#each navigation as item}
              {#if route.path === item.href}
                {item.name}
              {/if}
            {/each}
          </h2>
          <p class="text-sm text-gray-400 mt-1">
            Cross-platform AI assistant with local Ollama integration
          </p>
        </div>
        
        <div class="flex items-center gap-4">
          <div class="text-xs text-gray-400">
            Model: <span class="text-blue-400">qwen3-coder:latest</span>
          </div>
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </div>
    </header>
    
    <div class="flex-1 overflow-auto p-6">
      <slot />
    </div>
  </main>
</div>

<style>
  .active {
    background-color: #334155;
    color: #ffffff;
  }
</style>