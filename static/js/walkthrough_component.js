
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("walkthrough-player");
  const steps = window.walkthroughSteps || [];
  let stepIndex = 0;
  let answers = [];

  function renderStep() {
    if (stepIndex >= steps.length) {
      submitAnswers();
      return;
    }

    const step = steps[stepIndex];
    container.innerHTML = `
      <div class="prose">
        <h2 class="text-xl font-semibold mb-4">Стъпка ${stepIndex + 1}</h2>
        <p>${step}</p>
        <textarea id="answer-input" rows="4" class="w-full border rounded-lg p-2 mt-4" placeholder="Твоят отговор..."></textarea>
        <div class="text-right mt-4">
          <button onclick="nextStep()" class="btn btn-primary">Продължи</button>
        </div>
      </div>
    `;
  }

  window.nextStep = () => {
    const input = document.getElementById("answer-input");
    const answer = input ? input.value.trim() : "";
    answers.push(answer);
    stepIndex += 1;
    renderStep();
  };

  function submitAnswers() {
    fetch("/walkthrough/ai-feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers })
    })
      .then(res => res.json())
      .then(data => {
        container.innerHTML = `
          <div class="prose">
            <h2 class="text-xl font-semibold text-green-700">🔍 Обратна връзка</h2>
            <pre class="bg-gray-100 p-4 rounded-md">${data.feedback}</pre>
          </div>
        `;
      })
      .catch(() => {
        container.innerHTML = "<p>⚠️ Грешка при изпращане на отговорите.</p>";
      });
  }

  renderStep();
});
