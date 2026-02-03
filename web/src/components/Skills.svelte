<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  let skills = [];
  let loading = true;
  let error = null;
  
  onMount(() => {
    loadSkills();
  });
  
  async function loadSkills() {
    loading = true;
    error = null;
    
    try {
      const response = await axios.get('/api/v1/skills/list');
      skills = response.data.skills || [];
    } catch (err) {
      error = err.message;
      console.error('Failed to load skills:', err);
    } finally {
      loading = false;
    }
  }
  
  async function installSkill(skillId) {
    try {
      await axios.post(`/api/v1/skills/install/${skillId}`);
      await loadSkills();
    } catch (err) {
      console.error('Failed to install skill:', err);
    }
  }
  
  async function uninstallSkill(skillId) {
    try {
      await axios.delete(`/api/v1/skills/uninstall/${skillId}`);
      await loadSkills();
    } catch (err) {
      console.error('Failed to uninstall skill:', err);
    }
  }
</script>

<div class="max-w-4xl mx-auto">
  <div class="mb-6">
    <h2 class="text-2xl font-bold text-white mb-2">Skills & Plugins</h2>
    <p class="text-gray-400">Manage ClawMate's capabilities with custom skills</p>
  </div>
  
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-400">Loading skills...</span>
    </div>
  {:else if error}
    <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
      <h3 class="text-red-400 font-medium">Error loading skills</h3>
      <p class="text-red-300 text-sm mt-1">{error}</p>
      <button on:click={loadSkills} class="mt-2 text-red-400 hover:text-red-300">Try again</button>
    </div>
  {:else}
    {#if skills.length === 0}
      <div class="text-center py-12">
        <div class="text-gray-500 mb-4">No skills installed yet</div>
        <p class="text-gray-400">Skills extend ClawMate's capabilities. Install skills to add new features.</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {#each skills as skill}
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-semibold text-white">{skill.name}</h3>
              <span class="text-xs text-gray-400">v{skill.version}</span>
            </div>
            <p class="text-sm text-gray-400 mb-3">{skill.description}</p>
            <div class="flex gap-2">
              <span class="text-xs bg-gray-700 px-2 py-1 rounded">{skill.status || 'Active'}</span>
              <button on:click={() => uninstallSkill(skill.id)} class="text-xs text-red-400 hover:text-red-300 ml-auto">Remove</button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>
