import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addTodoRequest, deleteTodoRequest, todosRequest } from "../requests";
import { toast } from "sonner";

/**
 * Hook pour la récupération des todos
 *
 * Gère le processus de récupération des todos
 * avec notifications de succès/erreur
 */
export function useTodosQuery() {
    return useQuery({
        queryFn: async () => {
            return await todosRequest();
        },
        queryKey: ["todos"],
    });
}

export function useAddTodoMutation() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (text: string) => addTodoRequest({ text }),
        onSuccess: () => {
            toast.success("Todo added successfully");
            queryClient.invalidateQueries({ queryKey: ["todos"] });
        },
    });
}

export function useDeleteTodoMutation() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => deleteTodoRequest(id),
        onSuccess: () => {
            toast.success("Todo deleted successfully");
            queryClient.invalidateQueries({ queryKey: ["todos"] });
        },
    });
}
