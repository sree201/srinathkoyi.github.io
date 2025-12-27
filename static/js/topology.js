// topology.js - renders topology for a lab using vis-network

function initTopology(labId) {
    const topoDiv = document.getElementById('topology');
    const refreshBtn = document.getElementById('refresh-topology');
    const saveBtn = document.getElementById('save-topology');

    async function loadAndRender() {
        topoDiv.innerHTML = '<div style="color:#9fb3c9;padding:18px;">Loading topology...</div>';
        try {
            const res = await fetch(`/api/lab/${labId}/topology`, {credentials: 'same-origin'});
            const data = await res.json();

            // Map nodes with styling per group (router/switch/pc)
            const nodes = new vis.DataSet(data.nodes.map(n => ({
                id: n.id,
                label: n.label,
                title: n.title,
                group: n.group,
                color: getColorForGroup(n.group),
                shape: getShapeForGroup(n.group),
                font: { color: '#ffffff' }
            })));
            const edges = new vis.DataSet(data.edges.map((e,i) => ({
                id: e.id || `${e.from}-${e.to}-${i}`,
                from: e.from,
                to: e.to,
                label: e.label || '',
                cost: e.cost || 1,
                src_if: e.src_if || null,
                dst_if: e.dst_if || null,
                title: (e.src_if && e.dst_if) ? `${e.src_if} ↔ ${e.dst_if}` : (e.label || ''),
                font: { align: 'top' }
            })));


            const container = topoDiv;
            const networkData = {nodes, edges};
            const options = {
                layout: { improvedLayout: true },
                nodes: { margin: 12 },
                edges: { color: '#8aa4b6', arrows: { to: {enabled: false} }, smooth: { type: 'cubicBezier' } },
                physics: { enabled: true, stabilization: true },
                interaction: { hover: true, multiselect: true },
                manipulation: {
                    enabled: false, // disabled by default; toggle with Edit
                    addNode: false,
                    editNode: false,
                    addEdge: function (data, callback) { callback(data); },
                    editEdge: false,
                    deleteNode: false,
                    deleteEdge: function (data, callback) { callback(data); }
                }
            };

            // Clean previous network if exists
            if (window._ccna_network && typeof window._ccna_network.destroy === 'function') {
                try { window._ccna_network.destroy(); } catch(e) {}
            }

            window._ccna_network = new vis.Network(container, networkData, options);

            // Apply saved positions if present (but keep nodes movable while in Edit mode)
            if (data.positions) {
                try {
                    Object.keys(data.positions).forEach(id => {
                        const p = data.positions[id];
                        try { window._ccna_network.moveNode(id, p.x, p.y); } catch(e) {}
                        // leave nodes unlocked by default
                        nodes.update({id: id, fixed: {x: false, y: false}});
                    });
                } catch (e) {
                    // ignore
                }
            }

            // Node click -> open terminal or browser for PC
            window._ccna_network.on('click', function(params) {
                if (params.nodes && params.nodes.length > 0) {
                    const deviceName = params.nodes[0];
                    const tab = document.querySelector(`.terminal-tab[data-device="${deviceName}"]`);
                    if (tab) tab.click();
                    else {
                        const link = document.querySelector(`.device-item[data-device="${deviceName}"] a`);
                        if (link) link.click();
                    }
                }
            });

            // Double click -> edit link or open device configuration modal (if available)
            window._ccna_network.on('doubleClick', function(params) {
                if (params.edges && params.edges.length > 0) {
                    const edgeId = params.edges[0];
                    const edgeObj = window._ccna_network.body.data.edges.get(edgeId);
                    openLinkModal(edgeObj.from, edgeObj.to, edgeObj);
                    return;
                }
                if (params.nodes && params.nodes.length > 0) {
                    const deviceName = params.nodes[0];
                    if (typeof window.openDeviceConfig === 'function') {
                        window.openDeviceConfig(labId, deviceName);
                    }
                }
            });
        } catch (e) {
            topoDiv.innerHTML = '<div style="color:#ffb3b3;padding:18px;">Failed to load topology: ' + e.message + '</div>';
        }
    }

    // Save topology edges and node positions (persist to backend)
    async function saveTopology() {
        if (!window._ccna_network) return;
        const edges = window._ccna_network.body.data.edges.get();
        const payloadEdges = edges.map(e => ({from: e.from, to: e.to, label: e.label || '', cost: e.cost || 1, src_if: e.src_if || null, dst_if: e.dst_if || null}));
        // get node positions
        const positionsRaw = window._ccna_network.getPositions(); // {id: {x,y}}
        try {
            const res = await fetch(`/api/lab/${labId}/topology`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({edges: payloadEdges, positions: positionsRaw})
            });
            const data = await res.json();
            if (data.success) {
                alert('Topology saved');
                loadAndRender();
            } else {
                alert('Failed to save topology: ' + (data.error || 'unknown'));
            }
        } catch (e) {
            alert('Save failed: ' + e.message);
        }
    }

    // Custom toolbar behaviors: Add/Delete/Reset
    const addBtn = document.getElementById('add-link');
    const delBtn = document.getElementById('delete-link');
    const resetBtn = document.getElementById('reset-layout');

    let mode = null; // 'add' | 'delete' | null
    let addSelection = [];
    let pendingEdge = null;

    const linkModal = document.getElementById('link-config-modal');
    const linkClose = document.getElementById('link-config-close');
    const linkSave = document.getElementById('save-link-config');
    const linkSrc = document.getElementById('link-src');
    const linkDst = document.getElementById('link-dst');
    const linkSrcIf = document.getElementById('link-src-if');
    const linkDstIf = document.getElementById('link-dst-if');
    const linkLabel = document.getElementById('link-label');
    const linkCost = document.getElementById('link-cost');

    function openLinkModal(src, dst, existing) {
        linkSrc.value = src; linkDst.value = dst; linkLabel.value = existing?.label || '';
        linkCost.value = existing?.cost || 1;
        // populate interface selects from device configs
        Promise.all([
            fetch(`/api/lab/${labId}/device/${src}/config`, {credentials:'same-origin'}).then(r=>r.json()),
            fetch(`/api/lab/${labId}/device/${dst}/config`, {credentials:'same-origin'}).then(r=>r.json())
        ]).then(([srcData, dstData]) => {
            linkSrcIf.innerHTML = '';
            linkDstIf.innerHTML = '';
            (srcData.interfaces || []).forEach(it => { const opt = document.createElement('option'); opt.value = it.name || it.ifname || ''; opt.textContent = it.name + (it.ip ? (' — ' + it.ip) : ''); linkSrcIf.appendChild(opt); });
            (dstData.interfaces || []).forEach(it => { const opt = document.createElement('option'); opt.value = it.name || it.ifname || ''; opt.textContent = it.name + (it.ip ? (' — ' + it.ip) : ''); linkDstIf.appendChild(opt); });
            // set selected if existing present
            if (existing) { if (existing.src_if) linkSrcIf.value = existing.src_if; if (existing.dst_if) linkDstIf.value = existing.dst_if; }
            linkModal.style.display = 'block';
        }).catch(e => { alert('Failed to fetch device interfaces: ' + e.message); });
    }

    function closeLinkModal() { linkModal.style.display = 'none'; }

    // network interactions
    window._ccna_network.on('click', function(params) {
        if (mode === 'add') {
            if (params.nodes && params.nodes.length > 0) {
                const node = params.nodes[0];
                if (!addSelection.includes(node)) addSelection.push(node);
                if (addSelection.length === 2) {
                    // open configuration modal for new edge
                    openLinkModal(addSelection[0], addSelection[1], null);
                    // reset selection
                    addSelection = [];
                    mode = null;
                    addBtn.classList.remove('active');
                }
            }
            return;
        }
        if (mode === 'delete') {
            if (params.edges && params.edges.length > 0) {
                const edgeId = params.edges[0];
                if (confirm('Delete selected link?')) {
                    try { window._ccna_network.body.data.edges.remove(edgeId); } catch(e){}
                    saveTopology();
                    mode = null; delBtn.classList.remove('active');
                }
            } else {
                alert('Click on an existing link to delete it');
            }
            return;
        }

        // default click behavior (open terminal)
        if (params.nodes && params.nodes.length > 0) {
            const deviceName = params.nodes[0];
            const tab = document.querySelector(`.terminal-tab[data-device="${deviceName}"]`);
            if (tab) tab.click();
            else {
                const link = document.querySelector(`.device-item[data-device="${deviceName}"] a`);
                if (link) link.click();
            }
        }
    });

    addBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); mode = 'add'; addSelection = []; addBtn.classList.add('active'); delBtn.classList.remove('active'); });
    delBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); mode = 'delete'; delBtn.classList.add('active'); addBtn.classList.remove('active'); });
    resetBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); if (!window._ccna_network) return; window._ccna_network.fit(); // clear saved positions by saving empty positions
        (async ()=>{ try { const res = await fetch(`/api/lab/${labId}/topology`, {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({edges: window._ccna_network.body.data.edges.get(), positions: {}})}); const d = await res.json(); if (d.success) alert('Layout reset'); else alert('Reset failed'); } catch(e){ alert('Reset failed: '+e.message); } })(); });

    linkClose.addEventListener('click', (ev)=>{ ev.preventDefault(); closeLinkModal(); });

    linkSave.addEventListener('click', (ev)=>{
        ev.preventDefault();
        const src = linkSrc.value, dst = linkDst.value;
        const src_if = linkSrcIf.value || null, dst_if = linkDstIf.value || null;
        const labelVal = (linkLabel.value || '').trim();
        const costVal = parseInt(linkCost.value) || 1;
        // add edge to network
        try {
            window._ccna_network.body.data.edges.add({from: src, to: dst, label: labelVal, cost: costVal, src_if: src_if, dst_if: dst_if, font:{align:'top'}});
            saveTopology();
            closeLinkModal();
        } catch (e) { alert('Failed to add link: ' + e.message); }
    });

    // disable vis default manipulation UI (we use custom toolbar)
    if (window._ccna_network) window._ccna_network.setOptions({manipulation:{enabled:false}});

    refreshBtn.addEventListener('click', (ev) => { ev.preventDefault(); loadAndRender(); });
    saveBtn.addEventListener('click', (ev) => { ev.preventDefault(); saveTopology(); });

    loadAndRender();
}


function getColorForGroup(group) {
    switch ((group||'').toLowerCase()) {
        case 'router': return {background:'#ff7f50', border:'#ff6b3a', highlight:{background:'#ff8f60'}};
        case 'switch': return {background:'#6fa3ff', border:'#4e86f0', highlight:{background:'#85b8ff'}};
        case 'pc': return {background:'#7be495', border:'#5fd07a', highlight:{background:'#8cf5a0'}};
        default: return {background:'#9fb3c9', border:'#7fa0b3', highlight:{background:'#b3cde0'}};
    }
}

function getShapeForGroup(group) {
    switch ((group||'').toLowerCase()) {
        case 'router': return 'triangle';
        case 'switch': return 'box';
        case 'pc': return 'ellipse';
        default: return 'box';
    }
}
