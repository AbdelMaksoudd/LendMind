// ========================================
// WebSocket Connection & Toast Notifications
// ========================================

function initWebSocket() {
    const toastContainer = document.getElementById('toast-container');
    let ws = null;
    let reconnectTimer = null;

    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/ws';

        ws = new WebSocket(wsUrl);

        ws.onopen = function () {
            console.log('[WS] Connected');
        };

        ws.onmessage = function (event) {
            try {
                const data = JSON.parse(event.data);
                handleEvent(data);
            } catch (e) {
                console.error('[WS] Parse error:', e);
            }
        };

        ws.onclose = function () {
            console.log('[WS] Disconnected, reconnecting in 3s...');
            reconnectTimer = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = function () {
            ws.close();
        };
    }

    function handleEvent(data) {
        if (data.event === 'NEW_APPLICATION') {
            showToast(
                'New Application Received',
                'Application #' + data.id + ' — $' + Number(data.amount).toLocaleString()
            );
            if (window.location.pathname === '/dashboard') {
                setTimeout(function () { location.reload(); }, 1500);
            }
        } else if (data.event === 'STATUS_UPDATE') {
            showToast(
                'Application Updated',
                'Application #' + data.id + ' is now ' + data.status
            );
            var detailPath = '/applications/' + data.id;
            if (window.location.pathname === '/dashboard' || window.location.pathname === detailPath) {
                setTimeout(function () { location.reload(); }, 1500);
            }
        }
    }

    function showToast(title, body) {
        if (!toastContainer) return;
        var toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        toast.innerHTML =
            '<div class="toast-title">' + escapeHtml(title) + '</div>' +
            '<div class="toast-body">' + escapeHtml(body) + '</div>';
        toastContainer.appendChild(toast);
        setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 5000);
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // Auto-connect on dashboard pages
    if (window.location.pathname === '/dashboard' || window.location.pathname === '/apply') {
        connectWebSocket();
    }
};

// ========================================
// Donut Chart (Canvas)
// ========================================

function initChart() {
    var container = document.getElementById('chart-container');
    if (!container) return;

    var approved = parseInt(container.dataset.approved || '0', 10);
    var pending = parseInt(container.dataset.pending || '0', 10);
    var rejected = parseInt(container.dataset.rejected || '0', 10);
    var total = approved + pending + rejected;

    var canvas = document.getElementById('analytics-chart');
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var size = 280;

    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';
    ctx.scale(dpr, dpr);

    var cx = size / 2;
    var cy = size / 2;
    var outerRadius = Math.max(1, (size / 2) - 16);
    var innerRadius = Math.max(1, outerRadius * 0.6);

    if (total === 0) {
        // Draw empty ring
        ctx.beginPath();
        ctx.arc(cx, cy, outerRadius, 0, Math.PI * 2);
        ctx.arc(cx, cy, innerRadius, 0, Math.PI * 2, true);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.fill();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No data yet', cx, cy);
        return;
    }

    var segments = [
        { value: approved, color: '#10b981', label: 'Approved' },
        { value: pending, color: '#f59e0b', label: 'Pending' },
        { value: rejected, color: '#ef4444', label: 'Rejected' },
    ];

    var startAngle = -Math.PI / 2;
    var gap = 0.03; // small gap between segments

    segments.forEach(function (seg) {
        if (seg.value === 0) return;
        var sliceAngle = (seg.value / total) * Math.PI * 2;
        var adjustedStart = startAngle + gap / 2;
        var adjustedEnd = startAngle + sliceAngle - gap / 2;

        if (adjustedEnd <= adjustedStart) {
            startAngle += sliceAngle;
            return;
        }

        ctx.beginPath();
        ctx.arc(cx, cy, outerRadius, adjustedStart, adjustedEnd);
        ctx.arc(cx, cy, innerRadius, adjustedEnd, adjustedStart, true);
        ctx.closePath();
        ctx.fillStyle = seg.color;
        ctx.fill();

        startAngle += sliceAngle;
    });

    // Center text
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = 'bold 28px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total.toString(), cx, cy - 8);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillText('Total', cx, cy + 14);
}


initWebSocket();
document.addEventListener("DOMContentLoaded", initChart);