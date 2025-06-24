document.addEventListener('DOMContentLoaded', () => {
  const sendBtn = document.getElementById('send-btn');
  const input = document.getElementById('user-input');
  const messages = document.getElementById('messages');

  sendBtn.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) return;
    messages.innerHTML += `<div><strong>You:</strong> ${text}</div>`;
    input.value = '';
    try {
      const resp = await fetch('/ai_teacher/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await resp.json();
      if (data.error) {
        messages.innerHTML += `<div><em>Error: ${data.error}</em></div>`;
      } else {
        messages.innerHTML += `<div><strong>AI:</strong> ${data.reply}</div>`;
      }
    } catch (err) {
      messages.innerHTML += `<div><em>Fetch error: ${err.message}</em></div>`;
    }
    messages.scrollTop = messages.scrollHeight;
  });

  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendBtn.click();
    }
  });
});
