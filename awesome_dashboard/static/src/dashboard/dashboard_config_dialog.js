/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { CheckBox } from "@web/core/checkbox/checkbox";

export class DashboardConfigurationDialog extends Component {
  static template = "awesome_dashboard.DashboardConfigurationDialog";
  static components = { Dialog, CheckBox };
  static props = {
    close: Function,
    items: Array,
    disabledItems: Array,
    onApply: Function,
  };

  setup() {
    this.items = this.props.items.map((item) => {
      return {
        ...item,
        isEnabled: !this.props.disabledItems.includes(item.id),
      };
    });
    this.state = useState({ items: this.items });
  }

  onApply() {
    const disabledItems = this.state.items
      .filter((i) => !i.isEnabled)
      .map((i) => i.id);
    this.props.onApply(disabledItems);
    this.props.close();
  }
}
