<script>
  import { onMount } from 'svelte';
  import { Router } from 'svelte-spa-router';
  
  // Import components
  import Layout from './components/Layout.svelte';
  import Chat from './components/Chat.svelte';
  import Terminal from './components/Terminal.svelte';
  import Skills from './components/Skills.svelte';
  import System from './components/System.svelte';
  
  // Routes configuration
  const routes = {
    '/': Chat,
    '/terminal': Terminal,
    '/skills': Skills,
    '/system': System
  };
  
  onMount(() => {
    // Initialize API connection
    console.log('ClawMate Web Interface initialized');
  });
</script>

<Router {routes}>
  <Layout>
    <slot />
  </Layout>
</Router>

<style>
  :root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #3b82f6;
  }
  
  body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
</style>