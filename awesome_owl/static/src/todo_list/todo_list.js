/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
  static template = "awesome_owl.TodoList";
  static components = { TodoItem };

  setup() {
    this.nextId = 0;
    this.state = useState({
      todos: [
        { id: this.nextId++, description: "buy milk", isCompleted: false },
        {
          id: this.nextId++,
          description: "read owl documentation",
          isCompleted: true,
        },
      ],
    });
  }

  addTodo(ev) {
    if (ev.keyCode === 13 && ev.target.value !== "") {
      this.state.todos.push({
        id: this.nextId++,
        description: ev.target.value,
        isCompleted: false,
      });
      ev.target.value = "";
    }
  }

  toggleTodo(todoId) {
    const todo = this.state.todos.find((t) => t.id === todoId);
    if (todo) {
      todo.isCompleted = !todo.isCompleted;
    }
  }

  deleteTodo(todoId) {
    const index = this.state.todos.findIndex((t) => t.id === todoId);
    if (index >= 0) {
      this.state.todos.splice(index, 1);
    }
  }
}
