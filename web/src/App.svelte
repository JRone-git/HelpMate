<script>
  import { onMount } from 'svelte';
  
  // Import components
  import Layout from './components/Layout.svelte';
  import Chat from './components/Chat.svelte';
  import Terminal from './components/Terminal.svelte';
  import Skills from './components/Skills.svelte';
  import System from './components/System.svelte';
  
  // Simple route management
  let currentRoute = window.location.pathname;
  
  function navigate(path) {
    currentRoute = path;
    window.history.pushState({}, '', path);
  }
  
  onMount(() => {
    console.log('ClawMate AI Assistant initialized');
    
    // Listen for route changes
    window.addEventListener('popstate', () => {
      currentRoute = window.location.pathname;
    });
  });
  
  function getComponent() {
    switch(currentRoute) {
      case '/terminal': return Terminal;
      case '/skills': return Skills;
      case '/system': return System;
      default: return Chat;
    }
  }
</script>

<Layout {currentRoute} {navigate}>
  <svelte:component this={getComponent()} />
</Layout>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
  }
</style>
