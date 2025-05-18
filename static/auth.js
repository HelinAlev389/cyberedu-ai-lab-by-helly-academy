function togglePassword(id) {
  const input = document.getElementById(id);
  const icon = input?.nextElementSibling?.querySelector("i");

  if (!input || !icon) return;

  const isPassword = input.type === "password";
  input.type = isPassword ? "text" : "password";
  icon.classList.toggle("fa-eye", !isPassword);
  icon.classList.toggle("fa-eye-slash", isPassword);
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("password");
  const strengthMeter = document.getElementById("strength-meter");

  if (!input || !strengthMeter) return;

  input.addEventListener("input", () => {
    const val = input.value.trim();
    let strength = 0;
    let label = "Слаба";
    let color = "#D74042";

    if (val.length >= 8 && /[A-Z]/.test(val) && /\d/.test(val)) {
      strength = 100;
      label = "Силна";
      color = "#197C85";
    } else if (val.length >= 6) {
      strength = 60;
      label = "Средна";
      color = "#F57426";
    } else {
      strength = 20;
    }

    strengthMeter.style.background = `linear-gradient(to right, ${color} ${strength}%, #333 ${strength}%)`;
    strengthMeter.setAttribute("aria-label", `Сигурност: ${label}`);
    strengthMeter.title = `Сигурност: ${label}`;
  });
});
