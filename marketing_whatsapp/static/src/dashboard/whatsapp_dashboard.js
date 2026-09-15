/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useState, useRef } from "@odoo/owl";

export class WhatsappDashboard extends Component {
    static template = "marketing_whatsapp.WhatsappDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.chartCanvasRef = useRef("chartCanvas");
        this.chartInstance = null;

        this.state = useState({
            loading: true,
            period: "all",
            metrics: {
                total_contacts: 0,
                contacts_with_whatsapp: 0,
                contacts_sent: 0,
                contacts_delivered: 0,
                contacts_read: 0,
                contacts_replied: 0,
                contacts_not_sent: 0,
                total_traces: 0,
                sent_traces: 0,
                delivered_traces: 0,
                read_traces: 0,
                failed_traces: 0,
                delivery_rate: 100.0,
                read_rate: 0.0,
                reply_rate: 0.0,
                fail_rate: 0.0,
                total_lists: 0,
                total_templates: 0,
                total_campaigns: 0,
            },
            subscription: {
                has_subscription: false,
                plan_name: "Plano Enterprise",
                messages_limit: 50000,
                messages_sent: 0,
                messages_remaining: 50000,
                usage_percentage: 0,
            },
            account: {
                has_account: true,
                name: "Simplexo Tecnologia",
                phone_number: "+55 11 5028-8495",
                status: "connected",
                quality_rating: "GREEN",
                daily_limit: 1000,
                pacing_rate: "125 msgs/hora",
            },
            campaigns: [],
            recent_replies: [],
            chart: {
                labels: [],
                sent: [],
                delivered: [],
                read: [],
                replied: [],
            }
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.renderChart();
        });
    }

    async loadDashboardData(period = this.state.period) {
        this.state.loading = true;
        this.state.period = period;
        try {
            const data = await this.orm.call("whatsapp.dashboard", "get_dashboard_data", [], { period });
            if (data) {
                this.state.metrics = data.metrics || this.state.metrics;
                this.state.subscription = data.subscription || this.state.subscription;
                this.state.account = data.account || this.state.account;
                this.state.campaigns = data.campaigns || [];
                this.state.recent_replies = data.recent_replies || [];
                this.state.chart = data.chart || this.state.chart;
            }
        } catch (error) {
            console.error("Erro ao carregar métricas do Dashboard WhatsApp:", error);
            this.notification.add("Erro ao carregar dados do Dashboard", { type: "danger" });
        } finally {
            this.state.loading = false;
            setTimeout(() => this.renderChart(), 100);
        }
    }

    async onPeriodChange(period) {
        await this.loadDashboardData(period);
    }

    renderChart() {
        if (!this.chartCanvasRef.el || !window.Chart) {
            return;
        }

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = this.chartCanvasRef.el.getContext("2d");
        const chartData = this.state.chart;

        this.chartInstance = new window.Chart(ctx, {
            type: "line",
            data: {
                labels: chartData.labels || ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
                datasets: [
                    {
                        label: "Enviados",
                        data: chartData.sent || [0, 0, 0, 0, 0, 0, 0],
                        borderColor: "#25D366",
                        backgroundColor: "rgba(37, 211, 102, 0.15)",
                        borderWidth: 3,
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Visualizados",
                        data: chartData.read || [0, 0, 0, 0, 0, 0, 0],
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59, 130, 246, 0.1)",
                        borderWidth: 2,
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    },
                    {
                        label: "Respondidos",
                        data: chartData.replied || [0, 0, 0, 0, 0, 0, 0],
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        borderWidth: 2,
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            font: { family: "Inter, sans-serif", size: 12, weight: 600 },
                            usePointStyle: true,
                            padding: 15,
                        }
                    },
                    tooltip: {
                        backgroundColor: "rgba(15, 23, 42, 0.9)",
                        titleFont: { size: 13, weight: 700 },
                        bodyFont: { size: 12 },
                        padding: 10,
                        cornerRadius: 8,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: "Inter, sans-serif", size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: "rgba(226, 232, 240, 0.6)" },
                        ticks: { font: { family: "Inter, sans-serif", size: 11 } }
                    }
                }
            }
        });
    }

    // Ações de Navegação
    openNewCampaign() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mailing.mailing",
            views: [[false, "form"]],
            target: "current",
            context: { default_mailing_type: "whatsapp" },
        });
    }

    openCampaign(campaignId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mailing.mailing",
            res_id: campaignId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openContacts(filter = false) {
        const context = {};
        if (filter === "sent") context.search_default_filter_wa_sent = 1;
        if (filter === "read") context.search_default_filter_wa_read = 1;
        if (filter === "replied") context.search_default_filter_wa_replied = 1;
        if (filter === "not_sent") context.search_default_filter_wa_not_sent = 1;

        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Contatos de WhatsApp",
            res_model: "mailing.contact",
            views: [[false, "list"], [false, "form"]],
            target: "current",
            context: context,
        });
    }

    openContactForm(contactId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mailing.contact",
            res_id: contactId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openLists() {
        this.action.doAction("mass_mailing.action_view_mass_mailing_lists");
    }

    openTemplates() {
        this.action.doAction("marketing_whatsapp.action_whatsapp_template_tree");
    }

    openImportWizard() {
        this.action.doAction("marketing_whatsapp.action_wizard_import_whatsapp_contacts");
    }

    openSettings() {
        this.action.doAction("marketing_whatsapp.action_whatsapp_configuration");
    }

    openSubscriptions() {
        this.action.doAction("marketing_whatsapp.action_whatsapp_subscription");
    }
}

registry.category("actions").add("whatsapp_dashboard_tag", WhatsappDashboard);
