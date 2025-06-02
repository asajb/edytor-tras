export {};

declare global {
    interface Window {
        SSE_URL: string;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const evtSource = new EventSource(window.SSE_URL);
    const toastContainer = createToastContainer();

    evtSource.addEventListener('open', () => {
        console.log('Connection to server opened. SSE');
    });

    evtSource.addEventListener('error', (err: any) => {
        console.error('SSE failed:', err);
    });

    evtSource.addEventListener('newBoard', (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        console.log('New board event received:', data);
        showToast(`Użytkownik ${data.creator_username} utworzył nową planszę: ${data.board_name}`);
    });

    evtSource.addEventListener('newPathsOnBoard', (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        console.log('New path event received:', data);
        showToast(`Użytkownik ${data.user_username} zapisał ścieżkę na planszy: ${data.board_name}`);
    });

    function createToastContainer(): HTMLElement {
        let c = document.getElementById('toast-container');
        if (!c) {
            c = document.createElement('div');
            c.id = 'toast-container';
            Object.assign(c.style, {
                position: 'fixed',
                top: '1rem', right: '1rem',
                display: 'flex', flexDirection: 'column',
                gap: '0.5rem', zIndex: '9999'
            });
            document.body.appendChild(c);
        }
        return c;
    }

    function showToast(text: string, type: 'info' | 'error' = 'info') {
        const t = document.createElement('div');
        t.textContent = text;
        Object.assign(t.style, {
            padding: '0.75rem 1rem',
            background: type === 'error' ? '#c00' : '#333',
            color: '#fff',
            borderRadius: '4px',
            opacity: '0',
            transition: 'opacity 0.3s ease'
        });
        toastContainer.appendChild(t);

        requestAnimationFrame(() => {
            t.style.opacity = '1';
        });

        setTimeout(() => {
            t.style.opacity = '0';
            t.addEventListener('transitionend', () => {
                toastContainer.removeChild(t);
            });
        }, 3000);
    }
});