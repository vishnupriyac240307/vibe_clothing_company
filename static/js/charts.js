/* Chart.js Visualizations for Dashboard & Factory Analytics */

let dashboardStatusChartInstance = null;
let chartOutputTimelineInstance = null;
let chartOrderStatusInstance = null;
let chartTopProductsInstance = null;
let chartInventoryCategoryInstance = null;
let chartQcDefectsInstance = null;
let chartCustomerSpendInstance = null;

function initDashboardCharts() {
    const ctxStatus = document.getElementById("dashboardStatusChart");
    if (!ctxStatus) return;

    $.get("/api/analytics/charts", function(res) {
        if (res.success && res.order_status) {
            if (dashboardStatusChartInstance) dashboardStatusChartInstance.destroy();

            dashboardStatusChartInstance = new Chart(ctxStatus, {
                type: "doughnut",
                data: {
                    labels: res.order_status.labels,
                    datasets: [{
                        data: res.order_status.values,
                        backgroundColor: ["#f59e0b", "#10b981", "#64748b", "#ef4444"],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom" }
                    }
                }
            });
        }
    });
}

function loadAnalyticsPageCharts(period) {
    $.get("/api/analytics/charts?period=" + period, function(res) {
        if (!res.success) return;

        // 1. Output Timeline Chart
        const ctxOutput = document.getElementById("chartOutputTimeline");
        if (ctxOutput) {
            if (chartOutputTimelineInstance) chartOutputTimelineInstance.destroy();
            chartOutputTimelineInstance = new Chart(ctxOutput, {
                type: "line",
                data: {
                    labels: res.timeline.labels,
                    datasets: [{
                        label: "Units Produced",
                        data: res.timeline.output,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.1)",
                        fill: true,
                        tension: 0.3,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        // 2. Order Status Doughnut Chart
        const ctxOrderStatus = document.getElementById("chartOrderStatus");
        if (ctxOrderStatus) {
            if (chartOrderStatusInstance) chartOrderStatusInstance.destroy();
            chartOrderStatusInstance = new Chart(ctxOrderStatus, {
                type: "doughnut",
                data: {
                    labels: res.order_status.labels,
                    datasets: [{
                        data: res.order_status.values,
                        backgroundColor: ["#f59e0b", "#10b981", "#64748b", "#ef4444"]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "bottom" } }
                }
            });
        }

        // 3. Top Products Bar Chart
        const ctxTopProducts = document.getElementById("chartTopProducts");
        if (ctxTopProducts) {
            if (chartTopProductsInstance) chartTopProductsInstance.destroy();
            chartTopProductsInstance = new Chart(ctxTopProducts, {
                type: "bar",
                data: {
                    labels: res.top_products.labels,
                    datasets: [
                        { label: "Target Qty", data: res.top_products.values, backgroundColor: "#2563eb" },
                        { label: "Available Stock", data: res.top_products.stock, backgroundColor: "#10b981" }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        // 4. Inventory Category Valuation (₹) Bar Chart
        const ctxInvCat = document.getElementById("chartInventoryCategory");
        if (ctxInvCat) {
            if (chartInventoryCategoryInstance) chartInventoryCategoryInstance.destroy();
            chartInventoryCategoryInstance = new Chart(ctxInvCat, {
                type: "bar",
                data: {
                    labels: res.inventory_category.labels,
                    datasets: [{
                        label: "Total Value (₹)",
                        data: res.inventory_category.values,
                        backgroundColor: "#7c3aed"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Valuation: ₹' + context.parsed.y.toLocaleString('en-IN');
                                }
                            }
                        }
                    }
                }
            });
        }

        // 5. QC Defects Breakdown
        const ctxDefects = document.getElementById("chartQcDefects");
        if (ctxDefects) {
            if (chartQcDefectsInstance) chartQcDefectsInstance.destroy();
            chartQcDefectsInstance = new Chart(ctxDefects, {
                type: "pie",
                data: {
                    labels: res.qc_defects.labels,
                    datasets: [{
                        data: res.qc_defects.values,
                        backgroundColor: ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#06b6d4"]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "right" } }
                }
            });
        }

        // 6. Customer Orders & Spend
        const ctxCustSpend = document.getElementById("chartCustomerSpend");
        if (ctxCustSpend) {
            if (chartCustomerSpendInstance) chartCustomerSpendInstance.destroy();
            chartCustomerSpendInstance = new Chart(ctxCustSpend, {
                type: "bar",
                data: {
                    labels: res.customer_orders.labels,
                    datasets: [{
                        label: "Completed Spend (₹)",
                        data: res.customer_orders.spend,
                        backgroundColor: "#0ea5e9"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    });
}
