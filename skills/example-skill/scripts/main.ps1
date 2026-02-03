#!/usr/bin/env pwsh
<# 
.SYNOPSIS
Example skill for ClawMate demonstrating the skill system.
This skill provides simple tools for demonstration purposes.

.PARAMETER ToolName
The name of the tool to execute (hello, system_info)

.PARAMETER Name
Optional name parameter for the hello tool
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("hello", "system_info")]
    [string]$ToolName,
    
    [Parameter(Mandatory=$false)]
    [string]$Name = "World"
)

function Get-Hello {
    param(
        [Parameter(Mandatory=$false)]
        [string]$Name = "World"
    )
    
    return "Hello, $Name! This is the example skill speaking."
}

function Get-SystemInfo {
    $info = [PSCustomObject]@{
        Platform          = (Get-CimInstance -ClassName Win32_OperatingSystem).Caption
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        CurrentTime       = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        WorkingDirectory  = (Get-Location).Path
        OS                = (Get-CimInstance -ClassName Win32_OperatingSystem).OSArchitecture
        Architecture      = $env:PROCESSOR_ARCHITECTURE
        Processor         = (Get-CimInstance -ClassName Win32_Processor).Name
    }
    
    $result = "System Information:`n"
    foreach ($property in $info.PSObject.Properties) {
        $result += "  $($property.Name): $($property.Value)`n"
    }
    
    return $result
}

# Main execution
switch ($ToolName) {
    "hello" {
        Write-Output (Get-Hello -Name $Name)
    }
    "system_info" {
        Write-Output (Get-SystemInfo)
    }
    default {
        Write-Error "Unknown tool: $ToolName"
        Write-Output "Available tools: hello, system_info"
        exit 1
    }
}