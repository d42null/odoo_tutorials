/** @odoo-module **/

import { registry } from "@web/core/registry"
import { routerBus } from "@web/core/browser/router"
import { user } from "@web/core/user"

const { markup } = owl

var personal_channel = 'asterisk_plus_actions_' + user.userId
var common_channel = 'asterisk_plus_actions'

export const pbxActionService = {
    dependencies: ["action", "notification", 'bus_service'],

    start(env, { action, notification, bus_service }) {
        this.action = action
        this.notification = notification

        bus_service.addChannel(personal_channel)
        bus_service.addChannel(common_channel)

        bus_service.subscribe("asterisk_plus_notify", (action) => this.asterisk_plus_handle_notify(action))
        bus_service.subscribe("open_record", (action) => this.asterisk_plus_handle_open_record(action))
        bus_service.subscribe("reload_view", (action) => this.asterisk_plus_handle_reload_view(action))
    },

    asterisk_plus_handle_open_record: function (message) {
        if (!this.action) return
        let action = this.action.currentController.action
        if (action.res_model === 'asterisk_plus.call') {
            this.action.doAction({
                'type': 'ir.actions.act_window',
                'res_model': message.model,
                'target': 'current',
                'res_id': message.res_id,
                'views': [[message.view_id, 'form']],
                'view_mode': 'list,form',
            })
        }
    },

    asterisk_plus_handle_reload_view: function (message) {
        if (!this.action || !this.action.currentController) return
        const action = this.action.currentController.action
        if (action.res_model === message.model) {
            routerBus.trigger("ROUTE_CHANGE")
        }
    },

    asterisk_plus_handle_notify: function ({ title, message, sticky, warning }) {
        if (warning === true)
            this.notification.add(markup(message), { title, sticky, type: 'danger' })
        else
            this.notification.add(markup(message), { title, sticky, type: 'warning' })
    },
}

registry.category("services").add("pbxActionService", pbxActionService)