/** @odoo-module */

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { reactive } from "@odoo/owl";

export const statisticsService = {
  start() {
    const statistics = reactive({});

    async function loadStatistics() {
      const stats = await rpc("/awesome_dashboard/statistics");
      Object.assign(statistics, stats);
    }

    setInterval(loadStatistics, 10000);
    loadStatistics();

    return {
      statistics,
    };
  },
};

registry
  .category("services")
  .add("awesome_dashboard.statistics", statisticsService);
