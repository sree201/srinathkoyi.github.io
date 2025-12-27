// Terminal Interface JavaScript for Network Device Simulation

document.addEventListener('DOMContentLoaded', function() {
    const terminalInputs = document.querySelectorAll('.terminal-input');
    
    // Track authentication state per device
    const deviceAuthState = {};
    const deviceWaitingPassword = {};
    
    terminalInputs.forEach(input => {
        const deviceName = input.dataset.device;
        const labId = input.dataset.labId;
        const output = document.getElementById(`output-${deviceName}`);
        
        // Initialize auth state
        deviceAuthState[deviceName] = false;
        deviceWaitingPassword[deviceName] = false;
        
        // Command history
        let commandHistory = [];
        let historyIndex = -1;
        
        // Focus on first active terminal
        const activeWrapper = document.querySelector('.terminal-wrapper.active');
        if (activeWrapper) {
            const activeInput = activeWrapper.querySelector('.terminal-input');
            if (activeInput) {
                activeInput.focus();
            }
        }
        
        // Set initial prompt based on device type
        const deviceItem = document.querySelector(`.device-item[data-device="${deviceName}"]`);
        const deviceType = deviceItem ? deviceItem.querySelector('.device-info small')?.textContent.toLowerCase() : '';
        const isRouterOrSwitch = deviceType.includes('cisco') || deviceType.includes('arista');
        
        if (isRouterOrSwitch && !deviceAuthState[deviceName]) {
            // Show user mode prompt initially
            const initialPrompt = output.querySelector('.terminal-line .prompt');
            if (initialPrompt) {
                initialPrompt.textContent = `${deviceName}>`;
            }
        }
        
        input.addEventListener('keydown', async function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const command = this.value.trim();
                const isPasswordMode = deviceWaitingPassword[deviceName];
                
                if (command || isPasswordMode) {
                    // Add to history (unless it's a password)
                    if (!isPasswordMode) {
                        commandHistory.push(command);
                        historyIndex = commandHistory.length;
                    }
                    
                    // Display command in output (mask password)
                    if (isPasswordMode) {
                        addOutputLine(output, `Password: ${'*'.repeat(command.length)}`, 'command');
                    } else {
                        const prompt = deviceAuthState[deviceName] ? '#' : '>';
                        addOutputLine(output, `${deviceName}${prompt} ${command}`, 'command');
                    }
                    
                    // Clear input
                    this.value = '';
                    
                    // Execute command
                    try {
                        const response = await fetch(`/api/lab/${labId}/device/${deviceName}/command`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ 
                                command: isPasswordMode ? 'enable' : command,
                                password: isPasswordMode ? command : ''
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.authenticated !== undefined) {
                            deviceAuthState[deviceName] = data.authenticated;
                            // Update prompt in input line
                            const promptElement = document.getElementById(`prompt-${deviceName}`);
                            if (promptElement) {
                                promptElement.textContent = `${deviceName}${data.authenticated ? '#' : '>'}`;
                            }
                        }
                        
                        if (data.requires_password) {
                            deviceWaitingPassword[deviceName] = true;
                            addOutputLine(output, 'Password:', 'output');
                            this.type = 'password';
                        } else {
                            deviceWaitingPassword[deviceName] = false;
                            this.type = 'text';
                            
                            if (data.success) {
                                // Display output
                                if (data.output) {
                                    addOutputLine(output, data.output, 'output');
                                }
                                
                                // Add new prompt
                                const prompt = deviceAuthState[deviceName] ? '#' : '>';
                                addPrompt(output, deviceName, prompt);
                            } else {
                                // Error case
                                if (data.output) {
                                    addOutputLine(output, data.output, 'error');
                                }
                                const prompt = deviceAuthState[deviceName] ? '#' : '>';
                                addPrompt(output, deviceName, prompt);
                            }
                        }
                    } catch (error) {
                        console.error('Error executing command:', error);
                        addOutputLine(output, 'Error: Could not execute command', 'error');
                        const prompt = deviceAuthState[deviceName] ? '#' : '>';
                        addPrompt(output, deviceName, prompt);
                        deviceWaitingPassword[deviceName] = false;
                        this.type = 'text';
                    }
                } else {
                    // Empty command - just show new prompt
                    const prompt = deviceAuthState[deviceName] ? '#' : '>';
                    addPrompt(output, deviceName, prompt);
                }
            } else if (e.key === 'ArrowUp' && !deviceWaitingPassword[deviceName]) {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    this.value = commandHistory[historyIndex];
                }
            } else if (e.key === 'ArrowDown' && !deviceWaitingPassword[deviceName]) {
                e.preventDefault();
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    this.value = commandHistory[historyIndex];
                } else {
                    historyIndex = commandHistory.length;
                    this.value = '';
                }
            } else if (e.key === 'Tab') {
                e.preventDefault();
                // Could implement tab completion here
            }
        });
        
        // Keep cursor in view
        input.addEventListener('input', function() {
            // Scroll terminal output to bottom
            if (output) {
                output.scrollTop = output.scrollHeight;
            }
        });
    });
    
    // Handle terminal tab switching focus
    document.querySelectorAll('.terminal-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            setTimeout(() => {
                const deviceName = this.dataset.device;
                const input = document.querySelector(`.terminal-input[data-device="${deviceName}"]`);
                if (input) {
                    input.focus();
                }
            }, 100);
        });
    });

    // Refresh devices button (simple page reload to pick up DB changes)
    const refreshBtn = document.getElementById('refresh-devices');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }
});

function addOutputLine(output, text, type = 'output') {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    
    if (type === 'command') {
        line.innerHTML = `<span class="prompt">${text.split(' ')[0]}#</span> ${text.split(' ').slice(1).join(' ')}`;
    } else if (type === 'error') {
        line.style.color = '#ef4444';
        line.textContent = text;
    } else {
        line.textContent = text;
    }
    
    output.appendChild(line);
    
    // Remove cursor from last line if it exists
    const lastCursor = output.querySelector('.cursor-blink');
    if (lastCursor) {
        lastCursor.remove();
    }
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
}

function addPrompt(output, deviceName, promptType = '#') {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `<span class="prompt">${deviceName}${promptType}</span><span class="cursor-blink">_</span>`;
    output.appendChild(line);
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
}

// Save lab progress periodically
function saveLabProgress(labId, config) {
    fetch(`/api/lab/${labId}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            config: config,
            status: 'In Progress'
        })
    }).catch(error => {
        console.error('Error saving lab progress:', error);
    });
}

// Auto-save progress every 30 seconds
setInterval(() => {
    const activeInput = document.querySelector('.terminal-wrapper.active .terminal-input');
    if (activeInput) {
        const labId = activeInput.dataset.labId;
        if (labId) {
            // Get current terminal state (simplified - in real app, capture full config)
            const output = document.querySelector(`#output-${activeInput.dataset.device}`);
            if (output) {
                const config = output.innerText;
                saveLabProgress(labId, config);
            }
        }
    }
}, 30000);

