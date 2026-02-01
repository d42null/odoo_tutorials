/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item/dashboard_item";
import { DashboardConfigurationDialog } from "./dashboard_config_dialog";
import { browser } from "@web/core/browser/browser";
import "./dashboard_items";

class AwesomeDashboard extends Component {
  static template = "awesome_dashboard.AwesomeDashboard";
  static components = { Layout, DashboardItem };

  setup() {
    this.action = useService("action");
    this.dialog = useService("dialog");
    this.statisticsService = useService("awesome_dashboard.statistics");
    this.statistics = useState(this.statisticsService.statistics);

    const disabledItems = JSON.parse(
      browser.localStorage.getItem("dashboard.disabled_items") || "[]"
    );
    this.state = useState({ disabledItems });

    this.display = {
      controlPanel: { "top-right": false, "bottom-right": false },
    };
  }

  get items() {
    return registry
      .category("awesome_dashboard")
      .getAll()
      .filter((item) => !this.state.disabledItems.includes(item.id));
  }

  openConfiguration() {
    this.dialog.add(DashboardConfigurationDialog, {
      items: registry.category("awesome_dashboard").getAll(),
      disabledItems: this.state.disabledItems,
      onApply: (disabledItems) => {
        this.state.disabledItems = disabledItems;
        browser.localStorage.setItem(
          "dashboard.disabled_items",
          JSON.stringify(disabledItems)
        );
      },
    });
  }

  openCustomers() {
    this.action.doAction("base.action_partner_form");
  }

  openLeads() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Leads",
      res_model: "crm.lead",
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }
}

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
