document.addEventListener("DOMContentLoaded", function () {
    const gridTable = document.querySelector("table.grid");
    const defaultColorSelect = document.getElementById("default-color");
    const formsetTableBody = document.getElementById("formset-table-body");
    const emptyFormDiv = document.getElementById("empty-form");
    const totalFormsInput = document.querySelector('input[name="form-TOTAL_FORMS"]');
    if (!gridTable || !defaultColorSelect || !formsetTableBody || !emptyFormDiv || !totalFormsInput)
        return;
    gridTable.addEventListener("click", function (e) {
        const target = e.target;
        if (!(target instanceof Element))
            return;
        const cell = target.closest("td[data-row][data-col]");
        if (!cell)
            return;
        const row = cell.getAttribute("data-row") || "";
        const col = cell.getAttribute("data-col") || "";
        const color = defaultColorSelect.value;
        const colorCount = Array.from(formsetTableBody.querySelectorAll("tr")).filter(tr => {
            const colorInput = tr.querySelector('input[name$="-color"]');
            return colorInput && colorInput.value === color;
        }).length;
        if (colorCount >= 2) {
            alert("You can only add 2 dots of each color.");
            return;
        }
        const exists = Array.from(formsetTableBody.querySelectorAll("tr")).some(tr => {
            const rowInput = tr.querySelector('input[name$="-row"]');
            const colInput = tr.querySelector('input[name$="-col"]');
            return rowInput && colInput && rowInput.value === row && colInput.value === col;
        });
        if (exists)
            return;
        // Clone the empty form row
        let formIdx = parseInt(totalFormsInput.value, 10);
        let emptyRowHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, formIdx.toString());
        // Create a temporary element to manipulate the row
        let temp = document.createElement("table");
        temp.innerHTML = emptyRowHtml;
        let newRow = temp.querySelector("tr");
        if (!newRow)
            return;
        // Set the values for row, col, color
        let rowInput = newRow.querySelector('input[name$="-row"]');
        let colInput = newRow.querySelector('input[name$="-col"]');
        let colorInput = newRow.querySelector('input[name$="-color"]');
        if (rowInput)
            rowInput.value = row;
        if (colInput)
            colInput.value = col;
        if (colorInput)
            colorInput.value = color;
        // Append the new row to the formset table
        formsetTableBody.appendChild(newRow);
        // Update TOTAL_FORMS
        totalFormsInput.value = (formIdx + 1).toString();
        const dot = document.createElement('div');
        dot.className = 'dot';
        dot.style.background = color;
        dot.style.width = '20px';
        dot.style.height = '20px';
        dot.style.borderRadius = '50%';
        dot.style.margin = 'auto';
        dot.style.display = 'block';
        cell.appendChild(dot);
    });
});
//# sourceMappingURL=addDotsGrid.js.map