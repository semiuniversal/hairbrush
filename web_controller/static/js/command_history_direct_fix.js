/**
 * Simple Command History Fix
 */
(function() {
    // Wait for DOM to be fully loaded
    window.addEventListener('load', function() {
        console.log('Simple command history fix loaded');
        
        // Get the command history container
        const commandHistoryContainer = document.getElementById('command-history');
        if (!commandHistoryContainer) {
            console.error('Command history container not found');
            return;
        }
        
        // Apply basic styles
        commandHistoryContainer.style.height = '300px';
        commandHistoryContainer.style.overflowY = 'scroll';
        commandHistoryContainer.style.whiteSpace = 'pre-wrap';
        commandHistoryContainer.style.fontFamily = 'monospace';
        commandHistoryContainer.style.fontSize = '14px';
        commandHistoryContainer.style.padding = '10px';
        commandHistoryContainer.style.lineHeight = '1.2'; // Reduce line height for compactness
        
        // Clear existing content
        commandHistoryContainer.innerHTML = '<div class="text-muted text-center">No commands sent yet</div>';
        
        // Keep track of commands as simple text
        let commandHistory = [];
        const MAX_COMMANDS = 100;
        
        // Override the global addToCommandHistory function with a simple version
        window.addToCommandHistory = function(command, result, isError = false) {
            // Clear "no commands" message if it's the only content
            if (commandHistoryContainer.textContent === 'No commands sent yet') {
                commandHistoryContainer.innerHTML = '';
            }
            
            // Format the command entry
            const commandText = `> ${command}`;
            
            // Handle different result types
            let resultText = '';
            if (result === null || result === undefined) {
                resultText = 'No response';
            } else if (typeof result === 'object') {
                try {
                    // Try to stringify the object with nice formatting
                    resultText = JSON.stringify(result, null, 2);
                } catch (e) {
                    // If that fails, try to extract useful properties
                    resultText = Object.keys(result).map(key => `${key}: ${result[key]}`).join(', ');
                }
            } else {
                resultText = isError ? `ERROR: ${result}` : String(result);
            }
            
            // Create compact entry with minimal spacing
            const entry = `${commandText}\n${resultText}\n`;
            
            // Add to history array
            commandHistory.push(entry);
            
            // Trim history if too long
            if (commandHistory.length > MAX_COMMANDS) {
                commandHistory = commandHistory.slice(-MAX_COMMANDS);
            }
            
            // Update display
            commandHistoryContainer.innerHTML = commandHistory.join('');
            
            // Scroll to bottom
            commandHistoryContainer.scrollTop = commandHistoryContainer.scrollHeight;
            
            // Update command count if the element exists
            const commandCount = document.getElementById('command-count');
            if (commandCount) {
                commandCount.textContent = commandHistory.length;
                commandCount.className = 'badge ' + (commandHistory.length > 0 ? 'bg-primary' : 'bg-secondary');
            }
        };
        
        // Override clear history function
        const clearHistoryBtn = document.getElementById('clear-history');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', function() {
                commandHistory = [];
                commandHistoryContainer.innerHTML = '<div class="text-muted text-center">No commands sent yet</div>';
                
                // Update command count
                const commandCount = document.getElementById('command-count');
                if (commandCount) {
                    commandCount.textContent = '0';
                    commandCount.className = 'badge bg-secondary';
                }
            });
        }
        
        console.log('Simple command history fix applied');
    });
})(); 