document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("lesson-player");
  let step = 0;

  function renderStep() {
    const current = lessonSteps[step];
    container.innerHTML = '';

    if (current.type === 'text') {
      container.innerHTML = `<div class="prose">${current.content}</div>`;
    } else if (current.type === 'image') {
      container.innerHTML = `<img src="${current.src}" class="rounded-xl w-full mx-auto" />`;
    } else if (current.type === 'video') {
      container.innerHTML = `<iframe class="w-full h-64" src="${current.src}" frameborder="0" allowfullscreen></iframe>`;
    } else if (current.type === 'question') {
      const questionHTML = `
        <p class="text-lg font-semibold mb-4">${current.question}</p>
        <div class="space-y-2">
          ${current.options.map(opt => `<button class="btn btn-outline w-full" onclick="nextStep()">${opt}</button>`).join('')}
        </div>
      `;
      container.innerHTML = questionHTML;
    }

    const nav = document.createElement('div');
    nav.className = "flex justify-between mt-6";
    nav.innerHTML = `
      <button onclick="prevStep()" class="btn btn-secondary">Назад</button>
      <button onclick="nextStep()" class="btn btn-primary">Продължи</button>
    `;
    container.appendChild(nav);
  }

  window.nextStep = () => {
    step = Math.min(lessonSteps.length - 1, step + 1);
    renderStep();
  };

  window.prevStep = () => {
    step = Math.max(0, step - 1);
    renderStep();
  };

  renderStep();
});
