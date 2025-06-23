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
  const strengthMeter = document.getElementById("strength-meter");
  const passwordInputs = [
    document.getElementById("password"),
    document.getElementById("signup-password")
  ].filter(Boolean);

  passwordInputs.forEach(input => {
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

      if (strengthMeter) {
        strengthMeter.style.background = `linear-gradient(to right, #f5c054 ${strength}%, #333 ${strength}%)`;
        strengthMeter.setAttribute("aria-label", `Сигурност: ${label}`);
        strengthMeter.style.height = "6px"; // optional visual cue
        strengthMeter.title = `Сигурност: ${label}`;
      }
    });
  });
});
