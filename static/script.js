async function analyze() {
    const log = document.getElementById("logInput").value;

    try {
        const response = await fetch("/analyze-log", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({log})
        });

        const data = await response.json();
        document.getElementById("result").innerText = data.answer;

        // ⬇️ Автоматично изтегли резултата като .txt файл
        downloadResult(log, data.answer);
    } catch (error) {
        document.getElementById("result").innerText = "⚠️ Грешка при заявката към сървъра.";
        console.error("Грешка:", error);
    }
}

function loadFile() {
    const fileInput = document.getElementById('logFile');
    const reader = new FileReader();

    reader.onload = function () {
        document.getElementById('logInput').value = reader.result;
    };

    if (fileInput.files.length > 0) {
        reader.readAsText(fileInput.files[0]);
    }
}

function downloadResult(log, result) {
    const blob = new Blob([`Log:\n${log}\n\n---\nGPT Response:\n${result}`], {type: "text/plain"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ai-soc-analysis-result.txt";
    a.click();
    URL.revokeObjectURL(url);
}
