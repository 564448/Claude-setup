$out = @{
    hookSpecificOutput = @{
        hookEventName = 'SessionStart'
        additionalContext = 'New session started. Before proceeding with any task, confirm with the user whether to work in C:\Knight (or a specific subfolder such as ClaudeTaughtMe, CS, or Project) for this session.'
    }
}
$out | ConvertTo-Json -Depth 5 -Compress
