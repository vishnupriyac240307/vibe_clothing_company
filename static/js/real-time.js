/* Real-time Notifications & KPI Updates via AJAX Polling */

document.addEventListener("DOMContentLoaded", function() {
    fetchNotifications();
    // Poll notifications every 15 seconds
    setInterval(fetchNotifications, 15000);
});

function markAllNotifsRead(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    $.ajax({
        url: "/api/notifications/mark-read",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({}),
        success: function(res) {
            fetchNotifications();
        }
    });
}

function clearAllNotifs(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    if (confirm("Are you sure you want to clear all notifications?")) {
        $.ajax({
            url: "/api/notifications/delete-all",
            type: "POST",
            success: function(res) {
                const badge = document.getElementById("notifBadge");
                const list = document.getElementById("notifList");
                if (badge) badge.style.display = "none";
                if (list) {
                    list.innerHTML = '<div class="text-center py-4 text-muted small"><i class="fa-regular fa-bell-slash d-block mb-2 fs-5 text-secondary"></i>No notifications</div>';
                }
            }
        });
    }
}

function deleteSingleNotif(e, notifId) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    const item = document.getElementById('notif-item-' + notifId);
    if (item) {
        item.remove();
    }
    $.ajax({
        url: "/api/notifications/delete/" + notifId,
        type: "POST",
        success: function(res) {
            fetchNotifications();
        }
    });
}

function fetchNotifications() {
    $.get("/api/notifications", function(res) {
        if (!res.success) return;

        const badge = document.getElementById("notifBadge");
        const list = document.getElementById("notifList");

        if (badge) {
            if (res.unread_count > 0) {
                badge.style.display = "inline-block";
                badge.innerText = res.unread_count;
            } else {
                badge.style.display = "none";
            }
        }

        if (list) {
            if (!res.notifications || res.notifications.length === 0) {
                list.innerHTML = '<div class="text-center py-4 text-muted small"><i class="fa-regular fa-bell-slash d-block mb-2 fs-5 text-secondary"></i>No notifications</div>';
                return;
            }

            let html = "";
            res.notifications.forEach(function(n) {
                let badgeClass = "bg-info";
                if (n.type === "danger") badgeClass = "bg-danger";
                else if (n.type === "warning") badgeClass = "bg-warning text-dark";
                else if (n.type === "success") badgeClass = "bg-success";

                const unreadStyle = !n.is_read ? "background-color: rgba(37, 99, 235, 0.05);" : "";

                html += `
                    <div class="list-group-item p-3 border-bottom position-relative notif-item" id="notif-item-${n.id}" style="${unreadStyle}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="badge ${badgeClass}">${n.type.toUpperCase()}</span>
                            <div class="d-flex align-items-center gap-2">
                                <span class="micro text-muted">${n.created_at}</span>
                                <button type="button" class="btn btn-link text-secondary p-0 border-0" onclick="deleteSingleNotif(event, ${n.id})" title="Delete Notification" style="line-height: 1; text-decoration: none; cursor: pointer;">
                                    <i class="fa-solid fa-trash-can text-danger fs-6"></i>
                                </button>
                            </div>
                        </div>
                        <a href="${n.link}" class="text-decoration-none text-dark d-block">
                            <h6 class="fw-bold mb-1 small">${n.title}</h6>
                            <p class="mb-0 text-muted micro">${n.message}</p>
                        </a>
                    </div>
                `;
            });
            list.innerHTML = html;
        }
    });
}
