document.addEventListener('DOMContentLoaded', function() {
    const hostInput = document.getElementById('host-input');
    const browseBtn = document.getElementById('browse-btn');
    const output = document.getElementById('browser-output');

    // DNS UI elements
    const dnsHostInput = document.getElementById('dns-host-input');
    const dnsResponseInput = document.getElementById('dns-response-input');
    const addDnsBtn = document.getElementById('add-dns-btn');
    const dnsMessage = document.getElementById('dns-message');

    // Helper to get labId and deviceName from path
    function _parsePath() {
        const parts = window.location.pathname.split('/');
        const labIdx = parts.indexOf('lab');
        const labId = parts[labIdx+1];
        const deviceName = parts[labIdx+3];
        return {labId, deviceName};
    }

    browseBtn.addEventListener('click', async () => {
        const host = hostInput.value.trim();
        if (!host) {
            output.innerHTML = '<span style="color:#ffb3b3">Please enter a hostname.</span>';
            return;
        }

        output.innerHTML = '<em>Resolving ' + host + '...</em>';

        try {
            const {labId, deviceName} = _parsePath();

            const res = await fetch(`/api/lab/${labId}/pc/${deviceName}/browse`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({host})
            });

            // If the server redirected to login/html, try to parse safely
            const data = await res.json().catch(() => ({success:false, error: 'Invalid response'}));
            if (data.success) {
                output.innerHTML = data.content || '<em>(no content returned)</em>';
            } else {
                output.innerHTML = '<span style="color:#ffb3b3">Error: ' + (data.error || 'Unknown') + '</span>';
            }
        } catch (e) {
            output.innerHTML = '<span style="color:#ffb3b3">Request failed: ' + e.message + '</span>';
        }
    });

    // Add DNS mapping handler
    addDnsBtn.addEventListener('click', async (ev) => {
        ev.preventDefault();
        dnsMessage.textContent = '';
        const host = dnsHostInput.value.trim();
        const response = dnsResponseInput.value.trim();
        if (!host) { dnsMessage.textContent = 'Host required'; return; }

        try {
            const {labId} = _parsePath();
            const res = await fetch(`/api/lab/${labId}/dns`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({host, response})
            });
            const data = await res.json().catch(() => ({success:false, error:'Invalid response'}));
            if (data.success) {
                dnsMessage.style.color = '#b3ffb3';
                dnsMessage.textContent = 'DNS entry added';
            } else {
                dnsMessage.style.color = '#ffb3b3';
                dnsMessage.textContent = data.error || 'Failed to add DNS entry';
            }
        } catch (e) {
            dnsMessage.style.color = '#ffb3b3';
            dnsMessage.textContent = 'Request failed: ' + e.message;
        }
    });
});