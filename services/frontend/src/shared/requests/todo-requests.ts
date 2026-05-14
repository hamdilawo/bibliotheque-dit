import { handleHttpRequest } from "@/lib/http-client";

/**
 * Requête de récupération des todos
 */
export function todosRequest() {
    return handleHttpRequest({
        method: "GET",
        endpoint: "/api/todos",
    });
}

export function addTodoRequest(payload: { text: string }) {
    return handleHttpRequest({
        method: "POST",
        endpoint: "/api/todos",
        payload,
    });
}

export function deleteTodoRequest(id: number) {
    return handleHttpRequest({
        method: "DELETE",
        endpoint: `/api/todos/${id}`,
    });
}