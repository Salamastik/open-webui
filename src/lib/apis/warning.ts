import { marked } from 'marked';

// Read and parse warning content from WARNING.md
export const readWarningContent = async () => {
    try {
        const response = await fetch('/src/lib/WARNING.md');
        if (!response.ok) {
            throw new Error('Failed to load warning content');
        }
        const markdown = await response.text();
        // Convert markdown to HTML
        const html = marked(markdown);
        return html;
    } catch (error) {
        console.error('Error loading warning content:', error);
        return '';
    }
};
