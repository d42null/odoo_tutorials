/** @odoo-module */

import { registry } from "@web/core/registry";
import { NumberCard } from "./number_card";
import { PieChartCard } from "./pie_chart_card";

const dashboard_registry = registry.category("awesome_dashboard");

dashboard_registry.add("nb_new_orders", {
  id: "nb_new_orders",
  description: "Number of new orders",
  Component: NumberCard,
  props: (data) => ({
    title: "New Orders",
    value: data.nb_new_orders,
  }),
});

dashboard_registry.add("total_amount", {
  id: "total_amount",
  description: "Total amount of new orders",
  Component: NumberCard,
  props: (data) => ({
    title: "Total Amount",
    value: data.total_amount,
  }),
});

dashboard_registry.add("average_quantity", {
  id: "average_quantity",
  description: "Average quantity by order",
  Component: NumberCard,
  props: (data) => ({
    title: "Avg Quantity",
    value: data.average_quantity,
  }),
});

dashboard_registry.add("nb_cancelled_orders", {
  id: "nb_cancelled_orders",
  description: "Number of cancelled orders",
  Component: NumberCard,
  props: (data) => ({
    title: "Cancelled Orders",
    value: data.nb_cancelled_orders,
  }),
});

dashboard_registry.add("average_time", {
  id: "average_time",
  description: "Average time to sent",
  Component: NumberCard,
  props: (data) => ({
    title: "Avg Time to Sent",
    value: data.average_time + "h",
  }),
});

dashboard_registry.add("orders_by_size", {
  id: "orders_by_size",
  description: "Orders by size",
  Component: PieChartCard,
  size: 2,
  props: (data) => ({
    title: "Orders by Size",
    data: data.orders_by_size,
  }),
});
