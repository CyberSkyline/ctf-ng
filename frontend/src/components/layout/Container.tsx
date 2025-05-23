/**
 * Base container for application content that ensures a maximum width for readability on larger screens.
 */
export default function Container({ children }: { children: React.ReactNode }) {
    return (
        <main className="w-full max-w-6xl mx-auto px-4 py-16  text-gray-600 dark:text-gray-400">
            {children}
        </main>
    );
}