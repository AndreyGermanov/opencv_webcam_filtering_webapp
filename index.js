document.addEventListener("DOMContentLoaded", () => {
    const img = document.querySelector("img");
    // Update video frame image each 30 milliseconds
    setInterval(()=> {
        img.src = "./frame.jpg?t="+(new Date()).getTime();
    },30);
    applyFilters();
})

/**
 * Sends enabled filters to backend
 * each time when user changes something
 * in UI
 */
function applyFilters() {
    const filters = getFilters();
    fetch("/filter", {
        method: "POST",
        body: JSON.stringify(filters),
        headers: {
            "Content-Type": "application/json",
        }
    })
}

/**
 * Collects enabled filters to JSON object where
 * keys are filter names and values are filter parameters
 * @returns JSON object
 */
function getFilters() {
    const result = {};
    if (document.getElementById("only_face").checked) {
        result["only_face"] = true;
    }
    let colors = "";
    if (document.getElementById("r").checked) {
        colors += "r";
    }
    if (document.getElementById("g").checked) {
        colors += "g";
    }
    if (document.getElementById("b").checked) {
        colors += "b";
    }
    result["colors"] = colors;
    if (document.getElementById("blur").checked) {
        result["blur"] = parseInt(document.getElementById("blur_value").value);
    }
    if (document.getElementById("binary").checked) {
        result["binary"] = parseInt(document.getElementById("binary_value").value);
    }
    if (document.getElementById("brightness").checked) {
        result["brightness"] = parseInt(document.getElementById("brightness_value").value);
    }
    if (document.getElementById("contrast").checked) {
        result["contrast"] = parseFloat(document.getElementById("contrast_value").value);
    }
    if (document.getElementById("edges").checked) {
        result["edges"] = true;
    }
    return result;
}
