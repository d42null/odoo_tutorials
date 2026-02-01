/** @odoo-module */

import {
  Component,
  onMounted,
  onWillStart,
  onWillUnmount,
  useRef,
} from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
  static template = "awesome_dashboard.PieChart";
  static props = {
    data: { type: Object },
    label: { type: String },
  };

  setup() {
    this.canvasRef = useRef("canvas");
    this.chart = null;

    onWillStart(async () => {
      await loadJS("/web/static/lib/Chart/Chart.js");
    });

    onMounted(() => {
      const config = {
        type: "pie",
        data: {
          labels: Object.keys(this.props.data),
          datasets: [
            {
              label: this.props.label,
              data: Object.values(this.props.data),
            },
          ],
        },
      };
      this.chart = new Chart(this.canvasRef.el, config);
    });

    onWillUnmount(() => {
      if (this.chart) {
        this.chart.destroy();
      }
    });
  }
}
