import { marked } from 'marked';
import { WEBUI_BASE_URL } from '$lib/constants';
import markedKatexExtension from '$lib/utils/marked/katex-extension';

// Configure marked with KaTeX support
marked.use(markedKatexExtension({ throwOnError: false }));

export const getWarningContent = async () => {
    try {
        const response = await fetch(`${WEBUI_BASE_URL}/WARNING.md`);
        if (!response.ok) {
            throw new Error('Failed to load warning content');
        }
        const markdown = await response.text();
        // Convert markdown to HTML
        const html = marked.parse(markdown);
        console.log(html);
        return html;
    } catch (error) {
        console.error('Error loading warning content:', error);
        return '';
    }
};
