import { Skeleton } from '@/shared/components/ui/skeleton'
import { createFileRoute } from '@tanstack/react-router'
import { useAddTodoMutation, useDeleteTodoMutation, useTodosQuery } from '@/shared/hooks/useTodos'
import { Card } from '@/shared/components/ui/card'
import { Input } from '@/shared/components/ui/input'
import { Button } from '@/shared/components/ui/button'
import { Trash2, Plus } from 'lucide-react'
import { useState } from 'react'
import { Trans } from '@lingui/react/macro'

export const Route = createFileRoute('/$lang/todos')({
    component: RouteComponent,
})

function RouteComponent() {
    const { data: todos, isLoading } = useTodosQuery()
    const addTodo = useAddTodoMutation()
    const deleteTodo = useDeleteTodoMutation()
    const [text, setText] = useState('')

    const transformTodos = Array.isArray(todos) ? todos : todos?.data || []

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!text.trim()) return
        await addTodo.mutateAsync(text)
        setText('')
    }

    return (
        <div className="min-h-screen bg-background p-4 sm:p-8">
            <div className="mx-auto max-w-2xl animate-in fade-in zoom-in duration-500">
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                        <Trans>My Tasks</Trans>
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        <Trans>Stay organized and productive</Trans>
                    </p>
                </div>

                <Card className="p-6 backdrop-blur-sm bg-card/50 border shadow-xl">
                    <form onSubmit={handleAdd} className="flex gap-3 mb-6">
                        <Input
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            placeholder="What needs to be done?"
                            className="h-12 bg-background/50 transition-all focus:scale-[1.01]"
                        />
                        <Button
                            type="submit"
                            size="icon"
                            className="h-12 w-12 shrink-0 transition-all hover:scale-105 active:scale-95"
                            disabled={addTodo.isPending || !text.trim()}
                        >
                            <Plus className="h-6 w-6" />
                        </Button>
                    </form>

                    <div className="space-y-3">
                        {isLoading ? (
                            <div className="space-y-3">
                                {[...Array(5)].map((_, i) => (
                                    <div key={i} className="flex items-center justify-between p-4 rounded-xl border bg-background/50">
                                        <div className="flex items-center gap-3">
                                            <Skeleton className="h-5 w-5 rounded-full" />
                                            <Skeleton className="h-4 w-48" />
                                        </div>
                                        <Skeleton className="h-8 w-8 rounded-md" />
                                    </div>
                                ))}
                            </div>
                        ) : transformTodos.length === 0 ? (
                            <div className="py-12 text-center text-muted-foreground border-2 border-dashed rounded-xl">
                                <p className="opacity-50">
                                    <Trans>No tasks yet. Add one above!</Trans>
                                </p>
                            </div>
                        ) : (
                            <div className="flex flex-col gap-3">
                                {transformTodos.map((todo: any) => (
                                    <div
                                        key={todo.id}
                                        className="group flex items-center justify-between p-4 rounded-xl bg-background border hover:border-primary/50 transition-all duration-300 hover:shadow-md animate-in slide-in-from-bottom-2 fade-in fill-mode-backwards"
                                    >
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className={`h-5 w-5 rounded-full border flex items-center justify-center transition-colors ${todo.completed ? 'bg-primary border-primary' : 'border-muted-foreground'}`}>
                                                {todo.completed && <div className="h-2.5 w-2.5 bg-background rounded-full" />}
                                            </div>
                                            <span className={`font-medium truncate transition-all ${todo.completed ? 'text-muted-foreground line-through decoration-primary/50' : 'text-foreground'}`}>
                                                {todo.title}
                                            </span>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="text-destructive opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/10"
                                            onClick={() => deleteTodo.mutate(todo.id)}
                                        >
                                            <Trash2 className="h-5 w-5" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </Card>

                <div className="mt-8 text-center text-xs text-muted-foreground opacity-50">
                    <Trans>Powered by TanStack & Bun</Trans>
                </div>
            </div>
        </div>
    )
}
