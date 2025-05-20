let startingDot: {row: number, col: number, color: string} | null = null;
let finishingDot: {row: number, col: number, color: string} | null = null;
let pathPoints: Array<{row: number, col: number, color: string}> = [];
let drawing = false;
let allPaths: Array<{
    starting_dot: typeof startingDot,
    finishing_dot: typeof finishingDot,
    path_points: typeof pathPoints
}> = [];

function resetPath() {
    startingDot = null;
    finishingDot = null;
    pathPoints = [];
    drawing = false;
    // Remove only temporary drawing classes/styles
    document.querySelectorAll('.dot.selected').forEach(e => e.classList.remove('selected'));
    document.querySelectorAll('td.path-cell').forEach(e => {
        e.classList.remove('path-cell');
        (e as HTMLElement).style.backgroundColor = '';
    });
    document.removeEventListener('keydown', handleArrow);

    // Re-render all stored paths
    allPaths.forEach(path => {
        // Mark starting and finishing dots as selected
        const startDot = document.querySelector(`.dot[data-row="${path.starting_dot!.row}"][data-col="${path.starting_dot!.col}"]`);
        const finishDot = document.querySelector(`.dot[data-row="${path.finishing_dot!.row}"][data-col="${path.finishing_dot!.col}"]`);
        if (startDot) startDot.classList.add('selected');
        if (finishDot) finishDot.classList.add('selected');
        // Mark path cells
        path.path_points.forEach(point => {
            const td = document.querySelector(`td[data-row="${point.row}"][data-col="${point.col}"]`);
            if (td) {
                td.classList.add('path-cell');
                (td as HTMLElement).style.backgroundColor = path.starting_dot!.color;
            }
        });
    });
}
function handleArrow(e: KeyboardEvent) {
    if (!drawing || !startingDot) return;
    let last = pathPoints[pathPoints.length - 1];
    let next = { ...last };

    if (e.key === 'ArrowUp') next.row -= 1;
    if (e.key === 'ArrowDown') next.row += 1;
    if (e.key === 'ArrowLeft') next.col -= 1;
    if (e.key === 'ArrowRight') next.col += 1;

    let nextTd = document.querySelector(`td[data-row="${next.row}"][data-col="${next.col}"]`);
    if (!nextTd) return;

    // Already visited in current path
    if (pathPoints.some(p => p.row === next.row && p.col === next.col)) return;

    // Used in previous paths
    if (nextTd.classList.contains('used-path')) {
        alert("You crossed another path! Path cancelled.");
        resetPath();
        return;
    }

    // Is there a dot in this cell?
    let nextDot = nextTd.querySelector('.dot') as HTMLElement | null;
    if (nextDot) {
        const dotColor = nextDot.getAttribute('data-color')!;
        const isSameAsStart = next.row === startingDot.row && next.col === startingDot.col;

        if (!isSameAsStart && dotColor !== startingDot.color) {
            alert("You cannot enter a dot of another color.");
            resetPath();
            return;
        }

        if (dotColor === startingDot.color && !isSameAsStart) {
            finishingDot = {row: next.row, col: next.col, color: dotColor};
            pathPoints.push({row: next.row, col: next.col, color: dotColor});
            nextDot.classList.add('selected');

            allPaths.push({
                starting_dot: startingDot,
                finishing_dot: finishingDot,
                path_points: [...pathPoints],
            });

            // Mark all path cells as used
            pathPoints.forEach(point => {
                const td = document.querySelector(`td[data-row="${point.row}"][data-col="${point.col}"]`);
                if (td) td.classList.add('used-path');
            });

            resetPath();
            alert('Path added! Draw another or submit all.');
            return;
        }
    }

    nextTd.classList.add('path-cell');
    (nextTd as HTMLElement).style.backgroundColor = startingDot.color;
    pathPoints.push({row: next.row, col: next.col, color: startingDot.color});
}


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.dot').forEach(dotElem => {
        dotElem.addEventListener('click', function () {
            if (drawing) return;
            const row = parseInt(dotElem.getAttribute('data-row')!);
            const col = parseInt(dotElem.getAttribute('data-col')!);
            const color = dotElem.getAttribute('data-color')!;

            // Check if this dot is already used as a starting or finishing dot
            const alreadyUsed = allPaths.some(path =>
                (path.starting_dot!.row === row && path.starting_dot!.col === col) ||
                (path.finishing_dot!.row === row && path.finishing_dot!.col === col)
            );

            if (alreadyUsed) {
                alert("This dot has already been used.");
                return;
            }

            startingDot = {row, col, color};
            pathPoints = [{row, col, color}];
            dotElem.classList.add('selected');
            const parentTd = dotElem.closest('td');
            if (parentTd) {
                parentTd.classList.add('path-cell');
                (parentTd as HTMLElement).style.backgroundColor = color;
            }
            drawing = true;
            document.addEventListener('keydown', handleArrow);
        });
    });

    // Add submit button handler
    const submitBtn = document.getElementById('submit-paths');
    if (submitBtn) {
        submitBtn.addEventListener('click', function () {
            sendAllPaths();
        });
    }
});

function sendAllPaths() {
    if (allPaths.length === 0) {
        alert('No paths to submit!');
        return;
    }
    fetch(window.location.pathname, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            paths: allPaths,
        }),
    })
    .then(response => response.json())
    .then(data => {
        alert('All paths submitted!');
        window.location.reload();
    });
}

function getCSRFToken(): string {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
    }
    return '';
}