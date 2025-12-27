document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('device-config-modal');
    const closeBtn = document.getElementById('device-config-close');
    const saveBtn = document.getElementById('save-device-config');
    const addIfBtn = document.getElementById('add-interface');
    const interfacesList = document.getElementById('interfaces-list');
    const hostnameInput = document.getElementById('dev-hostname');

    let current = { labId: null, device: null, interfaces: [] };

    function openModal() { modal.style.display = 'block'; }
    function closeModal() { modal.style.display = 'none'; }

    function renderInterfaces() {
        interfacesList.innerHTML = '';
        current.interfaces.forEach((it, idx) => {
            const row = document.createElement('div');
            row.style.display = 'flex'; row.style.flexDirection = 'column'; row.style.gap='6px'; row.style.marginBottom='8px';
            row.innerHTML = `
                <div style="display:flex;gap:8px;">
                    <input class="form-control iface-name" data-idx="${idx}" placeholder="name (e.g. Gig0/0)" value="${it.name||''}" style="width:30%">
                    <input class="form-control iface-ip" data-idx="${idx}" placeholder="IP (e.g. 192.168.1.1 or 192.168.1.1/24)" value="${it.ip||''}" style="width:45%">
                    <button class="btn btn-sm btn-danger iface-del" data-idx="${idx}">Delete</button>
                </div>
                <div class="iface-error" data-idx="${idx}" style="color:#ff6b6b;font-size:12px;min-height:16px;"></div>
            `;
            interfacesList.appendChild(row);
        });
        // attach listeners for validation
        document.querySelectorAll('.iface-name, .iface-ip').forEach(inp=>{
            inp.addEventListener('input', (ev)=>{ validateAll(); });
        });
        document.querySelectorAll('.iface-del').forEach(btn=>{
            btn.addEventListener('click', (ev)=>{ const idx=Number(btn.dataset.idx); current.interfaces.splice(idx,1); renderInterfaces(); validateAll(); });
        });
    }

    function addInterfaceRow() {
        current.interfaces.push({name:'', ip:''});
        renderInterfaces();
        validateAll();
    }

    function validateIpValue(val) {
        const v = (val||'').trim();
        if (!v) return {ok:true};
        // IPv4 or IPv4/CIDR (0-32)
        const m = v.match(/^\s*(\d{1,3}(?:\.\d{1,3}){3})(?:\/(\d|[12]\d|3[0-2]))?\s*$/);
        if (!m) return {ok:false, msg:'Invalid IP format'};
        // validate octet ranges
        const parts = m[1].split('.').map(Number);
        for (let p of parts) { if (p<0 || p>255) return {ok:false, msg:'IP octet out of range'} }
        return {ok:true};
    }

    function validateAll() {
        let invalid = false;
        document.querySelectorAll('.iface-ip').forEach(inp=>{
            const idx = Number(inp.dataset.idx);
            const val = inp.value.trim();
            const res = validateIpValue(val);
            const errEl = document.querySelector(`.iface-error[data-idx="${idx}"]`);
            if (!res.ok) { invalid = true; inp.style.border='1px solid #ff6b6b'; errEl.textContent = res.msg; }
            else { inp.style.border=''; errEl.textContent = ''; }
        });
        // ensure names not empty
        document.querySelectorAll('.iface-name').forEach(inp=>{
            const idx = Number(inp.dataset.idx);
            const val = inp.value.trim();
            const errEl = document.querySelector(`.iface-error[data-idx="${idx}"]`);
            if (!val) { invalid = true; inp.style.border='1px solid #ff6b6b'; errEl.textContent = 'Interface name required'; }
            else if (!errEl.textContent) { inp.style.border=''; }
        });
        saveBtn.disabled = invalid;
    }

    // open config for a device
    window.openDeviceConfig = async function(labId, deviceName) {
        current.labId = labId; current.device = deviceName; current.interfaces = [];
        try {
            const res = await fetch(`/api/lab/${labId}/device/${deviceName}/config` , {credentials:'same-origin'});
            const data = await res.json();
            hostnameInput.value = data.hostname || deviceName;
            current.interfaces = data.interfaces || [];
            renderInterfaces();
            openModal();
        } catch (e) {
            alert('Failed to load device config: ' + e.message);
        }
    }

    // bind config buttons (works for initial render)
    document.querySelectorAll('.config-btn').forEach(btn=>{
        btn.addEventListener('click', function(ev){
            ev.stopPropagation(); // prevent device-item click from switching tabs
            const dev = this.dataset.device;
            const labId = document.querySelector('.terminal-input')?.dataset?.labId || 1;
            openDeviceConfig(labId, dev);
        });
    });

    closeBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); closeModal(); });

    addIfBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); addInterfaceRow(); });

    interfacesList.addEventListener('click', (ev)=>{
        if (ev.target.classList.contains('iface-del')) {
            const idx = Number(ev.target.dataset.idx);
            current.interfaces.splice(idx,1);
            renderInterfaces();
        }
    });

    // save handler with validation
    saveBtn.addEventListener('click', async (ev)=>{
        ev.preventDefault();
        // collect rows
        document.querySelectorAll('.iface-name').forEach(inp=>{ const i = Number(inp.dataset.idx); current.interfaces[i].name = inp.value.trim(); });
        document.querySelectorAll('.iface-ip').forEach(inp=>{ const i = Number(inp.dataset.idx); current.interfaces[i].ip = inp.value.trim(); });
        // validation: IP/mask must be empty or IPv4 with optional /CIDR
        const ipRegex = /^$|^\s*(?:\d{1,3}(?:\.\d{1,3}){3})(?:\/([0-9]|[12][0-9]|3[0-2]))?\s*$/;
        let invalid = false;
        document.querySelectorAll('.iface-ip').forEach(inp=>{
            if (!ipRegex.test(inp.value.trim())) {
                invalid = true; inp.style.border = '1px solid #ff6b6b';
            } else { inp.style.border = ''; }
        });
        if (invalid) { alert('One or more interface IPs are invalid. Use format 192.168.1.1 or 192.168.1.1/24'); return; }

        const payload = { hostname: hostnameInput.value.trim(), interfaces: current.interfaces };
        try {
            const res = await fetch(`/api/lab/${current.labId}/device/${current.device}/config`, {
                method: 'POST', credentials:'same-origin', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                alert('Device config saved'); closeModal();
            } else {
                alert('Save failed: ' + (data.error||'unknown'));
            }
        } catch (e) {
            alert('Save failed: ' + e.message);
        }
    });

});