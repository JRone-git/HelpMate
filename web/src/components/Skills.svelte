<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  let skills = [];
  let loading = false;
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

<div class="h-full">
  <!-- Header -->
  <div class="mb-6">
    <h2 class="text-2xl font-bold text-white mb-2">Skills & Plugins</h2>
    <p class="text-gray-400">Extend ClawMate's capabilities with custom skills</p>
  </div>
  
  <!-- Controls -->
  <div class="flex gap-3 mb-6">
    <button
      on:click={loadSkills}
      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
    >
      Refresh
    </button>
    <button
      class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
    >
      Install from URL
    </button>
  </div>
  
  <!-- Loading State -->
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-400">Loading skills...</span>
    </div>
  {/if}
  
  <!-- Error State -->
  {#if error}
    <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
      <h3 class="text-red-400 font-medium">Error loading skills</h3>
      <p class="text-red-300 text-sm mt-1">{error}</p>
      <button on:click={loadSkills} class="mt-2 text-red-400 hover:text-red-300">Try again</button>
    </div>
  {/if}
  
  <!-- Skills Grid -->
  {#if !loading && !error}
    {#if skills.length === 0}
      <div class="text-center py-12">
        <div class="text-gray-500 mb-4">No skills installed yet</div>
        <p class="text-gray-400">Skills extend ClawMate's capabilities. You can create custom skills or install from the marketplace.</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each skills as skill}
          <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-white mb-1">{skill.name}</h3>
                <p class="text-sm text-gray-400 mb-2">{skill.description}</p>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <span>Version: {skill.version}</span>
                  <span>•</span>
                  <span>{skill.author || 'Unknown author'}</span>
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  on:click={() => installSkill(skill.id)}
                  class="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                >
                  Install
                </button>
                <button
                  on:click={() => uninstallSkill(skill.id)}
                  class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
            
            <div class="space-y-2">
              <div class="text-xs text-gray-500">Tools:</div>
              <div class="flex flex-wrap gap-2">
                {#each skill.tools || [] as tool}
                  <span class="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">{tool}</span>
                {/each}
              </div>
            </div>
            
            {#if skill.documentation}
              <div class="mt-4 text-xs text-gray-400">
                <a href={skill.documentation} target="_blank" class="hover:text-gray-300">
                  Documentation →
                </a>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
  
  <!-- Skill Development Guide -->
  <div class="mt-12 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <h3 class="text-lg font-semibold text-white mb-4">Develop Your Own Skills</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-300">
      <div>
        <h4 class="font-medium mb-2">Skill Structure</h4>
        <pre class="bg-gray-900 p-3 rounded text-xs overflow-auto">{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "A custom skill",
  "tools": ["bash", "git"],
  "entrypoint": "scripts/main.py"
}</pre>
      </div>
      <div>
        <h4 class="font-medium mb-2">Available Tools</h4>
        <ul class="space-y-1">
          <li>• <strong>bash:</strong> Execute shell commands</li>
          <li>• <strong>git:</strong> Git operations</li>
          <li>• <strong>file:</strong> File operations</li>
          <li>• <strong>http:</strong> HTTP requests</li>
          <li>• <strong>docker:</strong> Container operations</li>
        </ul>
      </div>
    </div>
    <div class="mt-4 flex gap-3">
      <a href="#" class="text-blue-400 hover:text-blue-300">Skill Development Guide</a>
      <a href="#" class="text-blue-400 hover:text-blue-300">API Reference</a>
      <a href="#" class="text-blue-400 hover:text-blue-300">Examples</a>
    </div>
  </div>
</div>