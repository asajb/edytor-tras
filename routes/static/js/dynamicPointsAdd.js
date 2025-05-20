window.addEventListener("DOMContentLoaded", () => {
    const mapContainer = document.getElementById("map-container");
    if (!mapContainer) {
        console.error("Map container not found");
        return;
    }
    // Get formset elements
    const totalFormsInput = document.getElementById("id_form-TOTAL_FORMS");
    const formsetTableBody = document.getElementById("formset-table-body");
    const emptyFormDiv = document.getElementById("empty-form");
    // Create SVG overlay for markers
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.position = "absolute";
    svg.style.top = "0";
    svg.style.left = "0";
    svg.style.width = "100%";
    svg.style.height = "100%";
    svg.style.pointerEvents = "none";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    mapContainer.appendChild(svg);
    function getFormIdx() {
        return document.querySelectorAll("#formset-table-body tr").length;
    }
    function addMarker(x, y) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", x.toString());
        circle.setAttribute("cy", y.toString());
        circle.setAttribute("r", "5");
        circle.setAttribute("fill", "red");
        circle.setAttribute("stroke", "darkred");
        circle.setAttribute("stroke-width", "2");
        svg.appendChild(circle);
    }
    const mapImage = mapContainer.querySelector('img');
    if (mapImage) {
        mapImage.addEventListener("click", (event) => {
            var _a, _b;
            // Prevent event bubbling if needed
            console.log("Map image clicked at clientX:", event.clientX, "clientY:", event.clientY);
            // Get the image's rendered rectangle on the screen
            const imageRect = mapImage.getBoundingClientRect();
            // Get intrinsic dimensions of the image
            const imageWidth = mapImage.naturalWidth;
            const imageHeight = mapImage.naturalHeight;
            console.log("Image intrinsic dimensions:", imageWidth, imageHeight);
            console.log("Image rendered dimensions:", imageRect.width, imageRect.height);
            console.log("Image bounding rect:", imageRect);
            // Container dimensions (the full <img> element)
            const containerWidth = imageRect.width;
            const containerHeight = imageRect.height;
            // Calculate the scale factor and drawn (visible) dimensions
            const scale = Math.min(containerWidth / imageWidth, containerHeight / imageHeight);
            const drawnWidth = imageWidth * scale;
            const drawnHeight = imageHeight * scale;
            // Compute offsets (letterbox areas) inside the container
            const offsetX = (containerWidth - drawnWidth) / 2;
            const offsetY = (containerHeight - drawnHeight) / 2;
            // Calculate click position relative to the drawn image
            const clickX = event.clientX - imageRect.left - offsetX;
            const clickY = event.clientY - imageRect.top - offsetY;
            // Ignore clicks outside the visible image area
            if (clickX < 0 || clickY < 0 || clickX > drawnWidth || clickY > drawnHeight) {
                console.log("Click outside image bounds", clickX, clickY);
                return;
            }
            // Convert click positions to coordinates in intrinsic image space
            const x = Math.round((clickX / drawnWidth) * imageWidth);
            const y = Math.round((clickY / drawnHeight) * imageHeight);
            console.log("Computed image coordinates:", x, y);
            // Update SVG overlay with intrinsic image dimensions
            svg.setAttribute("viewBox", `0 0 ${imageWidth} ${imageHeight}`);
            // Create a new form row for the clicked point
            let formIdx = getFormIdx();
            if (emptyFormDiv && formsetTableBody) {
                let template = emptyFormDiv.innerHTML.trim();
                template = template.replace(/__prefix__/g, formIdx.toString());
                // Create a new row with cells
                const newRow = document.createElement('tr');
                const cell1 = document.createElement('td');
                const cell2 = document.createElement('td');
                // Create a temporary div to parse the template
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = template;
                // Split the content between two cells
                const xElements = (_a = tempDiv.querySelector('[name$="-x"]')) === null || _a === void 0 ? void 0 : _a.parentElement;
                const yElements = (_b = tempDiv.querySelector('[name$="-y"]')) === null || _b === void 0 ? void 0 : _b.parentElement;
                if (xElements)
                    cell1.appendChild(xElements);
                if (yElements)
                    cell2.appendChild(yElements);
                newRow.appendChild(cell1);
                newRow.appendChild(cell2);
                // Set the coordinate values
                const xInput = newRow.querySelector('input[name$="-x"]');
                const yInput = newRow.querySelector('input[name$="-y"]');
                if (xInput) {
                    xInput.value = x.toFixed(2);
                    console.log("X input value set to:", xInput.value);
                }
                if (yInput) {
                    yInput.value = y.toFixed(2);
                    console.log("Y input value set to:", yInput.value);
                }
                formsetTableBody.appendChild(newRow);
                formIdx = getFormIdx();
                totalFormsInput.value = formIdx.toString();
            }
            // Add a marker to the map at the computed coordinates
            addMarker(x, y);
        });
    }
    document.getElementById("add-point").addEventListener("click", function(e) {
        // Get the empty form template and replace __prefix__ with formIdx
        let formIdx = getFormIdx();
        var emptyTemplate = document.getElementById("empty-form").innerHTML;
        var newRowHtml = emptyTemplate.replace(/__prefix__/g, formIdx);
        // Append the new row to the table body
        var newRow = document.createElement("tr");
        newRow.innerHTML = newRowHtml;
        document.getElementById("formset-table-body").appendChild(newRow);
        // Increase form count
        formIdx = getFormIdx();
        totalFormsInput.value = formIdx;
      });
});
//# sourceMappingURL=dynamicPointsAdd.js.map