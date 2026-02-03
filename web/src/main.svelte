<script>
  import { onMount } from 'svelte';
  import Layout from './components/Layout.svelte';
  
  // Import global styles
  import './global.css';
  
  onMount(() => {
    console.log('Portfolio Website initialized');
  });
</script>
<Layout />

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>

