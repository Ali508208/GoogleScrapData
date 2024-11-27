$(document).ready(function () {
    $("#searchForm").on("submit", function (e) {
        e.preventDefault();
        // Show the progress modal
        $("#progressModal").modal("show");

        const formData = {
            industry: $("#industry").val(),
            country: $("#country").val(),
            city: $("#city").val(),
        };

        $.ajax({
            url: "/scrape",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function (response) {
                $("#loading").hide();
                const results = response.results;

                // Destroy existing DataTable if it exists
                if ($.fn.DataTable.isDataTable("#resultsTable")) {
                    $("#resultsTable").DataTable().clear().destroy();
                }

                if (results.length > 0) {
                    // Populate the table with results
                    const tableBody = $("#resultsTable tbody");
                    tableBody.empty();

                    results.forEach((result) => {
                        const row = `
                            <tr>
                                <td>${result.Name}</td>
                                <td>${result.Rating || "N/A"}</td>
                                <td>${result.Description || "N/A"}</td>
                                <td><a href="${result['Visited Link']}" target="_blank">${result['Visited Link'] || "N/A"}</a></td>
                                <td>
                                    <img src="${result.Image || 'https://media.istockphoto.com/id/1354776457/vector/default-image-icon-vector-missing-picture-page-for-website-design-or-mobile-app-no-photo.jpg?s=612x612&w=0&k=20&c=w3OW0wX3LyiFRuDHo9A32Q0IUMtD4yjXEvQlqyYk9O4='}" 
                                    style="width: 100px; height: 100px; object-fit: cover;" 
                                    alt="${result.Name}"
                                    onError="this.onerror=null;this.src='https://media.istockphoto.com/id/1354776457/vector/default-image-icon-vector-missing-picture-page-for-website-design-or-mobile-app-no-photo.jpg?s=612x612&w=0&k=20&c=w3OW0wX3LyiFRuDHo9A32Q0IUMtD4yjXEvQlqyYk9O4=';">
                                </td>
                            </tr>`;
                        tableBody.append(row);
                    });

                    // Initialize DataTable with buttons
                    $("#resultsTable").DataTable({
                        pageLength: 10,
                        lengthChange: true,
                        searching: true,
                        dom: "Bfrtip", // Enables buttons above the table
                        buttons: [
                            {
                                extend: "copy",
                                text: "Copy",
                                className: "btn btn-primary", // Bootstrap Primary Button
                            },
                            {
                                extend: "csv",
                                text: "Download CSV",
                                className: "btn btn-success", // Bootstrap Success Button
                            },
                            {
                                extend: "excel",
                                text: "Export Excel",
                                className: "btn btn-warning", // Bootstrap Warning Button
                            },
                            {
                                extend: "pdf",
                                text: "Save PDF",
                                className: "btn btn-danger", // Bootstrap Danger Button
                            },
                            {
                                extend: "print",
                                text: "Print",
                                className: "btn btn-info", // Bootstrap Info Button
                            },
                        ],
                    });
                    

                    // Show the table
                    $("#result-table-data").show();
                    $("#resultsTable").show();
                    $("#progressModal").modal("hide");
                } else {
                    alert("No results found.");
                    $("#progressModal").modal("hide");
                }
            },
            error: function () {
                $("#progressModal").modal("hide");
                alert("An error occurred while scraping data.");
            },
        });
    });
    
    document.addEventListener("DOMContentLoaded", function () {
        const stopScrapingBtn = document.getElementById("stopScrapingBtn");
    
        stopScrapingBtn.addEventListener("click", function () {
            fetch("/stop", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    $("#progressModal").modal("hide");
                    alert("Scraping process stopped!");
                })
                .catch((error) => {
                    console.error("Error stopping scraping:", error);
                });
        });
    });
    
    
});
